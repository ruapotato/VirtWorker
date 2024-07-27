import logging
import random
import json
import re
import time
from virtworker import create_node

# Set logging level to INFO to see all output
logging.getLogger().setLevel(logging.INFO)

# Create nodes
topic_generator = create_node("llama3.1:8b", "Topic Generator")
character_generator = create_node("llama3.1:8b", "Character Generator", max_tokens=16384)
story_arc_generator = create_node("llama3.1:8b", "Story Arc Generator", max_tokens=16384)
chapter_writer = create_node("llama3.1:8b", "Chapter Writer", max_tokens=16384)
editor = create_node("llama3.1:8b", "Editor", max_tokens=16384)
publisher = create_node("llama3.1:8b", "Publisher", max_tokens=16384)
narrative_reviewer = create_node("llama3.1:8b", "Narrative Reviewer", max_tokens=16384)
json_master = create_node("llama3.1:8b", "JSON Master", max_tokens=16384)

# Node definitions
topic_generator.definition = """You are an expert in generating unique and engaging topics for novels. When prompted, create a topic that includes:

1. Genre (can be a combination of genres)
2. Setting (time and place, with detailed world-building elements)
3. Main theme or central conflict
4. At least five key elements or motifs
5. Potential subplots or secondary conflicts

Respond using ONLY the following JSON format:

{
  "genre": "Main genre (and subgenres if applicable)",
  "setting": "Detailed description of time and place",
  "theme": "Central theme or conflict",
  "elements": [
    "Element 1",
    "Element 2",
    "Element 3",
    "Element 4",
    "Element 5"
  ],
  "subplots": [
    "Subplot 1",
    "Subplot 2",
    "Subplot 3"
  ]
}

Be creative and avoid clichés. Think outside the box to create truly unique and intriguing topics with rich world-building potential. Do not include any additional text or explanations outside of this JSON structure."""

character_generator.definition = """You are an expert character creator for novels. Your task is to generate unique, complex characters that fit seamlessly into the given topic. When prompted, create a character with the following details:

1. Full name (including any relevant nicknames)
2. Age
3. Occupation
4. Five key personality traits
5. Detailed background (at least 5 sentences, including formative experiences, relationships, and motivations)
6. Physical description
7. Special skills or abilities
8. Internal conflicts or personal struggles
9. Goals and aspirations
10. Relationships with other characters (if applicable)
11. Potential for character growth and development

Respond using ONLY the following JSON format:

{
  "name": "Character's full name",
  "age": 30,
  "occupation": "Character's occupation",
  "traits": [
    "Trait 1",
    "Trait 2",
    "Trait 3",
    "Trait 4",
    "Trait 5"
  ],
  "background": "Detailed character background.",
  "physical_description": "Character's physical appearance",
  "skills": ["Skill 1", "Skill 2", "Skill 3"],
  "conflicts": "Character's internal conflicts or struggles",
  "goals": "Character's goals and aspirations",
  "relationships": "Character's relationships with others",
  "growth_potential": "Potential areas for character development"
}

Ensure your character is deeply rooted in the provided topic and genre. Be creative and avoid stereotypes. Do not include any explanations or additional text outside of this JSON structure."""

