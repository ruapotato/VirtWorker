import time
import os
import re
from typing import Dict
from virtworker import create_node  # Assume this function is available

def create_nodes() -> Dict[str, object]:
    print("Creating AI nodes for different writing tasks...")
    
    nodes = {}
    node_types = [
        'outline', 'character', 'world_building', 'act', 'chapter', 'scene',
        'dialogue', 'narrative_flow', 'theme', 'emotion', 'style', 'revision'
    ]
    
    for node_type in node_types:
        node_name = node_type.replace('_', ' ').title() + ' Generator'
        nodes[node_type] = create_node("llama3.1:8b", node_name, max_tokens=32768)
        print(f"Creating node '{node_name}' with model 'llama3.1:8b' and max_tokens 32768")

    for node_name, node in nodes.items():
        node.definition = get_node_definition(node_name)

    print("AI nodes created successfully.")
    return nodes

def get_node_definition(node_name: str) -> str:
    definitions = {
        'outline': "Generate a comprehensive story outline that includes main plot, themes, and character arcs. Provide only the outline, without any additional commentary or analysis.",
        'character': "Create detailed character arcs that show growth and change throughout the story. Focus solely on character development without any meta-commentary.",
        'world_building': "Develop comprehensive world-building that includes geography, culture, history, and societal structures. Provide only the world details without any additional analysis.",
        'act': "Create engaging act structures that advance the plot and develop characters. Focus on the story content without any commentary on the writing process.",
        'chapter': "Develop chapter content that hooks readers and advances the story. Provide only the chapter text without any suggestions for improvement.",
        'scene': "Create vivid and meaningful scenes that engage readers and move the story forward. Focus solely on the scene content without any meta-analysis.",
        'dialogue': "Write natural and engaging dialogue that enhances character interactions. Provide only the dialogue without any commentary on its effectiveness.",
        'narrative_flow': "Improve the overall narrative structure to ensure a smooth and engaging reading experience. Focus on the story flow without providing any editing suggestions.",
        'theme': "Enhance the thematic depth and symbolic richness of the story. Provide thematic elements without any additional analysis of their effectiveness.",
        'emotion': "Enhance the emotional resonance of scenes and character interactions. Focus on emotional content without commenting on the writing techniques used.",
        'style': "Ensure a cohesive writing style throughout the novel. Provide stylistic improvements without any meta-commentary on the writing process.",
        'revision': "Provide a revised version of the entire novel, focusing solely on improving the story without any additional commentary or suggestions."
    }
    return definitions.get(node_name, "You are an AI assistant specialized in writing tasks. Focus solely on generating story content without any meta-commentary or analysis.")

def print_ai_call(func):
    def wrapper(*args, **kwargs):
        node_name = args[0].__class__.__name__
        prompt = args[1]
        print(f"[{node_name}] Processing input:\n{prompt}")
        result = func(*args, **kwargs)
        print(f"[{node_name}] Output:\n{result}")
        return result
    return wrapper

