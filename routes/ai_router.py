from flask import Blueprint, request, jsonify
import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import routes.code_converter as code_converter
from cloudinary.uploader import upload as cloudinary_upload
import cloudinary
import ast

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

def extract_scene_name(python_file_path):
    """Extract the name of the Scene class from the Python file."""
    try:
        with open(python_file_path, 'r') as file:
            tree = ast.parse(file.read())
            
        # Look for class definitions that inherit from Scene or MovingCameraScene
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in ['Scene', 'MovingCameraScene']:
                        return node.name
        return None
    except Exception as e:
        print(f"Error extracting scene name: {str(e)}")
        return None

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

        # Extract the scene name from the Python file
        scene_name = extract_scene_name(manim_file_path)
        if not scene_name:
            return jsonify({'success': False, 'error': 'Could not determine scene name from generated code'}), 500

        print(f"Detected scene name: {scene_name}")

        # Generate the video using Manim
        output_directory = 'media'
        os.makedirs(output_directory, exist_ok=True)

        command = [
            'manim',
            '-pql',                    # Low quality (240p) preview
            '-r', '426,240',           # Set resolution to 240p
            '--media_dir', output_directory,
            manim_file_path
        ]

        # Run manim command
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Manim output:\n{process.stdout}")

        # Construct the expected video path using the scene name
        expected_video_path = os.path.join(
            output_directory,
            'videos',
            'temp_manim_script',
            '240p15',  # This is the resolution-specific subdirectory
            f"{scene_name}.mp4"
        )

        print(f"Looking for video at: {expected_video_path}")

        if not os.path.exists(expected_video_path):
            # If not found, try to find it by searching through the directory
            search_dir = os.path.join(output_directory, 'videos', 'temp_manim_script')
            found_files = []
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.endswith('.mp4') and scene_name in file:
                        found_files.append(os.path.join(root, file))
            
            if found_files:
                expected_video_path = found_files[0]
            else:
                return jsonify({
                    'success': False,
                    'error': 'Generated video not found',
                    'debug_info': {
                        'scene_name': scene_name,
                        'expected_path': expected_video_path,
                        'searched_directory': search_dir,
                        'found_files': found_files,
                        'manim_output': process.stdout,
                        'manim_errors': process.stderr if hasattr(process, 'stderr') else None
                    }
                }), 500

        # Upload the video to Cloudinary
        upload_result = cloudinary_upload(expected_video_path, resource_type='video')
        video_url = upload_result.get('url')

        if not video_url:
            return jsonify({'success': False, 'error': 'Video upload to Cloudinary failed'}), 500

        return jsonify({
            'success': True,
            'video_url': video_url,
            'video_path': expected_video_path
        }), 200

    except Exception as e:
        error_message = f"Error in generate-video: {str(e)}"
        print(error_message)
        return jsonify({
            'success': False,
            'error': error_message
        }), 500