story_arc_generator.definition = """You are a master storyteller specializing in crafting compelling narratives. Your task is to create an intricate story arc for a novel based on the given topic and characters. Craft a narrative that explores the main theme and incorporates the key elements.

Create a story arc with the following elements:
1. Detailed setting description
2. Inciting incident
3. Rising action (at least 15 key events)
4. Climax
5. Falling action
6. Resolution
7. At least 3 subplots that interweave with the main plot
8. Character development milestones for each major character
9. Worldbuilding elements to be explored in each section

For each story element, subplot, and character development milestone, specify which characters are involved and their roles. Respond using ONLY the following JSON format:

{
  "setting": {
    "description": "Detailed setting description",
    "characters_involved": ["Character 1", "Character 2"],
    "worldbuilding_elements": ["Element 1", "Element 2"]
  },
  "inciting_incident": {
    "description": "Description of the incident",
    "characters_involved": ["Character 1", "Character 2"],
    "worldbuilding_elements": ["Element 3"]
  },
  "rising_action": [
    {
      "description": "Event 1 description",
      "characters_involved": ["Character 1", "Character 3"],
      "worldbuilding_elements": ["Element 4"],
      "subplot_development": "Subplot 1 progress",
      "character_development": {
        "Character 1": "Development milestone",
        "Character 3": "Development milestone"
      }
    }
  ],
  "climax": {
    "description": "Description of the climax",
    "characters_involved": ["Character 1", "Character 2", "Character 3"],
    "worldbuilding_elements": ["Element 5"],
    "character_development": {
      "Character 1": "Major development milestone",
      "Character 2": "Major development milestone",
      "Character 3": "Major development milestone"
    }
  },
  "falling_action": {
    "description": "Description of falling action",
    "characters_involved": ["Character 1", "Character 2"],
    "worldbuilding_elements": ["Element 6"],
    "subplot_resolution": ["Subplot 1 resolution", "Subplot 2 resolution"]
  },
  "resolution": {
    "description": "Description of the resolution",
    "characters_involved": ["Character 1", "Character 2", "Character 3"],
    "worldbuilding_elements": ["Element 7"],
    "character_final_state": {
      "Character 1": "Final character state",
      "Character 2": "Final character state",
      "Character 3": "Final character state"
    }
  },
  "subplots": [
    {
      "description": "Subplot 1 description",
      "characters_involved": ["Character 2", "Character 4"],
      "events": [
        "Subplot event 1",
        "Subplot event 2",
        "Subplot event 3"
      ],
      "resolution": "Subplot resolution"
    }
  ]
}

Ensure that your story arc is rich with elements from the given topic and genre, exploring the main theme and incorporating the key elements. Do not include any explanations or additional text outside of this JSON structure."""

chapter_writer.definition = """You are a talented novelist with a knack for vivid, immersive storytelling. Your task is to write a compelling chapter for a novel based on the given topic, characters, story arc, and specific guidance for this chapter. Given a specific event from the story arc and relevant character information, craft a chapter of approximately 4000-5000 words.

Focus on:
1. Vivid and detailed descriptions of settings and atmosphere
2. In-depth character development through actions, dialogue, and internal monologue
3. Engaging dialogue that reflects each character's unique voice and background
4. Integration of the main theme and key elements from the topic
5. Advancing the plot while maintaining tension and reader engagement
6. Incorporating subplots and their development
7. Adding reflective or introspective passages to deepen character understanding
8. Balancing action, dialogue, and description to create a well-paced narrative
9. Exploring worldbuilding elements specific to this chapter
10. Showing character growth and development as outlined in the story arc
11. Maintaining genre conventions and thematic consistency

Start the chapter with "Chapter X: Title" where X is the chapter number and Title is a fitting, evocative title for the chapter. Immerse the reader in the world you're creating, making the theme and elements palpable through your prose.

Do not include any author notes, suggestions, editorial comments, or explanations about your writing process in your output. Focus solely on writing the narrative content of the chapter."""

editor.definition = """You are an experienced editor specializing in various genres of fiction. Your task is to review and provide constructive feedback on a chapter from a novel. Analyze the chapter for the following aspects:

1. Overall flow and pacing
2. Character consistency and development
3. Dialogue authenticity and effectiveness
4. Vividness and depth of descriptions, especially of settings and atmosphere
5. Grammar and style
6. Integration of the main theme and key elements from the topic
7. Worldbuilding and internal consistency
8. Development of subplots and their integration with the main plot
9. Balance of action, dialogue, and introspective passages
10. Length and completeness of the narrative (aiming for 4000-5000 words)
11. Adherence to genre conventions
12. Thematic consistency
13. Character growth and development as outlined in the story arc
14. Integration of specific worldbuilding elements assigned to this chapter

If the chapter needs improvement, provide specific, actionable suggestions. If the chapter meets high standards, approve it by starting your response with "APPROVED:" followed by a brief summary of the chapter's strengths.

Your feedback should help elevate the writing, ensuring it captures the essence of the given topic and genre while maintaining reader engagement and contributing to the overall narrative arc.

Provide your feedback in a clear, structured format. Do not rewrite the chapter or include narrative content in your response."""

