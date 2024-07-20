# VirtWorker Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)

## 1. Introduction

VirtWorker is a Python framework for creating and managing workflows with Language Learning Models (LLMs). It allows users to build complex AI-driven text processing and generation pipelines by chaining modular LLM operations.

## 2. Installation

### Prerequisites

- Debian 12
- CUDA 1.8
- NVIDIA RTX 3090 GPU
- Ollama

### Setup

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


## 3. Core Concepts

### Nodes

Nodes are the basic building blocks in VirtWorker. Each node represents a specific LLM operation, such as summarization or joke generation.

### Workflows

A workflow is a series of connected nodes that process input and produce output.

### Context

Nodes maintain context, allowing them to remember previous interactions within a session.

## 4. Basic Usage

Here's a simple example of how to use VirtWorker:

```python
from virtworker import *

# Create nodes
summarizer = create_node("gemma2:latest", "Summarizer")
summarizer.definition = "Summarize the given text concisely."

joke_writer = create_node("gemma2:latest", "Joke Writer")
joke_writer.definition = "Write a short, witty joke based on the given summary."

# Define workflow
summary = summarizer(input_text)
joke = joke_writer(summary)

print("Summary:", summary)
print("Joke:", joke)
```

## 5. Advanced Features

### Web Scraping and RSS Parsing

VirtWorker supports web scraping and RSS feed parsing for input:

```python
target_site = Website("https://www.yahoo.com/news/example-article-url")

summary = summarizer(target_site.text)
```

### Text-to-Speech

Generate audio from text output:

```python
summary_audio = generate_audio(summary, "summary.wav")
```

### Context Management

Clear node contexts for fresh interactions:

```python
summarizer.clear_context()
joke_writer.clear_context()
```

## 6. API Reference

### `create_node(model_name: str, name: str) -> Node`

Creates a new node with the specified model and name.

### `class Node`

- `definition`: Set the node's task definition.
- `__call__(input_text: str) -> str`: Process input and return output.
- `clear_context()`: Clear the node's conversation history.

### `class Website`

- `__init__(url: str, use_rss: bool = False, rss_feed_url: str = None)`
- `text`: Property that returns the fetched content.

### `generate_audio(text: str, filename: str) -> str`

Generates an audio file from the given text and returns the file path.

## 7. Troubleshooting

- Ensure Ollama is running before starting your VirtWorker script.
- Check that the required models (e.g., gemma2:latest) are available in Ollama.
- If you encounter CUDA errors, verify that your NVIDIA drivers and CUDA installation are correct.

## 8. Contributing

We welcome contributions to VirtWorker! Please see the [Contributing](README.md#contributing) section in the README for guidelines on how to contribute.

For any questions or issues not covered in this documentation, please open an issue on the GitHub repository or contact the project maintainer directly.
