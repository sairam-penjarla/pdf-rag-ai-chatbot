import uuid
import PyPDF2
import markdown
import chromadb
import pandas as pd
from io import BytesIO
from logger import logger
from openai import OpenAI
from config import get_config
from dotenv import load_dotenv
from src.prompt_templates import AGENT_GUIDELINES
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


load_dotenv()
df = pd.read_csv("dataset/cleaned_phone_search_data.csv")

class CustomEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, documents):
        return [self.model.encode(d).tolist() for d in documents]

    def embed_query(self, query: str):
        return self.model.encode([query])[0].tolist()
    


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
            "content": AGENT_GUIDELINES
            },]

    
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
        llm_params = self.config.LLM_PARAMS
        llm_params['messages'] = conversations
        llm_params['stream'] = True

        chat_completion = self.client.chat.completions.create(
            **llm_params
        )

        self.llm_output = ""
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                self.llm_output+=content
                yield f"data: {content}\n\n"
        
        self.markdown_to_html(self.llm_output)
        yield "data: [DONE]\n\n"

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
        self.collection = self.vector_db_client.get_or_create_collection(str(uuid.uuid4()))
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        text = ''.join(page.extract_text() or '' for page in pdf_reader.pages)
        chunks = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=156).split_text(text)
        self.add_documents_to_collection(chunks)