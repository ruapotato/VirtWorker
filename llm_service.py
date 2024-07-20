import logging
import zmq
import requests
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_llm_service():
    logging.info("Starting LLM service using Ollama with gemma2:latest...")
    
    # Set up ZeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        try:
            # Wait for next request from client
            message = socket.recv_string()
            logging.info(f"Received request: {message[:50]}...")

            # Prepare the prompt for joke generation
            prompt = f"""Based on the following text, generate a short, witty joke:

{message}

Joke:"""

            # Send request to Ollama
            response = requests.post('http://localhost:11434/api/generate', 
                                     json={
                                         "model": "gemma2:latest",
                                         "prompt": prompt,
                                         "stream": False
                                     })
            
            if response.status_code == 200:
                result = response.json()
                joke = result['response'].strip()
                
                # Extract only the generated joke, not the entire prompt
                joke = joke.split("Joke:")[-1].strip()
                
                socket.send_string(joke)
                logging.info(f"Generated joke: {joke}")
            else:
                error_message = f"Error in Ollama API call: {response.status_code} - {response.text}"
                logging.error(error_message)
                socket.send_string(error_message)
                
        except Exception as e:
            error_message = f"Error in processing: {str(e)}"
            logging.error(error_message)
            socket.send_string(error_message)

if __name__ == "__main__":
    run_llm_service()
