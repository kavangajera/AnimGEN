from manim import *
import numpy as np
import random
import math

class EuclideanEquationToCircle(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()
        
        # Euclidean Equation
        euclidean_eq = MathTex(r"a^2 + b^2 = c^2", font_size=72)
        euclidean_eq.shift(UP * 2)
        
        self.play(Write(euclidean_eq))
        self.wait(1)
        
        # Transition to Circle
        circle = Circle(radius=2, color=BLUE)
        circle.shift(DOWN * 2)
        
        self.play(
            TransformMatchingTex(euclidean_eq, MathTex(r"x^2 + y^2 = r^2", font_size=72).shift(UP * 2)),
            self.camera.frame.animate.move_to(circle).scale(0.5)
        )
        self.wait(1)
        
        self.play(Create(circle))
        self.wait(2)
        
        # Highlighting parts of the circle
        radius_line = Line(circle.get_center(), circle.point_at_angle(0), color=YELLOW)
        radius_text = MathTex("r", color=YELLOW).next_to(radius_line, RIGHT)
        
        self.play(
            Create(radius_line),
            Write(radius_text)
        )
        self.wait(1)
        
        # Adding a point on the circle
        point_on_circle = Dot(circle.point_at_angle(PI/4), color=RED)
        x_line = Line(circle.get_center(), point_on_circle.get_center(), color=GREEN).set_opacity(0.5)
        y_line = x_line.copy().rotate(PI/2).set_color(ORANGE)
        
        self.play(
            FadeIn(point_on_circle),
            Create(x_line),
            Create(y_line)
        )
        self.wait(1)
        
        x_text = MathTex("x", color=GREEN).next_to(x_line, DOWN)
        y_text = MathTex("y", color=ORANGE).next_to(y_line, LEFT)
        
        self.play(
            Write(x_text),
            Write(y_text)
        )
        self.wait(2)