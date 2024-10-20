from src.utils import Utilities
from flask import (
    Flask, 
    Response, 
    jsonify, 
    render_template, 
    request
)

app = Flask(__name__)
utils = Utilities()

agent_conversation = utils.get_default_conversation()

@app.route("/")
def landing_page():
    return render_template("index.html")

# Route to handle the PDF upload and process content
@app.route('/create_vector_index', methods=['POST'])
def create_vector_index():
    if 'pdf' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        pdf_bytes = file.read()  # Read the PDF content as bytes
        
        try:
            # Send the byte content directly to utils.read_documents
            utils.read_documents(pdf_bytes)

            # Return a success response
            return jsonify({'success': True})
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400


@app.route('/invoke_agent', methods=['POST'])
def invoke_agent():
    data = request.get_json()

    user_input = data.get('user_input')
    file_is_attached = data.get('file_is_attached')

    CONTENT = utils.query_chromadb(user_input) if file_is_attached else ""

    msg = utils.get_user_msg( 
                content = CONTENT, 
                conversations = agent_conversation, 
                present_question = user_input, 
            )
    agent_output = utils.invoke_llm_stream(conversations = agent_conversation + [msg])

    return Response(agent_output, content_type='text/event-stream')


@app.route('/markdown_to_html', methods=['POST'])
def markdown_to_html():
    data = request.get_json()
    user_input = data.get('user_input')
    
    agent_conversation.append({"role":"user", "content":user_input})
    agent_conversation.append({"role":"assistant", "content":utils.llm_output})

    return jsonify({"agent_output" : utils.html_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)