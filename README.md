# VirtWorker

VirtWorker is a powerful framework for creating and managing workflows with Language Learning Models (LLMs). It provides a flexible and intuitive interface for chaining LLM operations, allowing users to build complex AI-driven text processing and generation pipelines.

## Description

VirtWorker serves as the spiritual successor to VirtWorkForce, evolving the concept of visual LLM workflow editing into a more robust and versatile programming framework. While it doesn't include the web-based visual editor of its predecessor, VirtWorker maintains the core philosophy of modular, chainable LLM operations, now implemented as a Python library for greater flexibility and integration capabilities.

## Features

- Modular node-based workflow creation for LLM operations
- Integration with Ollama for accessing various AI models
- Context-aware nodes that maintain conversation history
- Ability to clear node contexts for fresh interactions
- Support for web scraping and RSS feed parsing
- Text-to-speech functionality for generating audio from text output
- Flexible node creation with customizable definitions
- Logging system for tracking node operations and outputs

## System Requirements

- Debian 12
- CUDA 1.8
- NVIDIA RTX 3090 GPU

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/VirtWorker.git
   cd VirtWorker
   ```

2. Run the setup script:
   ```bash
   bash setup_envs.sh
   ```
   Note: This script will take a considerable amount of time to download and set up all necessary files and environments.

## Usage

To use VirtWorker, you'll need to write your workflow in the `main.py` file. Here's a basic example:

```python
from virtworker import *

# Create nodes
summarizer = create_node("llama3.1:8b", "Summarizer", max_tokens=16384)
summarizer.definition = "Summarize the given text concisely."

joke_writer = create_node("llama3.1:8b", "Joke Writer", max_tokens=16384)
joke_writer.definition = "Write a short, witty joke based on the given summary."

# Define workflow
summary = summarizer(input_text)
joke = joke_writer(summary)

print("Summary:", summary)
print("Joke:", joke)
```

To run your workflow:

1. Execute the script: `./run.sh`

## Contributing

Contributions to improve VirtWorker are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project was developed by David Hamner.
- Claude.ai was used as a coding and documentation assistant in the development of this project.
- Thanks to the Ollama project for providing the AI model integration capabilities.
- Inspired by the concept of VirtWorkForce, adapted into a programming framework.

## Contact

For any questions or feedback, please open an issue in the GitHub repository or contact David Hamner directly.
