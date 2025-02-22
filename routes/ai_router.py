# routes/openai_router.py
# routes/ai_router.py
from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import httpx
from dotenv import load_dotenv
import routes.code_converter as code_converter

load_dotenv()
ai_routes = Blueprint('openai_routes', __name__)

# Create custom httpx client
http_client = httpx.Client(
    base_url="https://openrouter.ai/api/v1",
    headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Manim Animation Generator",
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"
    }
)

# Initialize OpenAI client with custom http client
client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    http_client=http_client
)

@ai_routes.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    try:
        data = request.json
        user_prompt = data.get('prompt')
        
        if not user_prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        completion = client.chat.completions.create(
            model="qwen/qwen2.5-vl-72b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
                                `You are an AI assistant that generates **high-quality, animated videos** using Manim. The output should resemble videos made by **3Blue1Brown**—clear, structured, visually engaging, and informative. Follow these strict guidelines:
                Write ONLY code for making manim ceanimation (NO EXPLAINATION) 
                ** dont use .svg files make them from scratch
                Take care of following things :
                - Make as many functions from scratch as possible
                - use new libraries as possible
                - Make only 1 Scene class if user prompts many scenes then merge it into one scene and then make longer code 
                - MathTex must have r"" and it must show proper equations
                - Don't write long sentenses given by user , break them and then explain them using shapes and animations and SHORT WORDS OR PHRASES
                IMP- Generate Manim CE code to display animations within a 16:9 aspect ratio screen (1920x1080). Keep all elements and animations within a central safe area of 1600x900 pixels, leaving a 10% margin on all sides. Avoid any text or graphics going beyond this region. Make text fonts and graph size accordingly . 

                - Use MovingCameraScene instead of Scene when you use Camera

                     

                     reference code :
                     from manim import *
                     import numpy as np
                     import random
                     import math
                           class MedicalDiagnosisScene(Scene):
                               def construct(self):
                                   # First, show "Real World Usage" alone
                                   initial_text = Text("Real World Usage", color="#90EE90").scale(0.7)
                                   initial_text.move_to(ORIGIN)

                                   # Show initial text
                                   self.play(Write(initial_text))
                                   self.wait(1)

                                   # Fade out initial text before showing the sequence
                                   self.play(FadeOut(initial_text))
                                   self.wait(0.5)

                                   # Create the three texts with proper spacing
                                   title1 = Text("Medical Diagnosis", color=BLUE).scale(0.7)
                                   title2 = Text("Real World Usage", color="#90EE90").scale(0.7)
                                   title3 = Text("Financial Risk Assessment", color="#FFA07A").scale(0.7)

                                   # Group and arrange them vertically
                                   text_group = VGroup(title1, title2, title3).arrange(DOWN, buff=1.5)
                                   text_group.move_to(ORIGIN)

                                   # Animate each text separately with proper timing
                                   self.play(FadeIn(title1), run_time=1)
                                   self.wait(0.5)

                                   self.play(FadeIn(title2), run_time=1)
                                   self.wait(0.5)

                                   self.play(FadeIn(title3), run_time=1)
                                   self.wait(2)
                  
                               
                                    
                                             
                                             
                              

                                always include this libraries in starting of the code:
                                manim , random , numpy , math

                                user's prompt :  {user_prompt}
           
                            """
                        },
                    ]
                }
            ]
        )

        ai_code = completion.choices[0].message.content

        print(f"AI code : \n{ai_code}","-"*20)

        manim_code = code_converter.extract_code_from_response(ai_code)

        print(f"Converted code:\n{manim_code}")

        return jsonify({
            'success': True,
            'code': manim_code
        })

    except Exception as e:
        print(f"Error in generate-prompt: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500