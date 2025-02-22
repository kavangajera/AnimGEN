from manim import *
import numpy as np
import random
import math

class HelloWorldScene(MovingCameraScene):
    def construct(self):
        # Define the safe area
        safe_area = Rectangle(width=16, height=9, color=WHITE).scale(0.5).set_stroke(width=2)
        safe_area.move_to(ORIGIN)

        # HELLO WORLD text
        hello_world = Text("HELLO WORLD", color=BLUE).scale(1.5)
        hello_world.move_to(ORIGIN)

        # Animate the text
        self.play(Write(hello_world))
        self.wait(1)

        # Break down HELLO WORLD into individual letters
        letters = VGroup(*[Text(char, color=BLUE).scale(1.5) for char in "HELLO WORLD"])
        letters.arrange(RIGHT, buff=0.5)
        letters.move_to(ORIGIN)

        # Animate the letters appearing one by one
        for letter in letters:
            self.play(FadeIn(letter), run_time=0.5)
            self.wait(0.1)

        self.wait(2)