publisher.definition = """You are an expert book publisher responsible for formatting approved chapters for publication. Your tasks include:

1. Ensure the chapter starts with the correct chapter number and title format: "Chapter X: Title"
2. If no title is present, add a suitable title based on the chapter content
3. Check that paragraphs are properly separated with blank lines
4. Verify that dialogue is correctly formatted with quotation marks and new lines for each speaker
5. Remove any remaining metadata, comments, or structural elements not part of the narrative
6. Maintain consistent formatting throughout the chapter

Your primary role is to format and clean the text, NOT to add or modify content. Follow these strict rules:
- Do not remove or change the chapter number and title
- Do not add any new content to the chapter
- Do not expand or elaborate on existing content
- Do not add descriptions, explanations, or commentary
- Focus solely on formatting and cleaning the existing text

If the chapter already meets the formatting criteria and no changes are needed, return the chapter exactly as it was provided.

Your output should be the formatted chapter text only, without any additional comments or explanations."""

narrative_reviewer.definition = """You are an expert in narrative structure and cohesion. Your task is to review the overall structure of a novel in progress and provide feedback on narrative flow, character development, subplot integration, and thematic consistency. Analyze the following aspects:

1. Overall narrative arc and pacing
2. Character development trajectories
3. Subplot integration and resolution
4. Thematic consistency and exploration
5. Worldbuilding depth and consistency
6. Genre adherence
7. Narrative tension and reader engagement

Provide specific feedback on areas that need improvement, such as:
- Chapters that may need reordering for better flow
- Character arcs that need more attention or development
- Subplots that require better integration or resolution
- Themes that need more consistent exploration
- Worldbuilding elements that should be expanded or clarified
- Genre expectations that are not being met
- Pacing issues that affect reader engagement

Your feedback should be actionable and specific, pointing out exact areas in the narrative that need attention. Provide suggestions for improvements that will enhance the overall coherence and quality of the novel.

Respond with a JSON object containing your analysis and recommendations. Use the following structure:

{
  "overall_assessment": "Brief overall assessment of the narrative",
  "narrative_arc": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "character_development": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "subplot_integration": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "thematic_consistency": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "worldbuilding": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "genre_adherence": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "pacing_and_engagement": {
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "specific_chapter_feedback": [
    {
      "chapter_number": 1,
      "issues": ["Issue 1", "Issue 2"],
      "recommendations": ["Recommendation 1", "Recommendation 2"]
    }
  ]
}

Do not include any explanations or additional text outside of this JSON structure."""

json_master.definition = """You are an expert in JSON formatting and error correction. Your task is to take potentially invalid JSON data and ensure it becomes valid. When given JSON data:

1. If the JSON is valid, return it as-is.
2. If the JSON is invalid, identify and correct the issues.
3. If given error messages about the JSON, use that information to guide your corrections.

Always respond with valid JSON. Do not include any explanations or additional text outside of the JSON structure."""

