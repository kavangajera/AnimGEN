from manim import *
import numpy as np
import random
import math

class PythagorasToCircle(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()
        
        # Pythagoras Equation
        a = 3
        b = 4
        c = math.sqrt(a**2 + b**2)
        
        square_a = Square(side_length=a, color=BLUE, fill_opacity=0.5)
        square_b = Square(side_length=b, color=GREEN, fill_opacity=0.5)
        square_c = Square(side_length=c, color=RED, fill_opacity=0.5)
        
        square_a.shift(LEFT * 2 + DOWN * 2)
        square_b.shift(RIGHT * 2 + DOWN * 2)
        square_c.shift(UP * 2)
        
        triangle = Polygon(
            square_a.get_corner(UR),
            square_b.get_corner(UL),
            square_c.get_corner(DL),
            fill_opacity=0.5,
            color=YELLOW
        )
        
        eq = MathTex(r"a^2 + b^2 = c^2", color=WHITE).scale(1.5).to_edge(DOWN)
        
        self.play(
            DrawBorderThenFill(square_a),
            DrawBorderThenFill(square_b),
            DrawBorderThenFill(square_c),
            run_time=2
        )
        self.play(Write(eq))
        self.play(FadeIn(triangle))
        self.wait(2)
        
        # Transition to Circle
        self.play(
            self.camera.frame.animate.scale(0.5).move_to(square_c),
            FadeOut(square_a), FadeOut(square_b), FadeOut(triangle), FadeOut(eq),
            run_time=2
        )
        
        circle = Circle(radius=c/2, color=RED, fill_opacity=0.5).move_to(square_c.get_center())
        self.play(Transform(square_c, circle), run_time=2)
        
        self.wait(2)