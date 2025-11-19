

from flask import (
    Blueprint, request, jsonify, render_template, session, redirect
)

import os

import json

from .processCommand import processCommand

base_path = os.path.dirname(__file__)

import openai
from openai import OpenAI
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

import json

def extract_relevant_info_from_json(user_query, jsoninfo_file_path):
    def flatten_value(value):
        """Convert any dict or list into a readable string."""
        if isinstance(value, dict):
            return " ".join([flatten_value(v) for v in value.values()])
        elif isinstance(value, list):
            return " ".join(map(str, value))
        else:
            return str(value)

    def recursive_search(data, query_words, path="", results=None):
        if results is None:
            results = {}
        if isinstance(data, dict):
            for key, value in data.items():
                full_path = f"{path} - {key}" if path else key
                text_value = flatten_value(value)
                if any(word in key.lower() or word in text_value.lower() for word in query_words):
                    results[full_path] = text_value
                recursive_search(value, query_words, full_path, results)
        elif isinstance(data, list):
            for item in data:
                recursive_search(item, query_words, path, results)
        return results

    with open(jsoninfo_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_query_lower = user_query.lower()
    query_words = user_query_lower.split()

    matched_sections = recursive_search(data, query_words)

    if not matched_sections:
        matched_sections["Info"] = "No exact match found. Try rephrasing your question."

    formatted_result = "\n".join([f"{k}: {v}" for k, v in matched_sections.items()])
    return formatted_result




@bp.route('/')
def chat_page():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/auth/login')
    
    return render_template('bot/chat.html')


@bp.route('/ask', methods=['POST'])
def ask():
    # response = client.responses.create(
    # model="gpt-4o-mini",
    # input="Your input."
    # )
    # answer = response.output_text
    # return jsonify({"reply": answer})

    data = request.get_json()
    user_message = data.get("message", "")

    link_response = processCommand(user_message)

    if link_response:
        return jsonify({"reply": link_response})

    info_file_path = os.path.join(base_path, "info.txt")

    with open(info_file_path, "r") as f:
        college_info = f.read()

    jsoninfo_file_path = os.path.join(base_path, "info.json")
    relevant_info = extract_relevant_info_from_json(user_message, jsoninfo_file_path)


    prompt = f"""
    You are ISH (IET STUDENT HELP), a helpful AI assistant for IET DAVV.
    Use the following college data to answer the student's question accurately.

    Context:
    {relevant_info}

    Question: {user_message}
    """

    response = client.responses.create(
            model="gpt-4o-mini",  
            input= prompt
        )
   
    
    answer = response.output_text
    print(prompt)
    # print(user_message)
    # print(answer)
    return jsonify({"reply": answer})

    

    

    



    