def validate_and_correct_json(json_string, original_node):
    json_master.clear_context()
    
    for attempt in range(5):  # Try up to 5 times
        try:
            # Remove any escaped characters
            json_string = json_string.encode().decode('unicode_escape')
            
            # Fix common JSON issues
            json_string = re.sub(r'"\s*:\s*"([^"]*)"([^,\}])', r'": "\1"\2,', json_string)  # Add missing commas
            json_string = re.sub(r',\s*}', '}', json_string)  # Remove trailing commas
            json_string = re.sub(r',\s*]', ']', json_string)  # Remove trailing commas in arrays
            
            # First, try to parse the JSON as-is
            json_data = json.loads(json_string)
            logging.info(f"JSON successfully parsed on attempt {attempt + 1}")
            return json_data  # If successful, return the parsed JSON
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON. Attempt {attempt + 1} to correct. Error: {str(e)}")
            
            # If parsing fails, ask json_master to correct it
            correction_prompt = f"""The following JSON is invalid. Please correct it:

{json_string[:1000]}  # Only send the first 1000 characters to avoid token limits

Error message: {str(e)}

Provide only the corrected JSON in your response."""

            corrected_json_string = json_master(correction_prompt)
            logging.info(f"Corrected JSON (first 500 chars): {corrected_json_string[:500]}...")
            
            json_string = corrected_json_string  # Use the corrected JSON for the next attempt
    
    logging.error("Failed to generate valid JSON after 5 attempts.")
    return None

def generate_topic():
    for attempt in range(3):  # Try up to 3 times
        topic_generator.clear_context()
        topic_json = topic_generator("Generate a unique and engaging topic for a novel. Be creative and think outside the box. Ensure the topic has rich potential for worldbuilding and character development.")
        topic = validate_and_correct_json(topic_json, topic_generator)
        if topic and isinstance(topic, dict) and len(topic) > 0:
            logging.info(f"Generated topic: {topic.get('genre', 'Unknown genre')} set in {topic.get('setting', 'Unknown setting')}")
            return topic
        logging.warning(f"Failed to generate a valid topic. Attempt {attempt + 1}")
    logging.error("Failed to generate a valid topic after 3 attempts.")
    return None

def generate_characters(num_characters, topic):
    characters = []
    attempts = 0
    max_attempts = num_characters * 5  # Allow more attempts than the number of characters we need

    while len(characters) < num_characters and attempts < max_attempts:
        attempts += 1
        character_generator.clear_context()
        prompt = f"""Generate a unique character for our novel with the following topic:
        Genre: {topic['genre']}
        Setting: {topic['setting']}
        Theme: {topic['theme']}
        Elements: {', '.join(topic['elements'])}
        Subplots: {', '.join(topic['subplots'])}
        
        Ensure the character has a UNIQUE NAME different from any previously generated characters.
        The character should have potential for growth and development throughout the story.
        Respond ONLY with a valid JSON object containing at least the following fields: name, age, occupation, traits."""
        
        character_json = character_generator(prompt)
        character = validate_and_correct_json(character_json, character_generator)
        
        if character and isinstance(character, dict):
            required_fields = ["name", "age", "occupation", "traits", "background", "physical_description", "skills", "conflicts", "goals", "relationships", "growth_potential"]
            
            # Fill in missing fields with placeholder data
            for field in required_fields:
                if field not in character:
                    character[field] = f"[{field.replace('_', ' ').title()}]"
            
            if isinstance(character.get('traits'), list) and len(character['traits']) > 0:
                if character['name'] not in [c['name'] for c in characters]:  # Ensure unique names
                    characters.append(character)
                    logging.info(f"Generated character: {character['name']}")
                else:
                    logging.warning(f"Duplicate character name: {character['name']}. Retrying.")
            else:
                logging.warning(f"Invalid traits for character. Retrying.")
        else:
            logging.error(f"Failed to generate valid character. Attempt {attempts}")

    if len(characters) < num_characters:
        logging.warning(f"Only generated {len(characters)} out of {num_characters} characters after {attempts} attempts.")

    return characters

