import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gdk, GLib, Notify
import subprocess
import json
import os
import threading
import re
import shutil
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIDesktopAssistant:
    def __init__(self, model_name: str = "llama3.1:8b", max_tokens: int = 16384):
        from virtworker import create_node
        self.assistant = create_node(model_name, "Desktop Assistant", max_tokens=max_tokens)
        self.assistant.definition = """
        You are an AI desktop assistant. Your task is to help users interact with their desktop environment,
        applications, and content. Provide concise, actionable responses to user queries. Your capabilities include:
        1. Analyzing and summarizing text
        2. Providing guidance on using applications and finding menu options
        3. Suggesting ways to manage windows and workspaces
        4. Offering productivity tips and shortcuts
        5. Assisting with basic image description (when provided)
        6. Helping with time management and scheduling

        You can execute certain commands directly. Use the following tags in your responses:
        <open>application_name</open> - Opens the specified application
        <click>x,y</click> - Simulates a mouse click at the specified coordinates
        <move_window>window_name x y</move_window> - Moves the specified window to the given coordinates
        <type>text</type> - Types the specified text
        <key>key_name</key> - Presses the specified key (e.g., <key>enter</key>)

        Important: 
        - Use command tags for all actions that can be executed directly.
        - For multi-step commands, use separate command tags for each step.
        - When opening a terminal and running a command, use the following sequence:
          <open>terminal</open>
          <wait_for>terminal_window</wait_for>
          <type>command_here</type>
          <key>enter</key>
        - Be concise in your responses. Avoid unnecessary explanations unless the user asks for more details.
        - When notified of window changes, respond with "noted" unless action is required based on previous commands.
        """
        self.context = []
        self.pending_actions = []

    def process_query(self, user_input: str, selected_text: str, active_window: str, clipboard_content: str) -> str:
        try:
            # Update context
            self.context.append(f"User Input: {user_input}")
            self.context.append(f"Selected Text: {selected_text}")
            self.context.append(f"Active Window: {active_window}")
            self.context.append(f"Clipboard Content: {clipboard_content}")
            
            # Keep only the last 5 context items
            self.context = self.context[-5:]
            
            prompt = f"""
            User Request: {user_input}

            Context:
            {self.context}
            
            Provide a helpful and concise response based on the user's input and context. Use command tags for all actions.
            For multi-step commands, use separate command tags for each step, including <wait_for> tags when necessary.
            """
            
            result = self.assistant(prompt)
            logging.info(f"AI Response: {result}")
            
            # Extract pending actions
            self.pending_actions = re.findall(r'<(\w+)>(.*?)</\1>', result)
            
            return result
        except Exception as e:
            logging.error(f"Error in process_query: {str(e)}")
            return f"Error: {str(e)}"

    def process_window_change(self, window_name: str) -> str:
        try:
            if not self.pending_actions:
                return "noted"
            
            action, content = self.pending_actions[0]
            if action == 'wait_for' and content.lower() in window_name.lower():
                self.pending_actions.pop(0)
                if self.pending_actions:
                    next_action, next_content = self.pending_actions[0]
                    return f"<{next_action}>{next_content}</{next_action}>"
            
            return "noted"
        except Exception as e:
            logging.error(f"Error in process_window_change: {str(e)}")
            return f"Error: {str(e)}"

