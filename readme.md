# [![Website](https://img.shields.io/badge/Website-Visit-brightgreen)](https://psairam9301.wixsite.com/website) [![YouTube](https://img.shields.io/badge/YouTube-Subscribe-red)](https://www.youtube.com/@sairampenjarla) [![GitHub](https://img.shields.io/badge/GitHub-Explore-black)](https://github.com/sairam-penjarla) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/sairam-penjarla-b5041b121/) [![Instagram](https://img.shields.io/badge/Instagram-Follow-ff69b4)](https://www.instagram.com/sairam.ipynb/)

# AI Chatbot with a Knowledge Base

## 🛠️ Installation and Setup Instructions

Follow the instructions below to clone this repository and set up the project in your local environment:

### 1. Clone the Repository

Run the following command in your terminal to clone the GitHub repository:

```bash
git clone https://github.com/sairam-penjarla/pdf-rag-ai-chatbot.git
```

### 2. Change Directory

Navigate into the cloned directory using the command:

```bash
cd pdf-rag-ai-chatbot
```

### 3. Set Up Virtual Environment

To create a virtual environment, follow the instructions in my [blog post on virtual environments](https://psairam9301.wixsite.com/website/post/learn-virtualenv-basics) or use one of the following commands depending on your environment:

- For **virtualenv**:
  ```bash
  python3 -m venv venv
  ```

- For **Anaconda**:
  ```bash
  conda create --name ai-chatbot python=3.8
  conda activate ai-chatbot
  ```

### 4. Install Dependencies

Once the virtual environment is set up, install the project dependencies by running:

```bash
pip install -r requirements.txt
```

### 5. Run the Project

To start the Flask server and run the project locally, use the following command:

```bash
python app.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## 📜 Project Details

The **AI Chatbot with a Knowledge Base** project is designed to create a chatbot that can interact with users using a knowledge base derived from PDF documents. It utilizes several key components to enable this functionality:

1. **Flask API**: The backend is built using Flask, which serves the frontend and handles user interactions.
2. **ChromaDB**: The project uses ChromaDB as the knowledge base to store and retrieve embeddings from PDF files.
3. **Sentence-Transformers Model**: The `sentence-transformers/all-MiniLM-L6-v2` model is used to create embeddings for the PDF content, allowing efficient similarity-based retrieval.
4. **User Interaction**: Users can chat with the AI chatbot, which is connected to the knowledge base. The chatbot can answer questions based on the data contained in the uploaded documents.
5. **Add More Documents**: Users have the option to upload additional PDFs to expand the knowledge base.
6. **Conversation History**: All previous conversations are stored in a SQLite database and are loaded into the UI when the page is refreshed.
7. **Clear Conversations**: Users can clear the conversation history directly from the UI.
8. **Document Preview**: The UI includes a preview window displaying thumbnails of the PDF files used in the knowledge base. Clicking on a thumbnail shows the content of the respective file.
9. **Main Components**: The core components of this project include **OpenAI** for the chatbot and **ChromaDB** for storing document embeddings.

## 📘 Learn More

For a detailed explanation and walkthrough of how this project works, check out my [blog post on this project](https://psairam9301.wixsite.com/website/post/ai-chatbot-with-a-knowledge-base).

## 🎥 Watch the Video

For a step-by-step guide, you can also watch the video on my [YouTube Channel](https://www.youtube.com/@sairampenjarla).