def generate_story_arc(topic, characters):
    story_arc_generator.clear_context()
    character_names = [char["name"] for char in characters]
    prompt = f"""Generate a complex, engaging story arc for our novel with the following details:
    Genre: {topic['genre']}
    Setting: {topic['setting']}
    Theme: {topic['theme']}
    Elements: {', '.join(topic['elements'])}
    Subplots: {', '.join(topic['subplots'])}
    Characters: {', '.join(character_names)}
    
    Ensure the story arc includes character development milestones and worldbuilding elements to explore.
    Respond with a valid JSON object containing the required structure."""
    
    story_arc_json = story_arc_generator(prompt)
    logging.info(f"Raw story arc JSON: {story_arc_json[:500]}...")  # Log the first 500 characters of the raw JSON
    
    story_arc = validate_and_correct_json(story_arc_json, story_arc_generator)
    
    required_keys = ["setting", "inciting_incident", "rising_action", "climax", "falling_action", "resolution", "subplots"]
    
    if story_arc and isinstance(story_arc, dict):
        # Fill in missing keys with default content
        for key in required_keys:
            if key not in story_arc:
                story_arc[key] = {"description": f"[{key.replace('_', ' ').title()}]", "characters_involved": character_names[:2]}
        
        if "rising_action" in story_arc and not isinstance(story_arc["rising_action"], list):
            story_arc["rising_action"] = [story_arc["rising_action"]]
        
        if "subplots" in story_arc and not isinstance(story_arc["subplots"], list):
            story_arc["subplots"] = [story_arc["subplots"]]
        
        logging.info("Successfully generated story arc with all required keys")
        return story_arc
    
    logging.error(f"Failed to generate a valid story arc. Keys present: {story_arc.keys() if story_arc else 'None'}")
    logging.info("Generating a basic structure.")
    
    # Generate a basic structure
    return {
        "setting": {"description": topic['setting'], "characters_involved": character_names[:2], "worldbuilding_elements": topic['elements'][:2]},
        "inciting_incident": {"description": "A mysterious event occurs", "characters_involved": character_names[:2], "worldbuilding_elements": [topic['elements'][2]]},
        "rising_action": [
            {"description": "Characters investigate the event", "characters_involved": character_names, "worldbuilding_elements": [topic['elements'][3]], "subplot_development": "Subplot 1 begins", "character_development": {char: "Initial development" for char in character_names}}
        ],
        "climax": {"description": "Confrontation with the main challenge", "characters_involved": character_names, "worldbuilding_elements": topic['elements'], "character_development": {char: "Major development" for char in character_names}},
        "falling_action": {"description": "Dealing with the aftermath", "characters_involved": character_names[:3], "worldbuilding_elements": topic['elements'][:3], "subplot_resolution": [f"Subplot {i} resolution" for i in range(1, len(topic['subplots'])+1)]},
        "resolution": {"description": "A new equilibrium is established", "characters_involved": character_names, "worldbuilding_elements": topic['elements'], "character_final_state": {char: "Final character state" for char in character_names}},
        "subplots": [{"description": subplot, "characters_involved": character_names[:2], "events": ["Event 1", "Event 2", "Event 3"], "resolution": "Subplot resolution"} for subplot in topic['subplots']]
    }

