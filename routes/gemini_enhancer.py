# # from openai import OpenAI
# # from dotenv import load_dotenv
# # import os
# # from typing import Optional

# # def modify_prompt(prompt:str) -> Optional[str]:
# #     """
# #     Analyzes an image using the Gemini model via OpenRouter API.
    
# #     Args:
# #         image_url (str): URL of the image to analyze
        
# #     Returns:
# #         str: Description of the image content
# #         None: If there's an error during analysis
# #     """
# #     try:
# #         load_dotenv()
        
# #         client = OpenAI(
# #             base_url="https://openrouter.ai/api/v1",
# #             api_key=os.getenv("OPENROUTER_API_KEY"),
# #         )

# #         completion = client.chat.completions.create(
# #             model="google/gemini-2.0-pro-exp-02-05:free",
# #             messages=[
# #                 {
# #                     "role": "user",
# #                     "content": [
# #                         {
# #                             "type": "text",
# #                             "text": f"""This prompt : {prompt} is provided by user
                                    
# #                                     -Add more examples related to the prompt.
# #                                     -Add more details if not specified.
# #                                     -Add more ideas of animations from context of prompt.

# #                                     Also give step by step guide to make cool good 2d animations

# #                             """
# #                         }
# #                     ]
# #                 }
# #             ]
# #         )
        
# #         return completion.choices[0].message.content
        
# #     except Exception as e:
# #         print(f"Error Generating Prompt : {str(e)}")
# #         return None
    



# from flask import Flask, request, send_file, jsonify
# from flask_cors import CORS
# import os
# from pathlib import Path
# import cloudinary
# import cloudinary.uploader
# from cloudinary.utils import cloudinary_url
# from pymongo import MongoClient
# from datetime import datetime, timezone
# from pymongo.errors import ServerSelectionTimeoutError

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# # Configuration       
# cloudinary.config( 
#     cloud_name = "dseqb8ysp", 
#     api_key = "731827311222451", 
#     api_secret = "TpScp_HLrN07CDPwG6cDpaI4SDQ",
#     secure=True
# )

# # MongoDB Configuration and Initialization
# MONGO_URI = "mongodb+srv://ashishrathod53839:ashishashish@cluster1.vki9pld.mongodb.net/"

# def initialize_mongodb():
#     try:
#         # Connect with a timeout of 5 seconds
#         client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
#         # Test the connection
#         client.server_info()
        
#         # Create or get the database
#         db = client['video_database']
        
#         # Create or get the collection
#         if 'videos' not in db.list_collection_names():
#             # Create the collection with validation
#             db.create_collection('videos')
#             print("Videos collection created successfully")
            
#         videos_collection = db['videos']
        
#         # Create an index on timestamp for efficient sorting
#         videos_collection.create_index([("timestamp", -1)])
        
#         print("MongoDB initialized successfully")
#         return client, db, videos_collection
#     except ServerSelectionTimeoutError:
#         print("Could not connect to MongoDB server. Please check your connection string and internet connection.")
#         raise
#     except Exception as e:
#         print(f"Error initializing MongoDB: {str(e)}")
#         raise

# try:
#     client, db, videos_collection = initialize_mongodb()
# except Exception as e:
#     print(f"Failed to initialize MongoDB: {str(e)}")
#     # You might want to exit the application here depending on your requirements
#     # sys.exit(1)

# # Define the path where we'll store our sample video
# STATIC_FOLDER = Path(__file__).parent / 'static'
# SAMPLE_VIDEO_PATH = STATIC_FOLDER / 'sample.mp4'

# # Create the static folder if it doesn't exist
# STATIC_FOLDER.mkdir(exist_ok=True)

# def store_video_url(url, prompt):
#     """Store video URL and metadata in MongoDB"""
#     video_data = {
#         'url': url,
#         'prompt': prompt,
#         'timestamp': datetime.now(timezone.utc),
#         'status': 'completed'
#     }
#     return videos_collection.insert_one(video_data)

# @app.route('/generate-video', methods=['POST'])
# def generate_video():
#     try:
#         data = request.get_json()
#         prompt = data.get('prompt')
        
#         if not prompt:
#             return jsonify({'error': 'No prompt provided'}), 400

#         if not SAMPLE_VIDEO_PATH.exists():
#             return jsonify({'error': 'Sample video not found'}), 404

#         upload_result = cloudinary.uploader.upload(
#             SAMPLE_VIDEO_PATH,
#             public_id="sample",
#             resource_type="video"
#         )

#         video_url = upload_result["secure_url"]
        
#         try:
#             stored_video = store_video_url(video_url, prompt)
#             response_data = {
#                 'video_url': video_url,
#                 'video_id': str(stored_video.inserted_id)
#             }
#             return jsonify(response_data)
#         except Exception as db_error:
#             print(f"Database error: {str(db_error)}")
#             # Still return the video URL even if database storage fails
#             return jsonify({
#                 'video_url': video_url,
#                 'warning': 'Video generated but failed to save to history'
#             })

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# # @app.route('/videos', methods=['GET'])
# # def get_videos():
# #     try:
# #         # Check if the collection exists and has documents
# #         if 'videos' not in db.list_collection_names():
# #             return jsonify([])
            
# #         videos = list(videos_collection.find(
# #             {},
# #             {'_id': 1, 'url': 1, 'prompt': 1, 'timestamp': 1}
# #         ).sort('timestamp', -1).limit(10))
        
# #         if not videos:
# #             return jsonify([])
            
# #         for video in videos:
# #             video['_id'] = str(video['_id'])
# #             video['timestamp'] = video['timestamp'].isoformat()
            
# #         return jsonify(videos)
# #     except Exception as e:
# #         print(f"Error fetching videos: {str(e)}")
# #         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     if not SAMPLE_VIDEO_PATH.exists():
#         print(f"Warning: Please place a sample video file at {SAMPLE_VIDEO_PATH}")
#         print("The application will still run, but video generation will fail")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)