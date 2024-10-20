# NLP to SQL AI Agent

This project is a Flask application that utilizes natural language processing to interact with SQL databases. It allows users to input queries in natural language, extract relevant schemas, and generate SQL content dynamically. The application can be easily modified to work with different databases and prompt guidelines.

## Features

- **Extract Relevant Schema**: Extracts the relevant schema based on user input and provided guidelines.
- **Gather SQL Content**: Executes SQL queries on the database and retrieves the content.
- **Invoke Agent**: Streams responses from the AI agent based on the SQL content and user input.
- **Markdown to HTML Conversion**: Converts agent output from Markdown format to HTML.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- Required libraries (install using `pip install -r requirements.txt`)

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/sairam-penjarla/nlp-to-sql-ai-agent.git
   cd nlp-to-sql-ai-agent
   ```

2. **Install Dependencies**:

   Make sure you have all required libraries installed. You can install them by running:

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Dataset**:

   This project uses a sample dataset from Kaggle. Download the [Phone Search Dataset](https://www.kaggle.com/datasets/shreyasur965/phone-search-dataset?resource=download) and place it in the appropriate directory.

### Configuration

- You can modify the `execute_query` function in `src/utils.py` to connect to your own database.
- Update the guidelines in `src/prompt_templates.py` as per your requirements.
- Adjust the examples in the `get_default_conversation` function in `src/utils.py` to customize the conversations.

### Running the Application

To run the application, execute the following command:

```bash
python run.py
```

The application will start and be accessible at `http://0.0.0.0:8000`.

## API Endpoints

- `POST /extract_relavant_schema`: Extracts relevant schema based on user input.
- `POST /gather_sql_content`: Gathers SQL content based on the extracted schema and user input.
- `POST /invoke_agent`: Invokes the agent to get a response based on the SQL content.
- `POST /markdown_to_html`: Converts the agent output from Markdown to HTML.

## YouTube Video

For a walkthrough of this project, check out my YouTube video [here](<insert_youtube_video_link>).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Kaggle](https://www.kaggle.com) for the dataset.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [OpenAI](https://openai.com/) for the LLM capabilities.