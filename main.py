from virtworker import *
import logging

# Set logging level to INFO to see all output
logging.getLogger().setLevel(logging.INFO)

# Use an RSS feed for Yahoo News
yahoo_rss_feed = "https://www.yahoo.com/news/rss"
target_site = Website("https://www.yahoo.com/news/biden-says-mistake-bullseye-reference-214050120.html", use_rss=True, rss_feed_url=yahoo_rss_feed)

manager = create_node("gemma2:latest", "Manager")
manager.definition = """You are a manager overseeing the creation of a short summary and a joke about a news article. 
Your tasks are:
1. Review the summary to ensure it's concise (no more than 2-3 sentences) and captures the key points of the news.
2. Review the joke to ensure it's relevant to the summary and appropriate.
3. If the joke needs improvement, provide specific feedback.
4. Once the joke meets your standards, approve it by starting your response with 'APPROVED:' followed by the summary and joke.

Respond in the following format:
[Your feedback or approval]
Summary: [The given summary]
Joke: [The current joke]"""

summarizer = create_node("gemma2:latest", "Summarizer")
summarizer.definition = "You are a concise news summarizer. Provide a brief summary of the given text in 2-3 sentences, capturing the key points. Don't use phrases like 'This article' or 'The text talks about'. Just give the summary directly."

joke_writer = create_node("gemma2:latest", "Joke Writer")
joke_writer.definition = "You are a clever joke writer. Based on the given summary of a news story, create a short, witty joke that's relevant to the main points of the story. The joke should be no more than 2-3 sentences."

# Get the summary (only once)
summary = summarizer(target_site.text)
print("Summary:", summary)

# Get the initial joke
initial_joke = joke_writer(summary)
print("Initial joke:", initial_joke)

# Combine summary and joke for manager review
content = f"Summary: {summary}\nJoke: {initial_joke}"
feedback = manager(content)

max_iterations = 5
iteration = 0

while "APPROVED:" not in feedback and iteration < max_iterations:
    print(f"\nIteration {iteration + 1}:")
    print(feedback)
    
    # Extract the current joke from the feedback
    joke_start = feedback.find("Joke: ") + 6
    current_joke = feedback[joke_start:].strip()

    # Improve joke based on feedback
    improved_joke = joke_writer(f"Improve this joke based on the feedback and summary: {feedback}\n\nCurrent summary: {summary}\nCurrent joke: {current_joke}")

    # Combine summary and improved joke for next review
    content = f"Summary: {summary}\nJoke: {improved_joke}"
    feedback = manager(content)
    
    iteration += 1

if "APPROVED:" in feedback:
    # Extract the final approved joke
    approved_content = feedback.split("APPROVED:")[1].strip()
    final_joke = approved_content.split("Joke:")[1].strip()

    print("\nFinal approved summary:")
    print(summary)
    print("\nFinal approved joke:")
    print(final_joke)
else:
    print("\nMax iterations reached without approval. Last feedback:")
    print(feedback)

# Generate audio files
summary_audio = generate_audio(summary, "summary.wav")
joke_audio = generate_audio(final_joke, "joke.wav")

# Clear contexts
manager.clear_context()
summarizer.clear_context()
joke_writer.clear_context()

print("Audio files generated and contexts cleared.")
