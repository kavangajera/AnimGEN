from flask import Blueprint, request, jsonify
import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import routes.code_converter as code_converter
from cloudinary.uploader import upload as cloudinary_upload
import cloudinary
import ast
import shutil
from pymongo import MongoClient
from datetime import datetime, timezone
from pymongo.errors import ServerSelectionTimeoutError
import routes.audio_video as audio_video
import routes.gemini_enhancer as gemini_enhancer

load_dotenv()

pro_routes = Blueprint('pro_routes', __name__)

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

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
mongodb_client = None
db = None
videos_collection = None

def initialize_mongodb():
    """Initialize MongoDB connection and return client, db, and collection"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        
        db = client['video_database']
        videos_collection = db.pro_videos
        
        # Create index for efficient timestamp-based sorting
        videos_collection.create_index([("timestamp", -1)])
        
        print("MongoDB initialized successfully")
        return client, db, videos_collection
    except ServerSelectionTimeoutError:
        print("Could not connect to MongoDB server. Check connection string and internet connection.")
        raise
    except Exception as e:
        print(f"Error initializing MongoDB: {str(e)}")
        raise

# Initialize MongoDB connection
try:
    mongodb_client, db, videos_collection = initialize_mongodb()
except Exception as e:
    print(f"Failed to initialize MongoDB: {str(e)}")

def store_video_url(videos_collection, url, prompt):
    """Store video URL and metadata in MongoDB"""
    try:
        video_data = {
            'url': url,
            'prompt': prompt,
            'timestamp': datetime.now(timezone.utc),
            'status': 'completed'
        }
        result = videos_collection.insert_one(video_data)
        return result
    except Exception as e:
        print(f"Error storing video URL: {str(e)}")
        raise



@pro_routes.route('/generate-pro-video', methods=['POST'])
def generate_pro_video():
    try:
        data = request.json
        user_prompt = data.get('prompt', '').strip()
        script = gemini_enhancer.parse_script_string(user_prompt)
        user_prompt = f"Prompt:  {user_prompt}  \n  Array:  {script}"
        
        if not user_prompt:
            return jsonify({'error': 'No prompt provided'}), 400

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
                    - Utilize the screen and make sure the content of video remains within the sceen.
                    - Avoid overlapping and ghosting of texts and animations of graph and shapes to avoid mess
                    ** AVOID --> errors of MObject like : Mobject.__init__() got an unexpected keyword argument 'side_length'
                    **Required Libraries:** 
                    ```python
                    from manim import *
                    import numpy as np
                    import random
                    import math
                    ```

                    **User's prompt:** {user_prompt}
                    ** user prompt includes one Array make animations as per that array and also consider user's abstract Prompt
                """
            }
        ]

        # Get completion from OpenAI
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=messages
        )

        ai_code = completion.choices[0].message.content.strip()
        print(f"AI Generated Code:\n{ai_code}\n{'-'*40}")

        manim_code = code_converter.extract_code_from_response(ai_code)
        print(f"Converted Manim Code:\n{manim_code}\n{'-'*40}")

        # Save code to temporary file
        
        scene_name = audio_video.extract_scene_name_from_strcode(manim_code)
       

        audio_video.generate_manim_video_with_voiceover(
        manim_code_string=manim_code,
        audio_script=script,
        scene_class_name=scene_name
    ) 
        
        expected_video_path = "./manim_video_output/manim_with_voiceover.mp4" 

        # Upload to Cloudinary
        upload_result = cloudinary_upload(expected_video_path, resource_type='video')
        video_url = upload_result.get('url')

        if not video_url:
            return jsonify({'error': 'Video upload to Cloudinary failed'}), 500

        try:
            stored_video = store_video_url(videos_collection, video_url, user_prompt)
            response_data = {
                'video_url': video_url,
                'video_id': str(stored_video.inserted_id)
            }
            
            # Clean up files
            
                
            return jsonify(response_data)
            
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            return jsonify({
                'video_url': video_url,
                'warning': 'Video generated but failed to save to history'
            })

    except Exception as e:
        error_message = f"Error in generate-video: {str(e)}"
        print(error_message)
        return jsonify({'error': error_message}), 500

