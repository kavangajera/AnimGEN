from flask import Blueprint, request, jsonify
import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import routes.code_converter as code_converter
from cloudinary.uploader import upload as cloudinary_upload
import cloudinary

load_dotenv()

ai_routes = Blueprint('ai_routes', __name__)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

@ai_routes.route('/generate-video', methods=['POST'])
def generate_video():
    try:
        data = request.json
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'}), 400

        # Prepare the message payload for the OpenAI request
        messages = [
            {
                "role": "user",
                "content": f"""
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

        # Request completion from OpenAI
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=messages
        )

        # Extract the generated Manim code from the response
        ai_code = completion.choices[0].message.content.strip()
        print(f"AI Generated Code:\n{ai_code}\n{'-'*40}")

        # Convert and clean up the generated code using the code_converter module
        manim_code = code_converter.extract_code_from_response(ai_code)
        print(f"Converted Manim Code:\n{manim_code}\n{'-'*40}")

        # Save the Manim code to a temporary Python file
        manim_file_path = 'temp_manim_script.py'
        with open(manim_file_path, 'w') as f:
            f.write(manim_code)

        # Generate the video using Manim with 240p resolution
        output_directory = 'media'
        os.makedirs(output_directory, exist_ok=True)

        command = [
            'manim',
            '-pql',                    # Low quality (240p) preview
            '-r', '426,240',           # Set resolution to 240p
            '--media_dir', output_directory,
            manim_file_path
        ]

        subprocess.run(command, check=True)

        # Find the generated video file
        video_files = [f for f in os.listdir(output_directory) if f.endswith('.mp4')]
        if not video_files:
            return jsonify({'success': False, 'error': 'Video generation failed'}), 500

        video_path = os.path.join(output_directory, video_files[0])

        # Upload the video to Cloudinary
        upload_result = cloudinary_upload(video_path, resource_type='video')
        video_url = upload_result.get('url')

        if not video_url:
            return jsonify({'success': False, 'error': 'Video upload to Cloudinary failed'}), 500

        # Return the video URL in the response
        return jsonify({
            'success': True,
            'video_url': video_url
        }), 200

    except Exception as e:
        error_message = f"Error in generate-video: {str(e)}"
        print(error_message)
        return jsonify({
            'success': False,
            'error': error_message
        }), 500
