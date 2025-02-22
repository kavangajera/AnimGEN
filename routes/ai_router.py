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
                Take care of following things :
                - Make as many functions from scratch as possible
                - Make only 1 Scene class if user prompts many scenes then merge it into one scene and then make longer code 
                - MathTex must have r"" and it must show proper equations
                - Don't write long sentenses given by user , break them and then explain them using shapes and animations and SHORT WORDS OR PHRASES
                IMP- Generate Manim CE code to display animations within a 16:9 aspect ratio screen (1920x1080). Keep all elements and animations within a central safe area of 1600x900 pixels, leaving a 10% margin on all sides. Avoid any text or graphics going beyond this region. Make text fonts and graph size accordingly . 

                - Use MovingCameraScene instead of Scene when you use Camera
                 **USE methods STRICTLY from this list ONLY:
                # Manim 0.19.0 Methods Reference

                     ## Animation Methods
                     - Create
                     - Write
                     - FadeIn
                     - FadeOut
                     - GrowFromCenter
                     - GrowFromPoint
                     - GrowFromEdge
                     - ShrinkToCenter
                     - Uncreate
                     - DrawBorderThenFill
                     - ShowPassingFlash
                     - ShowPartial
                     - AnimationGroup
                     - Succession
                     - LaggedStart 
                     - Transform
                     - ReplacementTransform
                     - MoveToTarget
                     - ApplyMethod
                     - ApplyFunction
                     - ScaleInPlace
                     - Restore
                     - ApplyPointwiseFunction
                     - ApplyMatrix
                     - CyclicReplace
                     - Rotate
                     - RotateAround
                     - Rotating
                     - FlipAroundPoint
                     - MoveAlongPath
                     - ParametricFunction
                     - CounterclockwiseTransform

                     ## Mobject Creation/Modification
                     - add
                     - remove
                     - become
                     - align_to
                     - arrange
                     - arrange_in_grid
                     - center
                     - flip
                     - generate_target
                     - move_to
                     - next_to
                     - rotate
                     - scale
                     - set_color
                     - set_fill
                     - set_stroke
                     - set_style
                     - shift
                     - stretch
                     - surround
                     - to_corner
                     - to_edge
                     - update

                     ## Shape Methods
                     - Circle
                     - Dot
                     - Square
                     - Rectangle
                     - RoundedRectangle
                     - Polygon
                     - RegularPolygon
                     - Triangle
                     - Line
                     - DashedLine
                     - Arrow
                     - DoubleArrow
                     - Vector
                     - CurvedArrow
                     - CurvedDoubleArrow
                     - Arc
                     - ArcBetweenPoints
                     - CurvedLine
                     - Ellipse
                     - Sector
                     - Annulus
                     - AnnularSector

                     ## Text Methods
                     - Text
                     - Tex
                     - MathTex
                     - TexText
                     - BulletedList
                     - NumberedList
                     - Code
                     - Table
                     - MathTable
                     - DecimalNumber
                     - Integer
                     - Variable
                     - SingleStringMathTex

                     ## Graphing Methods
                     - Axes
                     - NumberLine
                     - NumberPlane
                     - ComplexPlane
                     - CoordinateSystem
                     - ParametricFunction
                     - ImplicitFunction
                     - FunctionGraph
                     - ScatterPlot
                     - BarChart
                     - PieChart
                     - LineGraph
                     - DotPlot
                     - Histogram
                     - PointCloudDot
                     - SurfaceObject



                     ## Color Methods
                     - set_color
                     - set_color_by_gradient
                     - set_colors_by_radial_gradient
                     - set_submobject_colors_by_gradient
                     - fade
                     - fade_to
                     - set_opacity
                     - get_color
                     - invert
                     - lighten
                     - darken

                     ## Group Methods
                     - VGroup
                     - VMobject
                     - Group
                     - gather
                     - arrange_submobjects
                     - sort_submobjects
                     - shuffle_submobjects
                     - invert_submobject_order
                     - add_to_back
                     - bring_to_front
                     - bring_to_back

                     ## Path Methods
                     - get_path
                     - get_points
                     - get_start
                     - get_end 
                     - get_center
                     - get_anchors
                     - get_arc_length
                     - point_from_proportion
                     - proportion_from_point
                     - get_subcurve
                     - get_direction
                     - get_unit_normal
                     - get_tangent

                     ## 3D Methods
                     - Sphere
                     - Cube
                     - Prism
                     - Cylinder
                     - Cone
                     - Torus
                     - Surface
                     - ParametricSurface
                     - ThreeDVMobject
                     - ThreeDScene
                     - ThreeDCamera

                     ## Transform Methods
                     - apply_complex_function
                     - apply_function
                     - apply_matrix
                     - apply_about_point
                     - apply_over_time_interval
                     - apply_to_family
                     - match_style
                     - match_height
                     - match_width
                     - match_depth
                     - match_dim_size
                     - match_points

                     ## Position/Layout Methods
                     - get_critical_point
                     - get_edge_center
                     - get_corner
                     - get_center_of_mass
                     - get_boundary_point
                     - get_top
                     - get_bottom
                     - get_left
                     - get_right
                     - get_zenith
                     - get_nadir

                     ## Utility Methods
                     - save_image
                     - save_state
                     - update_config
                     - digest_config
                     - suspend_updating
                     - resume_updating
                     - get_time
                     - get_run_time
                     - get_animation_time
                     - wait
                     - play
                     - begin_ambient_camera_rotation
                     - stop_ambient_camera_rotation

                     ## Rate Functions
                     - linear
                     - smooth
                     - rush_into
                     - rush_from
                     - slow_into
                     - double_smooth
                     - there_and_back
                     - there_and_back_with_pause
                     - running_start
                     - wiggle

                     ## Interactive Methods
                     - add_mouse_press_listner
                     - add_key_press_handler
                     - add_mouse_scroll_listner
                     - add_update_function
                     - remove_update_function
                     - clear_update_functions
                     - add_foreground_mobject
                     - add_foreground_mobjects
                     - remove_foreground_mobject

                     ## Container Methods
                     - add_background_mobject
                     - add_foreground_mobject
                     - bring_to_back
                     - bring_to_front
                     - remove_updater
                     - add_updater
                     - get_updaters
                     - update

                     ## Additional Utility Methods
                     - deepcopy
                     - copy
                     - generate_points
                     - init_points
                     - reset_points
                     - clear_points
                     - get_all_points
                     - has_points
                     - get_num_points
                     - get_point_mobject
                     - interpolate
                     - pointwise_become_partial
                     - repeat
                     - reverse_points
                     - set_points
                     - set_points_as_corners
                     - set_points_smoothly

                     =>At last conquer on this two issues - 1) Overlapping of texts 2) Text and animations going out of screen

                     1. Screen Boundary Control:
                        - Set initial position to ORIGIN
                        - Scale all text to 0.7 or smaller
                        - Keep vertical positions between -4 and 4
                        - Keep horizontal positions between -7 and 7
                        - Set font_size=30 for all text
                        - Break long text into multiple lines

                     2. Overlap Prevention:
                        - Use VGroup() for all related elements
                        - Set minimum buff=1.0 in arrange() and next_to()
                        - Assign increasing z_index for overlapping elements
                        - Add wait(1) between transitions
                        - Clear previous elements using FadeOut when needed

                     3. Animation Flow:
                        - Start each major section from ORIGIN
                        - Move elements using relative positioning (next_to, arrange)
                        - Use shift() only with specific calculated distances
                        - Group related animations with AnimationGroup(lag_ratio=0.5)

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
                  
                                   
                                user's prompt : 
                                always include this libraries in starting of the code:
                                from manim import *
                                import numpy as np
                                import random
                                import math
                                {user_prompt}
           
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