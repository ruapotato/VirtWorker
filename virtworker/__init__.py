import logging
import requests
from bs4 import BeautifulSoup
import feedparser
import os
import sys
import json
import time
import zmq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            logging.info(f"Fetched {len(self._text)} characters from the website")
        return self._text

    def _fetch_from_url(self):
        logging.info(f"Fetching content from: {self.url}")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()

    def _fetch_from_rss(self):
        logging.info(f"Fetching content from RSS feed: {self.rss_feed_url}")
        feed = feedparser.parse(self.rss_feed_url)
        for entry in feed.entries:
            if entry.link == self.url:
                return entry.summary
        logging.warning(f"URL {self.url} not found in RSS feed. Falling back to direct URL fetch.")
        return self._fetch_from_url()

class Node:
    def __init__(self, model_name: str, name: str):
        self.model_name = model_name
        self.name = name
        self.definition = ""
        self.context = []

    def __call__(self, input_text: str):
        logging.info(f"[{self.name}] Processing input: {input_text[:50]}...")
        try:
            context_str = "\n".join(self.context)
            prompt = f"{self.definition}\n\nContext:\n{context_str}\n\nInput: {input_text}\n\nOutput:"
            response = requests.post('http://localhost:11434/api/generate', 
                                     json={
                                         "model": self.model_name,
                                         "prompt": prompt,
                                         "stream": False
                                     })
            
            if response.status_code == 200:
                output = response.json()['response'].strip()
                self.context.append(f"Input: {input_text}")
                self.context.append(f"Output: {output}")
                logging.info(f"[{self.name}] Output: {output[:50]}...")
                return output
            else:
                error_message = f"Error in Ollama API call: {response.status_code} - {response.text}"
                logging.error(error_message)
                return error_message
        except Exception as e:
            error_message = f"Error in processing: {str(e)}"
            logging.error(error_message)
            return error_message

    def clear_context(self):
        self.context = []
        logging.info(f"[{self.name}] Context cleared.")

def create_node(model_name: str, name: str):
    logging.info(f"Creating node '{name}' with model '{model_name}'")
    return Node(model_name, name)

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

    logging.info(f"TTS request written to {request_file}")

    timeout = 300  # 5 minutes timeout
    start_time = time.time()
    while not os.path.exists(output_file):
        if time.time() - start_time > timeout:
            logging.error("Timeout waiting for TTS output")
            return None
        time.sleep(1)

    logging.info(f"TTS output received: {output_file}")
    return output_file

# Check if Ollama is running
def check_ollama():
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            logging.info("Ollama is running.")
            return True
        else:
            logging.error("Ollama is not responding correctly.")
            return False
    except requests.ConnectionError:
        logging.error("Ollama is not running. Please start Ollama with 'ollama serve'.")
        return False

# Check Ollama on import
if not check_ollama():
    sys.exit(1)
