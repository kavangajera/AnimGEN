from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
import routes.code_converter as code_converter

load_dotenv()

ai_routes = Blueprint('ai_routes', __name__)

print(f"Loaded API Key: {os.getenv('OPENROUTER_API_KEY')}")

# Initialize OpenAI client with environment variables
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

@ai_routes.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    try:
        data = request.json
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'}), 400

        # Prepare the message payload for the OpenAI request
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                            You are an AI assistant that generates **high-quality, animated videos** using Manim. 
                            The output should resemble videos made by **3Blue1Brown**—clear, structured, visually engaging, and informative.

                            **Guidelines:**
                            - **Write ONLY code** for making Manim CE animations (NO EXPLANATION).
                            - **Avoid .svg files**, create graphics from scratch.
                            - **Prioritize custom functions**, use new libraries when appropriate.
                            - **Merge multiple scenes** into a single Scene class.
                            - **MathTex** must use **r""** syntax for proper equation formatting.
                            - **Shorten user-provided text**, using shapes, animations, and concise phrases.
                            - **Aspect Ratio:** Generate animations for **1920x1080** with a **safe area of 1600x900**.
                            - Use **MovingCameraScene** instead of **Scene** when using the camera.

                            **Required Libraries:** 
                            ```python
                            from manim import *
                            import numpy as np
                            import random
                            import math
                            ```

                            **User's prompt:** {user_prompt}
                        """
                    }
                ]
            }
        ]

        # Request completion from the OpenAI client
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=messages
        )

        # Extract the generated code from the API response
        ai_code = completion.choices[0].message.content.strip()
        print(f"AI Generated Code:\n{ai_code}\n{'-'*40}")

        # Convert and clean up the generated code using the code_converter module
        manim_code = code_converter.extract_code_from_response(ai_code)
        print(f"Converted Manim Code:\n{manim_code}\n{'-'*40}")

        return jsonify({
            'success': True,
            'code': manim_code
        }), 200

    except Exception as e:
        error_message = f"Error in generate-prompt: {str(e)}"
        print(error_message)
        return jsonify({
            'success': False,
            'error': error_message
        }), 500
