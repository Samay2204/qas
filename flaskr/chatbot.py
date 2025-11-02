

from flask import (
    Blueprint, request, jsonify, render_template
)

import os

from .processCommand import processCommand

base_path = os.path.dirname(__file__)

import openai
from openai import OpenAI
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@bp.route('/')
def chat_page():
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


    prompt = f"""
    You are a helpful AI assistant for IET DAVV.
    Answer only using the information provided below.

    College Information:
    {college_info}


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

    

    

    



    




