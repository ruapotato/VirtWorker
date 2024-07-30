import feedparser
from newspaper import Article
import time
from virtworker import *
import random

def fetch_news(rss_url, max_articles=5):
    all_articles = []
    feed = feedparser.parse(rss_url)
    
    for entry in feed.entries[:max_articles]:
        article = Article(entry.link)
        try:
            article.download()
            article.parse()
            article.nlp()
            all_articles.append({
                'title': article.title,
                'text': article.text,
                'url': entry.link,
            })
            time.sleep(1)
        except Exception as e:
            print(f"Error processing article {entry.link}: {str(e)}")
    
    return all_articles

summarizer = create_node("llama3.1:8b", "Summarizer", max_tokens=16384)
summarizer.definition = "Summarize the given news article concisely and humorously in one sentence."

joke_writer = create_node("llama3.1:8b", "Joke Writer", max_tokens=16384)
joke_writer.definition = "Write a witty joke about the news summary. Be politically neutral."

monologue_generator = create_node("llama3.1:8b", "Monologue Generator", max_tokens=16384)
monologue_generator.definition = "Generate a short, funny late-night show monologue based on the news summary and joke. Include self-deprecating AI humor."

def generate_late_night_content(rss_url):
    news_articles = fetch_news(rss_url)
    content = []
    
    content.append("<host>Hello, humans! I'm Circuit Colbert, your AI late-night host. Let's dive into tonight's news!</host>")
    
    for article in news_articles:
        content.append(f"<onscreen>Headline: {article['title']}</onscreen>")
        
        summary = summarizer(article['text'])
        joke = joke_writer(summary)
        monologue = monologue_generator(f"{summary}\n{joke}")
        
        content.append(f"<host>{monologue}</host>")
    
    content.append("<host>That's all for tonight, folks! Remember, I may be artificial, but my love for you is real... or is it just a well-trained language model? You decide! Goodnight!</host>")
    
    return "\n\n".join(content)

if __name__ == "__main__":
    rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/US.xml'
    
    print("Generating content...")
    script_content = generate_late_night_content(rss_url)
    
    # Write the content to a file
    with open('late_night_show_script.txt', 'w') as f:
        f.write(script_content)

    print("\nScript has been saved to 'late_night_show_script.txt'")
    
    # Print the content of the file
    print("\nHere's the content of 'late_night_show_script.txt':")
    print(script_content)
