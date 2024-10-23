# [![Website](https://img.shields.io/badge/Website-Visit-brightgreen)](https://psairam9301.wixsite.com/website) [![YouTube](https://img.shields.io/badge/YouTube-Subscribe-red)](https://www.youtube.com/@sairampenjarla) [![GitHub](https://img.shields.io/badge/GitHub-Explore-black)](https://github.com/sairam-penjarla) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/sairam-penjarla-b5041b121/) [![Instagram](https://img.shields.io/badge/Instagram-Follow-ff69b4)](https://www.instagram.com/sairam.ipynb/)

# Building a RAG Application Part 1

## Introduction

Welcome to the **Building a RAG Application Part 1** project! This repository contains the code for the first part of a series where we build a Retrieval-Augmented Generation (RAG) application. We will use a structure previously explored, where we built an LLM-based chatbot, understood the basics of vector databases, and created an AI agent.

This first part covers the creation of a **basic RAG application** along with a working demo. In the next part, we will enhance the app and make it more robust.

## Getting Started

To set up this project on your local machine, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/sairam-penjarla/pdf-rag-ai-chatbot.git
```

### 2. Navigate to the project directory

```bash
cd pdf-rag-ai-chatbot
```

### 3. Set up the environment

You can create a virtual environment using `virtualenv` or Anaconda.

- For a tutorial on creating a virtual environment, check out my blog post: [Learn Virtualenv Basics](https://psairam9301.wixsite.com/website/post/learn-virtualenv-basics).

- Using `virtualenv`:

```bash
python -m venv env
source env/bin/activate  # On Windows, use: .\env\Scripts\activate
```

- Using Anaconda:

```bash
conda create --name myenv python=3.8
conda activate myenv
```

### 4. Install the project dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the project

Once the dependencies are installed, you can start the project by running:

```bash
python app.py
```

## Project Details

This project is focused on building a **Retrieval-Augmented Generation (RAG)** application. It uses the following concepts:

- **LLM-based Chatbot:** We have previously built a chatbot using large language models (LLM).
- **Vector Database:** We explored vector databases and how they help in storing and retrieving relevant information.
- **AI Agent:** We built an AI agent using the above structures.

The purpose of this RAG application is to augment the generative capabilities of a language model with external knowledge, retrieved from a vector database. This allows for more accurate and context-aware responses.

### Key Features

- **Basic RAG Setup**: This part covers the fundamentals of RAG and how to implement a simple RAG application.
- **Working Demo**: We’ll explore how to integrate the vector database and language model for generating responses.
- **Modular Structure**: Built on the foundation of previous chatbot and AI agent projects, this structure can be expanded and modified.
  
In **Part 2**, we will further enhance this basic RAG application, adding robustness and additional features.

## Learn More

For a more detailed explanation of this project, check out my blog post:

[In-depth Blog Post on Building a RAG Application](https://psairam9301.wixsite.com/website)

Stay tuned for the upcoming **Part 2**, where we’ll continue to improve the RAG application!

---

Feel free to watch my video tutorials on this topic as well:

- [YouTube Video Tutorial](https://www.youtube.com/@sairampenjarla)

Thank you for checking out the project!
