import uuid
import PyPDF2
import sqlite3
import markdown
import chromadb
import pandas as pd
from io import BytesIO
from logger import logger
from openai import OpenAI
from config import get_config
from dotenv import load_dotenv
from src.prompt_templates import BOT_GUIDELINES
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


load_dotenv()

class CustomEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, documents):
        return [self.model.encode(d).tolist() for d in documents]

    def embed_query(self, query: str):
        return self.model.encode([query])[0].tolist()


class ConversationDB:
    def __init__(self, db_name="conversations.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """Create the table for storing conversations if it doesn't exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            flow_index INTEGER DEFAULT 0,
            conversation_index INTEGER DEFAULT 0
        )
        """)
        self.connection.commit()

    def store_conversation(self, question: str, answer: str, flow_index: int = 0, conversation_index: int = 0):
        """Store a question, answer, and flow index into the database."""
        self.cursor.execute("""
        INSERT INTO conversations (question, answer, flow_index, conversation_index)
        VALUES (?, ?, ?, ?)
        """, (question, answer, flow_index, conversation_index))
        self.connection.commit()

    def retrieve_conversations(self):
        """Retrieve all conversations from the database along with the flow index."""
        self.cursor.execute("SELECT question, answer, flow_index, conversation_index FROM conversations")
        rows = self.cursor.fetchall()
        conversations = [{"question": row[0], "answer": row[1], "flow_index": row[2], "conversation_index": row[2]} for row in rows]
        return conversations

    def delete_all_conversations(self):
        """Delete all conversations from the database."""
        self.cursor.execute("DELETE FROM conversations")
        self.connection.commit()

    def close(self):
        """Close the database connection."""
        self.connection.close()


class Utilities:
    def __init__(self):
        logger.debug("initializing utilities")
        self.config = get_config()
        self.client = OpenAI()
        self.vector_db_client = chromadb.Client()
        self.embedding_model = CustomEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    def get_default_conversation(self):
        logger.debug("getting default conversations")
        return [
            {
            "role": "system",
            "content": BOT_GUIDELINES
            }
        ]

    
    def get_user_msg(self, 
                     content, 
                     conversations, 
                     present_question, 
                     previous_question="", 
                     previous_answer=""
                    ):
        logger.debug("getting user message")
        if len(conversations) > 1:
            previous_question = "Previous Question: " + conversations[-2]['content']
            previous_answer = "Previous Answer: " + conversations[-1]['content']

        return {
            "role": "user",
            "content": f"Content:{content}\n\n{previous_question}\n\n{previous_answer}\n\nQuestion:{present_question}\n\nAnswer:",
        }

    def markdown_to_html(self, markdown_text):
        logger.debug("converting markdown to html")
        self.html_text = markdown.markdown(markdown_text, extensions=['tables'])
    
    def invoke_llm_stream(self, conversations):
        logger.debug("invoking llm")
        llm_params = self.config['LLM_PARAMS']
        llm_params['messages'] = conversations
        llm_params['stream'] = True

        # for i in conversations:
        #     print(i)

        chat_completion = self.client.chat.completions.create(
            **llm_params
        )

        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def embed_document(self, text):
        return self.embedding_model.embed_query(text)  

    def add_documents_to_collection(self, documents):
        for doc_id, text in enumerate(documents):
            embedding = self.embed_document(text)
            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                ids=[str(uuid.uuid4())]
            )

    def query_chromadb(self, query, top_n=3):
        query_embedding = self.embed_document(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_n)
        return "\n\n".join(results["documents"][0])
    

    def read_documents(self, content):
        self.collection = self.vector_db_client.get_or_create_collection("kaggle_old")
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        text = ''.join(page.extract_text() or '' for page in pdf_reader.pages)
        chunks = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=156).split_text(text)
        self.add_documents_to_collection(chunks)