def print_function_call(func):
    def wrapper(*args, **kwargs):
        print(f"Starting: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            print(f"Completed: {func.__name__}")
            return result
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

@print_function_call
def generate_story_outline(outline_node):
    prompt = "Create a detailed outline for a novel, including main plot, themes, and character arcs. Provide only the outline content, without any additional commentary or analysis."
    return outline_node(prompt)

@print_function_call
def generate_character_arc(character_node, outline, character_number):
    prompt = f"Based on this outline:\n\n{outline}\n\nCreate a detailed character arc for Character {character_number}. Focus solely on the character's development without any meta-commentary."
    return character_node(prompt)

@print_function_call
def generate_world(world_building_node, outline):
    prompt = f"Based on this outline:\n\n{outline}\n\nCreate a detailed world for the story to take place in. Provide only world-building details without any additional analysis."
    return world_building_node(prompt)

@print_function_call
def generate_act(act_node, outline, act_number):
    prompt = f"Based on this outline:\n\n{outline}\n\nWrite Act {act_number} of the story. Focus on the story content without any commentary on the writing process."
    return act_node(prompt)

@print_function_call
def generate_chapter(chapter_node, act, chapter_number):
    prompt = f"Based on this act:\n\n{act}\n\nWrite Chapter {chapter_number}. Provide only the chapter text without any suggestions for improvement."
    return chapter_node(prompt)

@print_function_call
def generate_scene(scene_node, chapter, scene_number):
    prompt = f"Based on this chapter:\n\n{chapter}\n\nWrite Scene {scene_number}. Focus solely on the scene content without any meta-analysis."
    return scene_node(prompt)

@print_function_call
def enhance_dialogue(dialogue_node, scene):
    prompt = f"Enhance the dialogue in the following scene:\n\n{scene}\nProvide only the improved dialogue without any commentary on its effectiveness."
    return dialogue_node(prompt)

@print_function_call
def manage_narrative_flow(narrative_flow_node, section):
    prompt = f"Improve the narrative flow of the following section:\n\n{section}\nFocus on the story flow without providing any editing suggestions."
    return narrative_flow_node(prompt)

@print_function_call
def enhance_themes_and_symbolism(theme_node, section):
    prompt = f"Enhance the themes and symbolism in the following section:\n\n{section}\nProvide thematic elements without any additional analysis of their effectiveness."
    return theme_node(prompt)

@print_function_call
def enhance_emotional_resonance(emotion_node, section):
    prompt = f"Enhance the emotional resonance of the following section:\n\n{section}\nFocus on emotional content without commenting on the writing techniques used."
    return emotion_node(prompt)

@print_function_call
def ensure_style_consistency(style_node, section):
    prompt = f"Ensure style consistency in the following section:\n\n{section}\nProvide stylistic improvements without any meta-commentary on the writing process."
    return style_node(prompt)

@print_function_call
def revise_story(revision_node, story):
    prompt = f"Revise and refine the following story. Provide a complete revised version, focusing solely on improving the story without any additional commentary or suggestions:\n\n{story}"
    return revision_node(prompt)

def save_intermediate(content, filename):
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Saved intermediate content to {filename}")

def remove_meta_commentary(text):
    # Remove sections that look like analysis or suggestions
    patterns = [
        r'\n*(?:Here (?:are|is)|The revised section|Overall,).*?(?=\n\n|\Z)',
        r'\n*\*\*.*?\*\*.*?(?=\n\n|\Z)',  # Remove bullet points
        r'\n*Note:.*?(?=\n\n|\Z)',  # Remove notes
        r'\n*I hope these suggestions are helpful!.*?(?=\n\n|\Z)',  # Remove closing statements
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    return text.strip()

def final_cleanup(text):
    # Remove any remaining meta-commentary or instructions
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith('*') and not line.strip().startswith('Note:')]
    return '\n'.join(cleaned_lines)

@print_function_call
def generate_book():
    nodes = create_nodes()
    
    try:
        print("Generating story outline...")
        outline = generate_story_outline(nodes['outline'])
        outline = remove_meta_commentary(outline)
        save_intermediate(outline, "outline.txt")
        
        print("Generating character arcs...")
        character_arcs = [generate_character_arc(nodes['character'], outline, i) for i in range(1, 6)]
        character_arcs = [remove_meta_commentary(arc) for arc in character_arcs]
        save_intermediate("\n\n".join(character_arcs), "character_arcs.txt")
        
        print("Generating world...")
        world = generate_world(nodes['world_building'], outline)
        world = remove_meta_commentary(world)
        save_intermediate(world, "world.txt")
        
        book_content = f"# Novel\n\n## World\n{world}\n\n## Characters\n"
        for arc in character_arcs:
            book_content += f"{arc}\n\n"
        
        for act_number in range(1, 4):
            print(f"Generating Act {act_number}...")
            act = generate_act(nodes['act'], outline, act_number)
            act = remove_meta_commentary(act)
            book_content += f"## Act {act_number}\n{act}\n\n"
            
            for chapter_number in range(1, 11):
                print(f"Generating Chapter {chapter_number} of Act {act_number}...")
                chapter = generate_chapter(nodes['chapter'], act, chapter_number)
                chapter = remove_meta_commentary(chapter)
                book_content += f"### Chapter {chapter_number}\n{chapter}\n\n"
                
                for scene_number in range(1, 6):
                    print(f"Generating Scene {scene_number} of Chapter {chapter_number}, Act {act_number}...")
                    scene = generate_scene(nodes['scene'], chapter, scene_number)
                    scene = remove_meta_commentary(scene)
                    enhanced_scene = enhance_dialogue(nodes['dialogue'], scene)
                    enhanced_scene = remove_meta_commentary(enhanced_scene)
                    enhanced_scene = manage_narrative_flow(nodes['narrative_flow'], enhanced_scene)
                    enhanced_scene = remove_meta_commentary(enhanced_scene)
                    enhanced_scene = enhance_themes_and_symbolism(nodes['theme'], enhanced_scene)
                    enhanced_scene = remove_meta_commentary(enhanced_scene)
                    enhanced_scene = enhance_emotional_resonance(nodes['emotion'], enhanced_scene)
                    enhanced_scene = remove_meta_commentary(enhanced_scene)
                    enhanced_scene = ensure_style_consistency(nodes['style'], enhanced_scene)
                    enhanced_scene = remove_meta_commentary(enhanced_scene)
                    book_content += f"{enhanced_scene}\n\n"
                
                save_intermediate(book_content, f"act_{act_number}_chapter_{chapter_number}.txt")
        
        print("Revising the entire story...")
        final_book = revise_story(nodes['revision'], book_content)
        final_book = remove_meta_commentary(final_book)
        final_book = final_cleanup(final_book)
        
        return final_book
    
    except Exception as e:
        print(f"Error in book generation: {str(e)}")
        return None

if __name__ == "__main__":
    book = generate_book()
    if book:
        filename = f"generated_novel_{int(time.time())}.txt"
        with open(filename, "w") as f:
            f.write(book)
        print(f"Book generation complete. The book has been saved as '{filename}'.")
    else:
        print("Book generation failed.")

    # Clean up intermediate files
    for file in os.listdir():
        if file.endswith(".txt") and file != filename:
            os.remove(file)
            print(f"Removed intermediate file: {file}")
