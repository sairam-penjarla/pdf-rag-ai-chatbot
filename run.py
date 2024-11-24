import os
import uuid
from src.utils import Utilities, ConversationDB
from src.prompt_templates import BOT_RESPONSE_GUIDELINES
from flask import (
    Flask, 
    Response, 
    jsonify, 
    render_template, 
    request
)

app = Flask(__name__)
conv_db = ConversationDB()
utils = Utilities()
bot_conversation = utils.get_default_conversation()

# Ensure a folder exists to store the uploaded PDFs
UPLOAD_FOLDER = "static/uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def landing_page():
    # Retrieve conversations
    conversations = conv_db.retrieve_conversations()
    
    # List all PDF files in the UPLOAD_FOLDER
    pdf_files = []
    if os.path.exists(UPLOAD_FOLDER):
        pdf_files = [
            os.path.join(UPLOAD_FOLDER, f)
            for f in os.listdir(UPLOAD_FOLDER)
            if f.endswith('.pdf')
        ]

    return render_template("index.html", conversations=conversations, pdf_files=pdf_files)


@app.route('/create_vector_index', methods=['POST'])
def create_vector_index():
    if 'pdf' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            # Generate a unique filename to avoid collisions
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

            # Save the file to the local folder
            file.save(file_path)
            
            # Read the content from the saved file for processing
            with open(file_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
                utils.read_documents(pdf_bytes)

            # Return a success response
            return jsonify({'success': True, 'file_path': file_path})
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400



@app.route('/invoke_bot', methods=['POST'])
def invoke_bot():
    data = request.get_json()

    user_input = data.get('user_input')
    file_is_attached = data.get('file_is_attached')

    CONTENT = utils.query_chromadb(user_input) if file_is_attached else ""

    msg = utils.get_user_msg( 
                content = CONTENT, 
                conversations = bot_conversation, 
                present_question = user_input + BOT_RESPONSE_GUIDELINES, 
            )
    bot_output = utils.invoke_llm_stream(conversations = bot_conversation + [msg])

    return Response(bot_output, content_type='text/event-stream')

@app.route('/delete_conversations', methods=['DELETE'])
def delete_conversations():
    """Delete all conversations from the database."""
    conv_db.delete_all_conversations()
    return jsonify({"success": True, "message": "All conversations deleted."})

@app.route('/update_conversation', methods=['POST'])
def update_conversation():
    data = request.get_json()
    user_input = data.get('user_input')
    llm_output = data.get('llm_output')
    flow_index = data.get('flow_index')
    conversation_index = data.get('conversation_index')
    
    bot_conversation.append({"role" : "user", "content" : user_input})
    bot_conversation.append({"role" : "assistant", "content" : llm_output})

    conv_db.store_conversation(user_input, llm_output, flow_index, conversation_index)

    return jsonify({"success" : True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)