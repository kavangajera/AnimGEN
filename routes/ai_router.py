# routes/openai_router.py
from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
import routes.code_converter as code_converter

load_dotenv()
ai_routes = Blueprint('openai_routes', __name__)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY')
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

                     ** use this when MULTIPLE TEXT AFTER TEXT ARE RENDERING Example positioning:
                     - First element: move_to(ORIGIN)
                     - Second element: next_to(first, DOWN, buff=1)
                     - Third element: arrange(DOWN, buff=1)

                     Please test all coordinates and ensure nothing extends beyond (-7,4) to (7,4) range."

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
                  
                                **TAKE THIS REFERENCE CODE IN THE CONSIDERATION for function usage only (DONT TAKE ANY LOGIN TO CONSIDER):
                                     from manim import *
                                     import numpy as np
                                     import random
                                     import math
                                     
                                     class NeuralNetworkExplanation(MovingCameraScene):
                                         def construct(self):
                                             # Scene 1: Introduction
                                             title = Text("What is a Neural Network?", color=BLUE).scale(0.7)
                                             title.move_to(ORIGIN)
                                             self.play(Write(title))
                                             self.wait(1)
                                     
                                             brain = self.create_brain()
                                             neural_network = self.create_neural_network()
                                             
                                             brain.move_to(LEFT * 4)
                                             neural_network.move_to(RIGHT * 4)
                                             
                                             self.play(FadeIn(brain), FadeIn(neural_network))
                                             self.wait(1)
                                     
                                             analogy_text = Text("Neural Networks: Learning Like a Brain", color=GREEN).scale(0.7)
                                             analogy_text.next_to(title, DOWN, buff=1)
                                             self.play(Write(analogy_text))
                                             self.wait(2)
                                     
                                             self.play(
                                                 FadeOut(title), 
                                                 FadeOut(analogy_text), 
                                                 FadeOut(brain), 
                                                 FadeOut(neural_network)
                                             )
                                             self.wait(0.5)
                                     
                                             # Scene 2: Building Blocks
                                             building_blocks_title = Text("Building Blocks of Neural Networks", color=BLUE).scale(0.7)
                                             building_blocks_title.move_to(UP * 3)
                                             self.play(Write(building_blocks_title))
                                             self.wait(1)
                                     
                                             # Create layers
                                             input_layer = self.create_layer("Input Layer", 4, RED, LEFT * 4)
                                             hidden_layer = self.create_layer("Hidden Layer", 3, GREEN, ORIGIN)
                                             output_layer = self.create_layer("Output Layer", 2, BLUE, RIGHT * 4)
                                     
                                             # Show layers one by one
                                             self.play(FadeIn(input_layer))
                                             self.wait(0.5)
                                             self.play(FadeIn(hidden_layer))
                                             self.wait(0.5)
                                             self.play(FadeIn(output_layer))
                                             self.wait(1)
                                     
                                             # Connect layers
                                             connections = self.create_connections(
                                                 [input_layer, hidden_layer, output_layer]
                                             )
                                             self.play(Create(connections))
                                             self.wait(2)
                                     
                                             self.play(
                                                 FadeOut(building_blocks_title),
                                                 FadeOut(input_layer),
                                                 FadeOut(hidden_layer),
                                                 FadeOut(output_layer),
                                                 FadeOut(connections)
                                             )
                                             self.wait(0.5)
                                     
                                             # Scene 3: Data Flow
                                             data_flow_title = Text("How Data Flows Through the Network", color=BLUE).scale(0.7)
                                             data_flow_title.move_to(UP * 3)
                                             self.play(Write(data_flow_title))
                                             self.wait(1)
                                     
                                             # Recreate network for data flow demonstration
                                             input_layer = self.create_layer("Input Layer", 4, RED, LEFT * 4)
                                             hidden_layer = self.create_layer("Hidden Layer", 3, GREEN, ORIGIN)
                                             output_layer = self.create_layer("Output Layer", 2, BLUE, RIGHT * 4)
                                             connections = self.create_connections([input_layer, hidden_layer, output_layer])
                                     
                                             self.play(
                                                 FadeIn(input_layer),
                                                 FadeIn(hidden_layer),
                                                 FadeIn(output_layer),
                                                 Create(connections)
                                             )
                                     
                                             # Animate data flow
                                             self.animate_data_flow(input_layer, hidden_layer, output_layer)
                                             self.wait(2)
                                     
                                             self.play(
                                                 FadeOut(data_flow_title),
                                                 FadeOut(input_layer),
                                                 FadeOut(hidden_layer),
                                                 FadeOut(output_layer),
                                                 FadeOut(connections)
                                             )
                                             self.wait(0.5)
                                     
                                             # Scene 4: Learning Process
                                             learning_title = Text("How Neural Networks Learn", color=BLUE).scale(0.7)
                                             learning_title.move_to(UP * 3)
                                             self.play(Write(learning_title))
                                             self.wait(1)
                                     
                                             # Create network for learning demonstration
                                             input_layer = self.create_layer("Input Layer", 4, RED, LEFT * 4)
                                             hidden_layer = self.create_layer("Hidden Layer", 3, GREEN, ORIGIN)
                                             output_layer = self.create_layer("Output Layer", 2, BLUE, RIGHT * 4)
                                             connections = self.create_connections([input_layer, hidden_layer, output_layer])
                                     
                                             self.play(
                                                 FadeIn(input_layer),
                                                 FadeIn(hidden_layer),
                                                 FadeIn(output_layer),
                                                 Create(connections)
                                             )
                                     
                                             # Animate learning process
                                             self.animate_learning_process(connections)
                                             self.wait(2)
                                     
                                             self.play(
                                                 FadeOut(learning_title),
                                                 FadeOut(input_layer),
                                                 FadeOut(hidden_layer),
                                                 FadeOut(output_layer),
                                                 FadeOut(connections)
                                             )
                                             self.wait(0.5)
                                     
                                             # Scene 5: Example Application
                                             example_title = Text("Example: Image Recognition", color=BLUE).scale(0.7)
                                             example_title.move_to(UP * 3)
                                             self.play(Write(example_title))
                                             self.wait(1)
                                     
                                             # Create image and network
                                             input_image = self.create_smile_image()
                                             input_image.move_to(LEFT * 4)
                                             
                                             input_layer = self.create_layer("Input Layer", 4, RED, LEFT * 2)
                                             hidden_layer = self.create_layer("Hidden Layer", 3, GREEN, RIGHT * 2)
                                             output_layer = self.create_layer("Output Layer", 2, BLUE, RIGHT * 4)
                                             connections = self.create_connections([input_layer, hidden_layer, output_layer])
                                     
                                             self.play(
                                                 FadeIn(input_image),
                                                 FadeIn(input_layer),
                                                 FadeIn(hidden_layer),
                                                 FadeIn(output_layer),
                                                 Create(connections)
                                             )
                                     
                                             # Animate recognition process
                                             self.animate_image_recognition(input_layer, hidden_layer, output_layer)
                                             self.wait(2)
                                     
                                             # Final fadeout
                                             self.play(
                                                 FadeOut(example_title),
                                                 FadeOut(input_image),
                                                 FadeOut(input_layer),
                                                 FadeOut(hidden_layer),
                                                 FadeOut(output_layer),
                                                 FadeOut(connections)
                                             )
                                             self.wait(1)
                                     
                                         def create_brain(self):
                                             brain = VGroup()
                                             
                                             # Main brain shape
                                             main_shape = VGroup()
                                             
                                             # Create hemispheres using correct CubicBezier parameters
                                             left_curve = CubicBezier(
                                                 start_anchor=np.array([-1, -1, 0]),
                                                 start_handle=np.array([-1.5, 0, 0]),
                                                 end_handle=np.array([-1.5, 1, 0]),
                                                 end_anchor=np.array([-1, 1, 0])
                                             )
                                             
                                             right_curve = CubicBezier(
                                                 start_anchor=np.array([1, -1, 0]),
                                                 start_handle=np.array([1.5, 0, 0]),
                                                 end_handle=np.array([1.5, 1, 0]),
                                                 end_anchor=np.array([1, 1, 0])
                                             )
                                             
                                             top_curve = CubicBezier(
                                                 start_anchor=left_curve.get_end(),
                                                 start_handle=np.array([-0.5, 1.2, 0]),
                                                 end_handle=np.array([0.5, 1.2, 0]),
                                                 end_anchor=right_curve.get_end()
                                             )
                                             
                                             bottom_curve = CubicBezier(
                                                 start_anchor=left_curve.get_start(),
                                                 start_handle=np.array([-0.5, -1.2, 0]),
                                                 end_handle=np.array([0.5, -1.2, 0]),
                                                 end_anchor=right_curve.get_start()
                                             )
                                             
                                             main_shape.add(left_curve, right_curve, top_curve, bottom_curve)
                                             
                                             # Add brain folds with correct CubicBezier parameters
                                             for i in range(6):
                                                 y_pos = -0.8 + (1.6 * i / 5)
                                                 fold = CubicBezier(
                                                     start_anchor=np.array([-0.8, y_pos, 0]),
                                                     start_handle=np.array([-0.3, y_pos + 0.2, 0]),
                                                     end_handle=np.array([0.3, y_pos - 0.2, 0]),
                                                     end_anchor=np.array([0.8, y_pos, 0])
                                                 )
                                                 main_shape.add(fold)
                                             
                                             brain.add(main_shape)
                                             brain.set_stroke(color=BLUE_D, width=2)
                                             brain.set_fill(color=BLUE_E, opacity=0.3)
                                             
                                             return brain
                                     
                                         def create_neural_network(self):
                                             network = VGroup()
                                             layer_sizes = [4, 3, 2]
                                             x_spacing = 1.5
                                             
                                             layers = []
                                             for i, size in enumerate(layer_sizes):
                                                 layer = VGroup()
                                                 for j in range(size):
                                                     neuron = Circle(radius=0.2)
                                                     neuron.set_fill(WHITE, opacity=0.5)
                                                     neuron.set_stroke(WHITE, width=2)
                                                     neuron.move_to([i * x_spacing, (j - (size-1)/2), 0])
                                                     layer.add(neuron)
                                                 layers.append(layer)
                                                 network.add(layer)
                                             
                                             # Add connections
                                             for i in range(len(layers)-1):
                                                 for n1 in layers[i]:
                                                     for n2 in layers[i+1]:
                                                         connection = Line(
                                                             n1.get_center(),
                                                             n2.get_center(),
                                                             stroke_width=1,
                                                             stroke_opacity=0.5
                                                         )
                                                         network.add(connection)
                                             
                                             return network
                                     
                                         def create_layer(self, label, num_neurons, color, position):
                                             layer = VGroup()
                                             
                                             # Create neurons
                                             neurons = VGroup()
                                             for i in range(num_neurons):
                                                 neuron = Circle(radius=0.2)
                                                 neuron.set_fill(color, opacity=0.3)
                                                 neuron.set_stroke(color, width=2)
                                                 neuron.move_to([0, (i - (num_neurons-1)/2), 0])
                                                 neurons.add(neuron)
                                             
                                             # Add label
                                             label = Text(label, color=color).scale(0.4)
                                             label.next_to(neurons, DOWN, buff=0.5)
                                             
                                             layer.add(neurons, label)
                                             layer.move_to(position)
                                             return layer
                                     
                                         def create_connections(self, layers):
                                             connections = VGroup()
                                             for i in range(len(layers)-1):
                                                 layer1 = layers[i][0]  # Get neurons VGroup (first element of layer)
                                                 layer2 = layers[i+1][0]
                                                 for n1 in layer1:
                                                     for n2 in layer2:
                                                         connection = Line(
                                                             n1.get_center(),
                                                             n2.get_center(),
                                                             stroke_width=1,
                                                             stroke_opacity=0.5
                                                         )
                                                         connections.add(connection)
                                             return connections
                                     
                                         def animate_data_flow(self, input_layer, hidden_layer, output_layer):
                                             data = Dot(color=YELLOW, radius=0.1)
                                             data.move_to(input_layer[0][0].get_center())  # Start at first neuron of input layer
                                             
                                             # Highlight path through network
                                             self.play(FadeIn(data))
                                             for layer in [hidden_layer, output_layer]:
                                                 self.play(
                                                     data.animate.move_to(layer[0][0].get_center()),
                                                     run_time=1
                                                 )
                                             self.play(FadeOut(data))
                                     
                                         def animate_learning_process(self, connections):
                                             # Show error
                                             error_text = Text("Error Detected!", color=RED).scale(0.6)
                                             error_text.to_edge(UP)
                                             self.play(Write(error_text))
                                             
                                             # Highlight connections being updated
                                             self.play(
                                                 connections.animate.set_color(YELLOW),
                                                 run_time=2
                                             )
                                             self.play(
                                                 connections.animate.set_color(WHITE),
                                                 FadeOut(error_text)
                                             )
                                     
                                         def create_smile_image(self):
                                             smile = VGroup()
                                             
                                             # Face circle
                                             face = Circle(radius=1, color=YELLOW)
                                             face.set_fill(YELLOW, opacity=0.3)
                                             
                                             # Eyes
                                             left_eye = Dot(point=[-0.3, 0.2, 0], color=BLACK)
                                             right_eye = Dot(point=[0.3, 0.2, 0], color=BLACK)
                                             
                                             # Smile
                                             smile_curve = ArcBetweenPoints(
                                                 start=np.array([-0.5, -0.2, 0]),
                                                 end=np.array([0.5, -0.2, 0]),
                                                 angle=PI/2
                                             )
                                             
                                             smile.add(face, left_eye, right_eye, smile_curve)
                                             return smile
                                     
                                         def animate_image_recognition(self, input_layer, hidden_layer, output_layer):
                                             # Animate recognition process
                                             result_text = Text("Recognized: Smiley Face", color=GREEN).scale(0.6)
                                             result_text.to_edge(UP)
                                             
                                             data = Dot(color=YELLOW, radius=0.1)
                                             data.move_to(input_layer[0][0].get_center())
                                             
                                             self.play(FadeIn(data))
                                             self.play(
                                                 data.animate.move_to(hidden_layer[0][0].get_center()),
                                                 run_time=1
                                             )
                                             self.play(
                                                 data.animate.move_to(output_layer[0][0].get_center()),
                                                 run_time=1
                                             )
                                             self.play(
                                                 FadeOut(data),
                                                 Write(result_text)
                                             )
                                             self.wait(1)
                                             self.play(FadeOut(result_text))
                              

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

        manim_code = code_converter.extract_code_from_response(ai_code)

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