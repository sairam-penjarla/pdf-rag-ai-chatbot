import os
import json
import random
import re
import pandas as pd
import pandasql as ps
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from custom_logger import logger
from config import get_config
from src.session_utils import SessionUtilities
from src.multi_shot_examples import examples
from src.prompt_templates import instructions, prompt_instructions
from sentence_transformers import SentenceTransformer, CrossEncoder

# Load environment variables from .env file
load_dotenv()


class Utilities:
    """
    A utility class for handling various operations such as session management,
    retrieval-augmented generation (RAG) using ChromaDB, invoking LLM models,
    and managing user interactions with the chatbot.
    """

    def __init__(self):
        """
        Initializes the Utilities class by setting up configuration parameters,
        loading necessary models, and establishing database connections.
        """
        logger.debug("Initializing Utilities class")

        # Load configuration settings
        self.config = get_config()

        # Initialize session utilities for session-based operations
        self.session_utils = SessionUtilities()

        # Initialize OpenAI client for interacting with the LLM
        TOKEN = os.environ.get('TOKEN')
        HOST = os.environ.get('HOST')
        self.client = OpenAI(
            api_key = TOKEN,
            base_url = f"{HOST}/serving-endpoints"
        )

        # Setup persistent ChromaDB client and embedding collection
        self.chroma_client = chromadb.PersistentClient(path="knowledge_base")
        self.collection = self.chroma_client.get_or_create_collection(name="embeddings_collection")

        # Load SentenceTransformer for text embeddings
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Load CrossEncoder for more precise relevance ranking
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def fetch_top_relevant_queries(self, query: str, top_k: int = 10):
        """
        Retrieves the top-k most relevant queries from the ChromaDB collection using embedding similarity.

        :param query: The input search query.
        :param top_k: The number of relevant results to fetch.
        :return: A list of dictionaries containing relevant documents, metadata, and similarity scores.
        """
        # Convert query text into an embedding vector
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)

        # Perform similarity search in ChromaDB collection
        search_results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        # Process and structure the search results
        relevant_queries = [
            {
                "document": doc,
                "metadata": search_results['metadatas'][index],
                "score": search_results['distances'][index]
            }
            for index, doc in enumerate(search_results['documents'])
        ]

        return relevant_queries

    def get_relevant_content(self, query: str, top_k: int = 3):
        """
        Uses both embedding similarity and cross-encoder ranking to fetch the most relevant content.

        :param query: The input query to search for.
        :param top_k: Number of top results to return after ranking.
        :return: A list of dictionaries with top-ranked documents.
        """
        # Fetch top-k results based on embedding similarity
        candidate_results = self.fetch_top_relevant_queries(query, top_k=10)

        # Rank results using a cross-encoder model
        ranked_results = [
            {
                "document": candidate_results[0]['document'][i],
                "metadata": candidate_results[0]['metadata'][i],
                "similarity_score": candidate_results[0]['score'][i],
                "cross_encoder_score": self.cross_encoder.predict([(query, candidate_results[0]['document'][i])])[0]
            }
            for i in range(len(candidate_results[0]['document']))
        ]

        # Sort by cross-encoder score and return top-k
        return sorted(ranked_results, key=lambda x: x["cross_encoder_score"], reverse=True)[:top_k]


    def get_user_msg(self, content: str, question: str):
        """
        Constructs a structured user message for the LLM.

        :param content: Contextual information or retrieved documents.
        :param question: The user's query.
        :return: A dictionary formatted for OpenAI API.
        """
        logger.debug("Formatting user message for LLM interaction")

        return {
            "role": "user",
            "content": f"{prompt_instructions} Question: {question}\n\nContent: {content}\n\n"
        }

    def get_session_icon(self, session_id: str):
        """
        Retrieves the session icon associated with a session. If no icon is found,
        a random icon is assigned from the predefined directory.

        :param session_id: The ID of the session.
        :return: The filename of the session icon.
        """
        icon_name = self.session_utils.get_session_icon(session_id)
        if icon_name is None:
            icons_dir_path = "static/images/session-icons"
            random_icon = random.choice([x for x in os.listdir(icons_dir_path) if x.endswith(".svg")])
            return random_icon
        return icon_name

    def get_previous_messages(self, session_id: str):
        """
        Retrieves the previous conversation messages for a given session.

        :param session_id: The ID of the session.
        :param instructions: System-level instructions for the LLM.
        :param component: The specific component (e.g., "response") to retrieve.
        :return: A list of formatted messages for the conversation history.
        """
        session_data = self.session_utils.get_session_data(session_id)

        # Construct initial system message
        messages = [{"role": "system", "content": instructions}]

        # Add few-shot examples
        messages += examples

        # Append past user interactions and assistant responses
        for request in session_data:
            messages.append({"role": "user", "content": request['prompt']})
            messages.append({"role": "assistant", "content": str(request['llm_output'])})

        return messages

    def invoke_llm(self, messages):
        """
        Sends a structured message history to the OpenAI chat model and retrieves a response.

        :param messages: List of message dictionaries structured for OpenAI API.
        :return: The text response from the LLM.
        """
        logger.debug("Invoking OpenAI LLM with standard request")

        # Prepare API parameters
        llm_params = self.config.LLM_PARAMS
        llm_params.update({"messages": messages, "stream": False})

        # Invoke OpenAI API for chat completion
        chat_completion = self.client.chat.completions.create(**llm_params)

        return chat_completion.choices[0].message.content

    def invoke_llm_stream(self, messages):
        """
        Streams the LLM response for real-time interaction.

        :param messages: List of message dictionaries structured for OpenAI API.
        :yield: A generator yielding the streamed response content.
        """
        logger.debug("Invoking OpenAI LLM with streaming response")

        # Prepare API parameters
        llm_params = self.config.LLM_PARAMS
        llm_params.update({"messages": messages, "stream": True})

        # Invoke OpenAI API for streaming chat completion
        chat_completion = self.client.chat.completions.create(**llm_params)

        # Yield response in real-time
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content
