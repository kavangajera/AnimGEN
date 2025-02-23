from manim import *
import numpy as np
import random
import math

class PythagorasToCircle(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()
        
        # Pythagoras Theorem
        a = 3
        b = 4
        c = math.sqrt(a**2 + b**2)
        
        square_a = Square(side_length=a, color=BLUE, fill_opacity=0.5)
        square_b = Square(side_length=b, color=GREEN, fill_opacity=0.5)
        square_c = Square(side_length=c, color=RED, fill_opacity=0.5)
        
        square_a.shift(LEFT * (b / 2) + DOWN * (a / 2))
        square_b.shift(RIGHT * (a / 2) + DOWN * (b / 2))
        square_c.shift(UP * (c / 2))
        
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
        self.wait()
        
        # Transition to Circle
        self.play(
            self.camera.frame.animate.scale(0.5).move_to(square_c.get_center()),
            FadeOut(square_a), FadeOut(square_b), FadeOut(eq),
            run_time=2
        )
        
        circle = Circle(radius=c/2, color=RED, fill_opacity=0.5)
        self.play(Transform(square_c, circle), run_time=2)
        self.wait()
        
        # Circle Graph
        axes = Axes(
            x_range=[-c, c, 1],
            y_range=[-c, c, 1],
            x_length=6,
            y_length=6,
            axis_config={"color": WHITE},
            tips=False,
        ).move_to(circle.get_center())
        
        circle_graph = Circle(radius=c/2, color=RED, fill_opacity=0.5)
        self.play(
            self.camera.frame.animate.scale(2).move_to(circle.get_center()),
            Transform(circle, circle_graph),
            FadeIn(axes),
            run_time=2
        )
        self.wait()