class AIDesktopAssistantGTK(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="AI Desktop Assistant")
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_accept_focus(True)
        
        self.assistant = AIDesktopAssistant()
        
        # Initialize notification
        Notify.init("AI Desktop Assistant")
        
        # Load custom buttons
        self.custom_buttons = self.load_custom_buttons()
        
        self.create_widgets()
        self.connect_signals()
        self.position_window()
        
        # Start clipboard monitoring
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.primary = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        self.clipboard_content = ""
        self.primary_content = ""
        self.active_window = ""
        GLib.timeout_add(1000, self.check_context_changes)

    def create_widgets(self):
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.main_box)
        
        # Create horizontal box for input bar
        self.input_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.main_box.pack_start(self.input_bar, False, False, 0)
        
        self.entry = Gtk.Entry()
        self.entry.set_size_request(300, 30)
        self.input_bar.pack_start(self.entry, True, True, 0)
        
        # Add custom buttons
        self.custom_button_widgets = {}
        for button_name, button_prompt in self.custom_buttons.items():
            button = Gtk.Button(label=button_name)
            button.connect("clicked", self.on_custom_button_clicked, button_prompt)
            self.input_bar.pack_start(button, False, False, 0)
            self.custom_button_widgets[button_name] = button
        
        self.ask_button = Gtk.Button(label="Ask")
        self.input_bar.pack_start(self.ask_button, False, False, 0)
        
        self.stop_button = Gtk.Button(label="Stop")
        self.input_bar.pack_start(self.stop_button, False, False, 0)
        
        self.clear_button = Gtk.Button(label="Clear")
        self.input_bar.pack_start(self.clear_button, False, False, 0)
        
        self.copy_button = Gtk.Button(label="Copy")
        self.input_bar.pack_start(self.copy_button, False, False, 0)
        
        self.settings_button = Gtk.Button(label="Settings")
        self.input_bar.pack_start(self.settings_button, False, False, 0)
        
        # Create text view for output
        self.result_view = Gtk.TextView()
        self.result_view.set_editable(False)
        self.result_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.result_buffer = self.result_view.get_buffer()
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.result_view)
        scrolled_window.set_size_request(400, 200)
        
        self.main_box.pack_start(scrolled_window, True, True, 0)

    def connect_signals(self):
        self.connect("delete-event", Gtk.main_quit)
        self.ask_button.connect("clicked", self.on_button_clicked)
        self.entry.connect("activate", self.on_button_clicked)
        self.stop_button.connect("clicked", self.on_stop_clicked)
        self.clear_button.connect("clicked", self.on_clear_clicked)
        self.copy_button.connect("clicked", self.on_copy_clicked)
        self.settings_button.connect("clicked", self.on_settings_clicked)

    def position_window(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        scale_factor = monitor.get_scale_factor()
        width = scale_factor * geometry.width
        height = scale_factor * geometry.height
        
        window_width, window_height = self.get_size()
        x = (width - window_width) // 2
        y = height - window_height - 50  # 50 pixels from the bottom
        
        self.move(x, y)

    def on_button_clicked(self, widget):
        user_input = self.entry.get_text()
        if not user_input.strip():
            self.show_result("Please enter a query.")
            return
        
        selected_text = self.get_selected_text()
        active_window = self.get_active_window_title()
        
        threading.Thread(target=self.process_input, args=(user_input, selected_text, active_window, self.clipboard_content)).start()

    def on_stop_clicked(self, widget):
        subprocess.run(["killall", "espeak"])

    def on_clear_clicked(self, widget):
        self.result_buffer.set_text("")
        self.entry.set_text("")

    def on_copy_clicked(self, widget):
        start_iter = self.result_buffer.get_start_iter()
        end_iter = self.result_buffer.get_end_iter()
        text = self.result_buffer.get_text(start_iter, end_iter, True)
        self.clipboard.set_text(text, -1)

    def on_settings_clicked(self, widget):
        dialog = SettingsDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.custom_buttons = dialog.get_custom_buttons()
            self.save_custom_buttons()
            self.recreate_custom_buttons()
        dialog.destroy()

    def on_custom_button_clicked(self, widget, prompt):
        self.entry.set_text(prompt)
        self.on_button_clicked(widget)

    def process_input(self, user_input, selected_text, active_window, clipboard_content):
        result = self.assistant.process_query(user_input, selected_text, active_window, clipboard_content)
        processed_result = self.process_commands(result)
        GLib.idle_add(self.show_result, processed_result)
        self.speak_result(processed_result)
        self.send_notification(processed_result)

    def process_commands(self, text):
        def execute_open(app):
            try:
                if app.lower() == 'firefox':
                    subprocess.Popen(["firefox", "--new-window"])
                elif app.lower() == 'terminal':
                    terminal_emulators = ['gnome-terminal', 'xterm', 'konsole', 'terminator']
                    for emulator in terminal_emulators:
                        if shutil.which(emulator):
                            subprocess.Popen([emulator])
                            return f"Executed: Opened {emulator}"
                    return "Error: No suitable terminal emulator found"
                else:
                    subprocess.Popen(["xdg-open", app])
                return f"Executed: Opened {app}"
            except Exception as e:
                logging.error(f"Error opening {app}: {str(e)}")
                return f"Error opening {app}: {str(e)}"

        def execute_click(coords):
            try:
                x, y = map(int, coords.split(','))
                subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"])
                return f"Executed: Clicked at ({x}, {y})"
            except Exception as e:
                logging.error(f"Error clicking at {coords}: {str(e)}")
                return f"Error clicking at {coords}: {str(e)}"

        def execute_move_window(params):
            try:
                window, x, y = params.split()
                subprocess.run(["xdotool", "search", "--name", window, "windowmove", x, y])
                return f"Executed: Moved window '{window}' to ({x}, {y})"
            except Exception as e:
                logging.error(f"Error moving window {params}: {str(e)}")
                return f"Error moving window: {str(e)}"

        def execute_type(text):
            try:
                time.sleep(.5)
                subprocess.run(["xdotool", "type", text])
                return f"Executed: Typed '{text}'"
            except Exception as e:
                logging.error(f"Error typing text: {str(e)}")
                return f"Error typing text: {str(e)}"

        def execute_key(key):
            try:
                if key.lower() == 'enter':
                    key = 'Return'
                subprocess.run(["xdotool", "key", key])
                return f"Executed: Pressed key '{key}'"
            except Exception as e:
                logging.error(f"Error pressing key {key}: {str(e)}")
                return f"Error pressing key {key}: {str(e)}"

        def execute_wait_for(window):
            return f"Waiting for {window}"

        commands = {
            'open': execute_open,
            'click': execute_click,
            'move_window': execute_move_window,
            'type': execute_type,
            'key': execute_key,
            'wait_for': execute_wait_for
        }

        def replace_command(match):
            command = match.group(1)
            content = match.group(2)
            if command in commands:
                return commands[command](content)
            return match.group(0)

        pattern = r'<(\w+)>(.*?)</\1>'
        processed_text = re.sub(pattern, replace_command, text)
        
        # Remove any remaining command tags
        processed_text = re.sub(r'<\w+>.*?</\w+>', '', processed_text)
        
        return processed_text.strip()

    def show_result(self, result):
        self.result_buffer.set_text(result)
        return False

    def check_context_changes(self):
        clipboard_text = self.clipboard.wait_for_text()
        primary_text = self.primary.wait_for_text()
        active_window = self.get_active_window_title()
        
        if clipboard_text and clipboard_text != self.clipboard_content:
            self.clipboard_content = clipboard_text
        
        if primary_text and primary_text != self.primary_content:
            self.primary_content = primary_text
        
        if active_window != self.active_window:
            self.active_window = active_window
            self.handle_window_change(active_window)
        
        return True

    def handle_window_change(self, window_name):
        result = self.assistant.process_window_change(window_name)
        if result.lower() != "noted":
            processed_result = self.process_commands(result)
            GLib.idle_add(self.show_result, processed_result)
            self.speak_result(processed_result)
            self.send_notification(processed_result)

    def speak_result(self, text):
        subprocess.Popen(['espeak', text])

    def send_notification(self, text):
        notification = Notify.Notification.new("AI Assistant Reply", text)
        notification.show()

    def get_selected_text(self):
        return self.primary_content

    def get_active_window_title(self):
        try:
            return subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname']).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return "Unknown"

    def load_custom_buttons(self):
        if os.path.exists('custom_buttons.json'):
            with open('custom_buttons.json', 'r') as f:
                return json.load(f)
        return {}

    def save_custom_buttons(self):
        with open('custom_buttons.json', 'w') as f:
            json.dump(self.custom_buttons, f)

    def recreate_custom_buttons(self):
        # Remove existing custom buttons
        for button in self.custom_button_widgets.values():
            self.input_bar.remove(button)
        self.custom_button_widgets.clear()
        
        # Add new custom buttons
        for button_name, button_prompt in self.custom_buttons.items():
            button = Gtk.Button(label=button_name)
            button.connect("clicked", self.on_custom_button_clicked, button_prompt)
            self.input_bar.pack_start(button, False, False, 0)
            self.custom_button_widgets[button_name] = button
            button.show()

        # Reorder widgets to ensure standard buttons are at the end
        self.input_bar.reorder_child(self.ask_button, -1)
        self.input_bar.reorder_child(self.stop_button, -1)
        self.input_bar.reorder_child(self.clear_button, -1)
        self.input_bar.reorder_child(self.copy_button, -1)
        self.input_bar.reorder_child(self.settings_button, -1)

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Settings", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(350, 300)

        box = self.get_content_area()
        
        self.custom_buttons = parent.custom_buttons.copy()
        
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.listbox)
        box.pack_start(scrolled_window, True, True, 0)
        
        for button_name, button_prompt in self.custom_buttons.items():
            self.add_button_row(button_name, button_prompt)
        
        add_button = Gtk.Button(label="Add Custom Button")
        add_button.connect("clicked", self.on_add_button_clicked)
        box.pack_start(add_button, False, False, 0)
        
        self.show_all()

    def add_button_row(self, name, prompt):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.add(hbox)
        
        name_entry = Gtk.Entry()
        name_entry.set_text(name)
        name_entry.connect("changed", self.on_entry_changed, row)
        hbox.pack_start(name_entry, True, True, 0)
        
        prompt_entry = Gtk.Entry()
        prompt_entry.set_text(prompt)
        prompt_entry.connect("changed", self.on_entry_changed, row)
        hbox.pack_start(prompt_entry, True, True, 0)
        
        delete_button = Gtk.Button(label="Delete")
        delete_button.connect("clicked", self.on_delete_clicked, row)
        hbox.pack_start(delete_button, False, False, 0)
        
        self.listbox.add(row)
        row.show_all()

    def on_add_button_clicked(self, widget):
        name = f"New Button {len(self.custom_buttons) + 1}"
        prompt = "Custom prompt"
        self.add_button_row(name, prompt)
        self.update_custom_buttons()

    def on_delete_clicked(self, widget, row):
        self.listbox.remove(row)
        self.update_custom_buttons()

    def on_entry_changed(self, widget, row):
        self.update_custom_buttons()

    def update_custom_buttons(self):
        self.custom_buttons.clear()
        for row in self.listbox.get_children():
            name, prompt = self.get_row_data(row)
            if name and prompt:  # Ensure both name and prompt are non-empty
                self.custom_buttons[name] = prompt

    def get_row_data(self, row):
        hbox = row.get_child()
        name_entry, prompt_entry = hbox.get_children()[:2]
        return name_entry.get_text(), prompt_entry.get_text()

    def get_custom_buttons(self):
        return self.custom_buttons

def main():
    win = AIDesktopAssistantGTK()
    win.show_all()
    win.entry.grab_focus()
    Gtk.main()

if __name__ == "__main__":
    main()
