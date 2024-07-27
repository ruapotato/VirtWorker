import requests
from bs4 import BeautifulSoup
import feedparser
import os
import sys
import json
import time
import zmq

class Website:
    def __init__(self, url, use_rss=False, rss_feed_url=None):
        self.url = url
        self.use_rss = use_rss
        self.rss_feed_url = rss_feed_url
        self._text = None

    @property
    def text(self):
        if self._text is None:
            if self.use_rss:
                self._text = self._fetch_from_rss()
            else:
                self._text = self._fetch_from_url()
            print(f"Fetched {len(self._text)} characters from the website")
        return self._text

    def _fetch_from_url(self):
        print(f"Fetching content from: {self.url}")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()

    def _fetch_from_rss(self):
        print(f"Fetching content from RSS feed: {self.rss_feed_url}")
        feed = feedparser.parse(self.rss_feed_url)
        for entry in feed.entries:
            if entry.link == self.url:
                return entry.summary
        print(f"URL {self.url} not found in RSS feed. Falling back to direct URL fetch.")
        return self._fetch_from_url()

class Node:
    def __init__(self, model_name: str, name: str):
        self.model_name = model_name
        self.name = name
        self.definition = ""
        self.context = []
        self.max_context_length = 10  # Adjust this value as needed

    def __call__(self, input_text: str, max_tokens=8192):
        print(f"[{self.name}] Processing input:\n{input_text}")
        try:
            context_str = "\n".join([f"<|start_header_id|>{msg['role']}<|end_header_id|> {msg['content']}<|eot_id|>" for msg in self.context])
            
            prompt = f"""<|start_header_id|>system<|end_header_id|>{self.definition}<|eot_id|>
{context_str}
<|start_header_id|>user<|end_header_id|>{input_text}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>"""

            response = requests.post('http://localhost:11434/api/generate', 
                                     json={
                                         "model": self.model_name,
                                         "prompt": prompt,
                                         "stream": False,
                                         "options": {
                                             "stop": ["<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>"],
                                             "num_predict": max_tokens
                                         }
                                     })
            
            if response.status_code == 200:
                output = response.json()['response'].strip()
                self.context.append({"role": "user", "content": input_text})
                self.context.append({"role": "assistant", "content": output})
                print(f"[{self.name}] Output:\n{output}")
                return output
            else:
                error_message = f"Error in Ollama API call: {response.status_code} - {response.text}"
                print(error_message)
                return error_message
        except Exception as e:
            error_message = f"Error in processing: {str(e)}"
            print(error_message)
            return error_message

    def clear_context(self):
        self.context = []
        print(f"[{self.name}] Context cleared.")

def create_node(model_name: str, name: str, max_tokens=8192):
    print(f"Creating node '{name}' with model '{model_name}' and max_tokens {max_tokens}")
    node = Node(model_name, name)
    node.max_tokens = max_tokens
    return node

def generate_audio(text, filename):
    request_dir = './tts_requests'
    output_dir = './tts_output'
    os.makedirs(request_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    request_id = f"request_{int(time.time())}"
    request_file = os.path.join(request_dir, f"{request_id}.json")
    output_file = os.path.join(output_dir, filename)

    with open(request_file, 'w') as f:
        json.dump({
            "text": text,
            "output_filename": filename
        }, f)

    print(f"TTS request written to {request_file}")

    timeout = 300  # 5 minutes timeout
    start_time = time.time()
    while not os.path.exists(output_file):
        if time.time() - start_time > timeout:
            print("Timeout waiting for TTS output")
            return None
        time.sleep(1)

    print(f"TTS output received: {output_file}")
    return output_file

def check_ollama():
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            print("Ollama is running.")
            return True
        else:
            print("Ollama is not responding correctly.")
            return False
    except requests.ConnectionError:
        print("Ollama is not running. Please start Ollama with 'ollama serve'.")
        return False

# Check Ollama on import
if not check_ollama():
    sys.exit(1)
