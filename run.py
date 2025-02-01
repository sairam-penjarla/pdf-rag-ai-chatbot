import os
import json
import traceback
from flask import Flask, Response, jsonify, render_template, request
from src.utils import Utilities
from custom_logger import logger

# Initialize Flask app
app = Flask(__name__)

# Initialize utilities
utils = Utilities()

# ---------------- Landing Page ----------------

@app.route("/")
def landing_page():
    """
    Renders the main application interface.
    Fetches previous session metadata and passes it to the frontend.
    """
    try:
        previous_sessions = utils.session_utils.get_session_meta_data()
        return render_template("index.html", previous_session_meta_data=previous_sessions)
    except Exception as e:
        logger.error(f"Error in landing_page: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

# ---------------- Session Management Routes ----------------

@app.route('/get_random_session_icon', methods=['POST'])
def get_random_session_icon():
    """
    Returns a random session icon for a given session ID.
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        return jsonify({"session_icon": utils.get_session_icon(session_id)})
    except Exception as e:
        logger.error(f"Error in get_random_session_icon: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/get_session_data', methods=['POST'])
def get_session_data():
    """
    Retrieves session data for a given session ID.
    """
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        session_data = utils.session_utils.get_session_data(session_id)
        return jsonify({'session_data': session_data})
    except Exception as e:
        logger.error(f"Error in get_session_data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/delete_session', methods=['POST'])
def delete_session():
    """
    Deletes a specific session based on session ID.
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"error": "Session ID is required."}), 400

        response, status_code = utils.session_utils.delete_session(session_id)
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in delete_session: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/delete_all_sessions', methods=['POST'])
def delete_all_sessions():
    """
    Deletes all stored sessions.
    """
    try:
        response, status_code = utils.session_utils.delete_all_sessions()
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in delete_all_sessions: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/update_session', methods=['POST'])
def update_session():
    """
    Updates a session with new data (prompt, SQL query, assistant responses, etc.).
    """
    try:
        data = request.get_json()

        session_id = data.get('session_id')
        prompt = data.get('prompt')
        session_icon = data.get('session_icon')
        meta_data = data.get('meta_data')
        llm_output = data.get('llm_output')

        utils.session_utils.add_data(session_id, prompt, llm_output, meta_data, session_icon)

        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error in update_session: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

# ---------------- Content Retrieval Routes ----------------

@app.route('/get_relevant_content', methods=['POST'])
def get_relevant_content():
    """
    Retrieves the most relevant content from the knowledge base based on user input.
    """
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        relevant_content = utils.get_relevant_content(user_input)
        # Convert the numpy float32 values to regular float
        for result in relevant_content:
            result['similarity_score'] = float(result['similarity_score'])
            result['cross_encoder_score'] = float(result['cross_encoder_score'])

        # Now you can serialize it into JSON
        json_output = json.dumps(relevant_content, indent=4)

        return jsonify({"relevant_content": json_output})
    except Exception as e:
        logger.error(f"Error in get_relevant_content: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

# ---------------- AI Agent Invocation ----------------

@app.route('/invoke_agent', methods=['POST'])
def invoke_agent():
    """
    Processes a user query and streams an AI-generated response.
    Utilizes session history and relevant content for context.
    """
    try:
        data = request.get_json()

        user_input = data.get('user_input')
        session_id = data.get('session_id')
        relevant_content = data.get('relevant_content')
        relevant_content = " ".join([x['document'] for x in relevant_content])

        # Retrieve conversation history
        previous_messages = utils.get_previous_messages(session_id)

        # Format the user message
        user_message = utils.get_user_msg(relevant_content, user_input)

        # Stream AI-generated response
        agent_output = utils.invoke_llm_stream(messages=previous_messages + [user_message])
        return Response(agent_output, content_type='text/event-stream')

    except Exception as e:
        logger.error(f"Error in invoke_agent: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred"}), 500

# ---------------- Application Entry Point ----------------

if __name__ == "__main__":
    """
    Starts the Flask application.
    Accessible at http://0.0.0.0:8000
    """
    app.run(host="0.0.0.0", port=8000)