def write_and_edit_chapter(chapter_number, event, characters, topic, story_arc, words_per_chapter=5000, max_iterations=5):
    character_info = "\n".join([
        f"{char['name']}: {char.get('occupation', '[Occupation]')}, "
        f"Traits: {', '.join(char.get('traits', ['[Trait]']))}, "
        f"Background: {char.get('background', '[Background]')}, "
        f"Growth Potential: {char.get('growth_potential', '[Growth Potential]')}"
        for char in characters
    ])    
    chapter_guidance = f"""
    Worldbuilding elements to explore: {', '.join(event.get('worldbuilding_elements', ['[Worldbuilding Element]']))}
    Subplot development: {event.get('subplot_development', 'Continue developing ongoing subplots')}
    Character development: {json.dumps(event.get('character_development', {}))}
    """
    
    chapter_writer.clear_context()
    chapter_content = chapter_writer(f"""Write Chapter {chapter_number} of our novel. 
    Topic: {json.dumps(topic)}
    Event: {json.dumps(event)}
    Characters: 
    {character_info}
    Chapter Guidance:
    {chapter_guidance}
    Remember to vividly depict our world and deeply explore our characters. 
    Ensure you incorporate each character's traits, occupation, background, and potential for growth into the narrative.
    Focus on detailed descriptions, character development, and world-building.
    Include more dialogue and introspective passages.
    Develop subplots alongside the main plot.
    Maintain consistency with the genre and overall theme.
    Write a lengthy, detailed chapter of approximately {words_per_chapter} words.
    IMPORTANT: Do not include any explanations, comments, or meta-text about the writing process in your output. Provide only the narrative content of the chapter.""")
    
    for iteration in range(max_iterations):
        editor.clear_context()
        feedback = editor(f"""Review the following chapter:

        {chapter_content}

        Provide specific, actionable feedback for improvement. If the chapter meets high standards, start your response with 'APPROVED:' followed by a brief summary of the chapter's strengths.

        Ensure the chapter:
        1. Is approximately {words_per_chapter} words long
        2. Includes detailed descriptions and world-building
        3. Shows strong character development
        4. Contains engaging dialogue
        5. Incorporates reflective or introspective passages
        6. Develops subplots alongside the main plot
        7. Maintains consistency with the genre and overall theme
        8. Addresses the specific chapter guidance:
        {chapter_guidance}

        Do not include any narrative content in your response.""")
        
        if feedback.startswith("APPROVED:"):
            logging.info(f"Chapter {chapter_number} approved after {iteration + 1} iterations.")
            return chapter_content
        
        logging.info(f"Editing iteration {iteration + 1} for Chapter {chapter_number}")
        chapter_writer.clear_context()
        chapter_content = chapter_writer(f"""Revise the following chapter based on this editorial feedback:
        {feedback}

        Original chapter:
        {chapter_content}

        Ensure the revised chapter:
        1. Maintains its length of approximately {words_per_chapter} words
        2. Addresses all points raised in the editorial feedback
        3. Continues to focus on detailed descriptions, character development, and world-building
        4. Includes engaging dialogue and introspective passages
        5. Develops subplots alongside the main plot
        6. Maintains consistency with the genre and overall theme
        7. Addresses the specific chapter guidance:
        {chapter_guidance}
        IMPORTANT: Do not include any explanations, comments, or meta-text about the revision process in your output. Provide only the revised narrative content of the chapter.""")
    
    logging.info(f"Max iterations reached for Chapter {chapter_number}. Using last version.")
    return chapter_content

def review_narrative(chapters, topic, characters, story_arc):
    narrative_summary = "\n".join([f"Chapter {i+1} Summary: {chapter[:200]}..." for i, chapter in enumerate(chapters)])
    
    narrative_reviewer.clear_context()
    prompt = f"""Review the overall narrative structure of the novel with the following details:
    Topic: {json.dumps(topic)}
    Characters: {json.dumps(characters)}
    Story Arc: {json.dumps(story_arc)}
    Chapter Summaries:
    {narrative_summary}

    Provide feedback on narrative flow, character development, subplot integration, thematic consistency, worldbuilding depth, genre adherence, and pacing.
    Respond with a JSON object containing your analysis and recommendations."""

    review_json = narrative_reviewer(prompt)
    review = validate_and_correct_json(review_json, narrative_reviewer)
    
    if review:
        logging.info("Narrative review completed.")
        return review
    else:
        logging.error("Failed to generate a valid narrative review.")
        return None

