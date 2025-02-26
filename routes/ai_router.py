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
        videos_collection = db.videos
        
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

def extract_scene_name(python_file_path):
    """Extract the name of the Scene class from the Python file."""
    try:
        with open(python_file_path, 'r') as file:
            tree = ast.parse(file.read())
            
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

                    ** Please use shapes classes in this form only : 
                    Here's a brief definition of the common shape functions in Manim CE and their required parameters:

                        Circle

                        Required: None
                        Optional: radius, color, stroke_width
                        Example: Circle(radius=2, color=RED)


                        Square

                        Required: None
                        Optional: side_length, color
                        Example: Square(side_length=2, color=GREEN)


                        Rectangle

                        Required: None
                        Optional: width, height, color
                        Example: Rectangle(width=4, height=2, color=BLUE)


                        Triangle

                        Use Polygon with 3 points
                        Example: Polygon([-1,0,0], [1,0,0], [0,1,0], color=YELLOW)


                        RegularPolygon

                        Required: n (number of sides)
                        Optional: radius (NOT side_length), color
                        Example: RegularPolygon(n=5, radius=2, color=TEAL)


                        Polygon

                        Required: At least 3 points (as arrays)
                        Optional: color
                        Example: Polygon([0,0,0], [1,0,0], [0,1,0], color=PURPLE)


                        Ellipse

                        Required: None
                        Optional: width, height, color
                        Example: Ellipse(width=4, height=2, color=PINK)


                        Line

                        Required: start, end (as points)
                        Optional: color, stroke_width
                        Example: Line([0,0,0], [1,1,0], color=WHITE)


                        Arc

                        Required: None
                        Optional: radius, angle, start_angle, color
                        Example: Arc(radius=2, angle=PI/2, color=ORANGE)


                        Dot

                        Required: None
                        Optional: point, radius, color
                        Example: Dot(point=[0,0,0], radius=0.1, color=RED)

                    **

                    ** Make smooth transitions from slide to slide (Shapes to shapes to text etc)
                    ** Dont make all shapes or text in one slide ** First clear the area and then make animation at that place

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
        manim_file_path = 'temp_manim_script.py'
        with open(manim_file_path, 'w') as f:
            f.write(manim_code)

        scene_name = extract_scene_name(manim_file_path)
        if not scene_name:
            return jsonify({'error': 'Could not determine scene name from generated code'}), 500

        print(f"Detected scene name: {scene_name}")

        # Setup output directory
        output_directory = 'media'
        os.makedirs(output_directory, exist_ok=True)

        # Generate video with Manim
        command = [
            'manim',
            '-pql',                    # Low quality (240p) preview
            '-r', '426,240',           # Set resolution to 240p
            '--media_dir', output_directory,
            manim_file_path
        ]

        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Manim output:\n{process.stdout}")

        # Find generated video
        expected_video_path = os.path.join(
            output_directory,
            'videos',
            'temp_manim_script',
            '240p15',
            f"{scene_name}.mp4"
        )

        print(f"Looking for video at: {expected_video_path}")

        if not os.path.exists(expected_video_path):
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
            if os.path.exists('media'):
                shutil.rmtree('media')
            if os.path.exists('temp_manim_script.py'):
                os.remove('temp_manim_script.py')
                
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

@ai_routes.route('/videos', methods=['GET'])
def get_videos():
    try:
        # Get the all videos
        videos = list(videos_collection.find(
            {},
            {'_id': 1, 'url': 1, 'prompt': 1, 'timestamp': 1}
        ).sort('timestamp', -1))
        
        # Format the response
        for video in videos:
            video['_id'] = str(video['_id'])
            video['timestamp'] = video['timestamp'].isoformat()
            
        return jsonify(videos)
    except Exception as e:
        print(f"Error fetching videos: {str(e)}")
        return jsonify({'error': str(e)}), 500