def apply_narrative_review(chapters, review, topic, characters, story_arc):
    if not review:
        return chapters

    updated_chapters = chapters.copy()

    for chapter_feedback in review.get('specific_chapter_feedback', []):
        chapter_number = chapter_feedback['chapter_number']
        if 1 <= chapter_number <= len(chapters):
            chapter_content = chapters[chapter_number - 1]
            
            chapter_writer.clear_context()
            revision_prompt = f"""Revise the following chapter based on this feedback:
            {json.dumps(chapter_feedback)}

            Original chapter:
            {chapter_content}

            Ensure the revised chapter:
            1. Addresses all points raised in the feedback
            2. Maintains consistency with the overall narrative
            3. Improves character development, subplot integration, and worldbuilding as suggested
            4. Maintains the original word count

            Topic: {json.dumps(topic)}
            Characters: {json.dumps(characters)}
            Story Arc: {json.dumps(story_arc)}
            """

            revised_chapter = chapter_writer(revision_prompt)
            updated_chapters[chapter_number - 1] = revised_chapter

    logging.info("Applied narrative review recommendations.")
    return updated_chapters

def generate_book(num_characters=5, num_chapters=25, words_per_chapter=5000):
    logging.info("Generating topic...")
    topic = generate_topic()
    if not topic:
        logging.error("Failed to generate a valid topic. Aborting book generation.")
        return None

    logging.info("Generating characters...")
    characters = generate_characters(num_characters, topic)
    
    if not characters:
        logging.error("No valid characters generated. Aborting book generation.")
        return None
    
    logging.info("Generating story arc...")
    story_arc = generate_story_arc(topic, characters)
    
    logging.info("Writing chapters...")
    chapters = []
    chapter_number = 1
    
    def update_progress():
        progress = (chapter_number / num_chapters) * 100
        logging.info(f"Progress: {progress:.2f}% ({chapter_number}/{num_chapters} chapters)")
    
    # Inciting incident
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["inciting_incident"], characters, topic, story_arc, words_per_chapter)
    chapters.append(chapter_content)
    chapter_number += 1
    update_progress()
    
    # Rising action
    for event in story_arc["rising_action"]:
        if chapter_number > num_chapters - 3:
            break
        chapter_content = write_and_edit_chapter(chapter_number, event, characters, topic, story_arc, words_per_chapter)
        chapters.append(chapter_content)
        chapter_number += 1
        update_progress()
    
    # Generate additional rising action events if needed
    while chapter_number <= num_chapters - 3:
        new_event = story_arc["rising_action"][-1]  # Use the last rising action event as a template
        chapter_content = write_and_edit_chapter(chapter_number, new_event, characters, topic, story_arc, words_per_chapter)
        chapters.append(chapter_content)
        chapter_number += 1
        update_progress()
    
    # Climax
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["climax"], characters, topic, story_arc, words_per_chapter)
    chapters.append(chapter_content)
    chapter_number += 1
    update_progress()
    
    # Falling action
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["falling_action"], characters, topic, story_arc, words_per_chapter)
    chapters.append(chapter_content)
    chapter_number += 1
    update_progress()
    
    # Resolution
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["resolution"], characters, topic, story_arc, words_per_chapter)
    chapters.append(chapter_content)
    update_progress()
    
    # Review and revise the narrative
    logging.info("Reviewing the overall narrative...")
    narrative_review = review_narrative(chapters, topic, characters, story_arc)
    if narrative_review:
        logging.info("Applying narrative review recommendations...")
        chapters = apply_narrative_review(chapters, narrative_review, topic, characters, story_arc)
    
    # Combine chapters into a book
    book = "\n\n".join(chapters)
    
    return book

# Generate the book
logging.info("Starting book generation...")
book = generate_book()

if book:
    # Save the book to a file
    filename = f"generated_novel_{int(time.time())}.txt"
    with open(filename, "w") as f:
        f.write(book)
    logging.info(f"Book generation complete. The book has been saved as '{filename}'.")
else:
    logging.error("Book generation failed.")

# Clear contexts
topic_generator.clear_context()
character_generator.clear_context()
story_arc_generator.clear_context()
chapter_writer.clear_context()
editor.clear_context()
publisher.clear_context()
narrative_reviewer.clear_context()
json_master.clear_context()

logging.info("All node contexts cleared.")
