import os
import sys
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
import importlib.util
from gtts import gTTS
import numpy as np
import ast

def generate_manim_video_with_voiceover(manim_code_string, audio_script, 
                                        output_directory="manim_video_output", 
                                        final_video_name="manim_with_voiceover.mp4",
                                        scene_class_name=None,
                                        verbose=True):
    """
    Generate a Manim animation with synchronized voiceover at 240p with low audio quality.
    
    Parameters:
    -----------
    manim_code_string : str
        String containing the Manim code with Scene class definition
    audio_script : list
        List of strings for the voiceover script, each item will be a separate audio segment
    output_directory : str
        Directory to save the final video
    final_video_name : str
        Name of the final video file
    scene_class_name : str, optional
        Name of the Scene class to render. If None, tries to detect it automatically.
    verbose : bool
        Whether to print verbose log messages
        
    Returns:
    --------
    str
        Path to the final video
    """
    # Create a temporary directory for working files
    tmp_dir = tempfile.mkdtemp()
    
    if verbose:
        print(f"[INFO] Working in temporary directory: {tmp_dir}")
    
    try:
        # Step 1: Extract scene class name if not provided
        if scene_class_name is None:
            # Try to find class that inherits from Scene
            class_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', manim_code_string)
            if class_match:
                scene_class_name = class_match.group(1)
            else:
                raise ValueError("Could not detect Scene class name. Please provide scene_class_name parameter.")
        
        if verbose:
            print(f"[INFO] Using scene class: {scene_class_name}")
        
        # Step 2: Create audio files from script
        audio_paths, audio_durations = create_audio_files(audio_script, tmp_dir, verbose)
        
        # Step 3: Modify manim code to use lower quality settings
        manim_code_string = add_quality_settings(manim_code_string)
        
        # Step 4: Save Manim code to a temporary file
        module_path = os.path.join(tmp_dir, "manim_scene.py")
        with open(module_path, 'w') as f:
            f.write(manim_code_string)
        
        # Step 5: Load the Manim scene as a module
        spec = importlib.util.spec_from_file_location("manim_scene", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Step 6: Create a modified scene class with timings
        scene_class = getattr(module, scene_class_name)
        TimedScene = create_timed_scene_class(scene_class, audio_durations, verbose)
        
        # Step 7: Render the scene with low quality settings
        video_path = render_scene(TimedScene, tmp_dir, verbose, quality="low")
        
        # Step 8: Concatenate all audio files
        full_audio_path = os.path.join(tmp_dir, "full_audio.mp3")
        concatenate_audio_files(audio_paths, full_audio_path, verbose)
        
        # Step 9: Merge audio and video with low quality settings
        os.makedirs(output_directory, exist_ok=True)
        output_path = os.path.join(output_directory, final_video_name)
        final_video = merge_audio_and_video(video_path, full_audio_path, output_path, verbose, quality="240p")
        
        if verbose:
            print(f"[INFO] Successfully created video at: {final_video}")
        
        return final_video
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise
    finally:
        # Clean up temporary files
        if verbose:
            print(f"[INFO] Cleaning up temporary files")
        try:
            shutil.rmtree(tmp_dir)
        except:
            pass

def add_quality_settings(manim_code):
    """Add low quality settings to the manim code"""
    # Add config settings for low quality if not already present
    if "config" not in manim_code and "from manim import *" in manim_code:
        setup_code = """
from manim import *

# Set low quality config
config.pixel_height = 240
config.pixel_width = 426
config.frame_rate = 15
"""
        return setup_code + manim_code.replace("from manim import *", "")
    return manim_code

def create_audio_files(script, tmp_dir, verbose=True):
    """Create audio files for each segment of the voiceover script with low quality"""
    if verbose:
        print("[INFO] Creating voiceover audio files...")
    
    audio_paths = []
    audio_durations = []
    audio_dir = os.path.join(tmp_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    for i, text in enumerate(script):
        audio_path = os.path.join(audio_dir, f"segment_{i+1:02d}.mp3")
        if verbose:
            print(f"[INFO] Generating segment {i+1}: {text[:30]}...")
        
        # Generate audio with gTTS
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(audio_path)
        
        # Compress audio to lower quality
        compressed_path = os.path.join(audio_dir, f"compressed_{i+1:02d}.mp3")
        compress_audio(audio_path, compressed_path, verbose)
        
        # Get duration
        duration = get_audio_duration(compressed_path)
        audio_durations.append(duration)
        audio_paths.append(compressed_path)
    
    if verbose:
        print(f"[INFO] Audio durations: {audio_durations}")
    
    return audio_paths, audio_durations

def compress_audio(input_path, output_path, verbose=True):
    """Compress audio to lower quality"""
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-codec:a", "libmp3lame",
        "-qscale:a", "9",  # Lower quality (scale: 0-9, 9 being lowest quality)
        "-ac", "1",  # Mono audio
        "-ar", "22050",  # Lower sample rate
        "-y",  # Overwrite output file if it exists
        output_path
    ]
    
    if verbose:
        print(f"[INFO] Compressing audio with ffmpeg")
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def get_audio_duration(audio_path):
    """Get the duration of an audio file using FFmpeg"""
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        audio_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def create_timed_scene_class(original_scene_class, audio_durations, verbose=True):
    """Create a new scene class that uses audio durations for timing"""
    from manim import Scene
    
    class TimedScene(original_scene_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.audio_durations = audio_durations
            self.segment = 0
        
        def next_segment(self):
            """Move to the next audio segment and return its duration"""
            if self.segment < len(self.audio_durations):
                duration = self.audio_durations[self.segment]
                self.segment += 1
                return duration
            else:
                # If we've run out of audio segments, return a default duration
                return 1.0
    
    TimedScene.__name__ = f"Timed{original_scene_class.__name__}"
    if verbose:
        print(f"[INFO] Created timed scene class: {TimedScene.__name__}")
    
    return TimedScene

def render_scene(scene_class, tmp_dir, verbose=True, quality="low"):
    """Render the Manim scene and return the path to the generated video"""
    from manim import config, tempconfig
    
    if verbose:
        print("[INFO] Rendering Manim scene...")
    
    # Store original config values
    original_media_dir = config.media_dir
    original_verbosity = config.verbosity
    
    # Configure Manim to use our temp directory
    media_dir = os.path.join(tmp_dir, "media")
    
    # Set up output capture to find the video path
    global captured_video_path
    captured_video_path = None
    
    def custom_print(*args, **kwargs):
        global captured_video_path
        message = " ".join(str(arg) for arg in args)
        original_print(*args, **kwargs)
        
        # Try to capture the video path from Manim's output logs
        if "File ready at" in message and ".mp4" in message:
            match = re.search(r"File ready at\s+'([^']+\.mp4)'", message)
            if match:
                captured_video_path = match.group(1)
                if verbose:
                    print(f"[INFO] Captured video path from logs: {captured_video_path}")
    
    import builtins
    original_print = builtins.print
    builtins.print = custom_print
    
    try:
        # Render with temporary config
        quality_config = {
            "media_dir": media_dir,
            "verbosity": "DEBUG" if verbose else "WARNING",
            "pixel_height": 240,
            "pixel_width": 426,
            "frame_rate": 15
        }
        
        with tempconfig(quality_config):
            scene = scene_class()
            scene.render()
        
        # Restore original print function
        builtins.print = original_print
        
        # Return the captured path if available
        if captured_video_path and os.path.exists(captured_video_path):
            if verbose:
                print(f"[INFO] Using video file from Manim logs: {captured_video_path}")
            return captured_video_path
        
        # Look for the video file if not captured from logs
        if verbose:
            print("[INFO] Looking for video file...")
        
        # Try common output locations
        class_name = scene_class.__name__
        possible_paths = [
            os.path.join(media_dir, f"videos/240p15/{class_name}.mp4"),
            os.path.join(media_dir, f"videos/low/{class_name}.mp4")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                if verbose:
                    print(f"[INFO] Found video at: {path}")
                return path
        
        # Last resort: recursive search
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if file.endswith(".mp4"):
                    path = os.path.join(root, file)
                    if verbose:
                        print(f"[INFO] Found video at: {path}")
                    return path
        
        raise Exception("Manim didn't generate any video files or they couldn't be found")
        
    except Exception as e:
        builtins.print = original_print
        raise e
    finally:
        # Always restore original print function
        builtins.print = original_print

def concatenate_audio_files(audio_paths, output_path, verbose=True):
    """Concatenate multiple audio files into one"""
    if verbose:
        print("[INFO] Concatenating audio files...")
    
    # Create a temporary file with the list of audio files
    dirname = os.path.dirname(output_path)
    os.makedirs(dirname, exist_ok=True)
    
    list_file = os.path.join(dirname, "audio_list.txt")
    with open(list_file, "w") as f:
        for audio_path in audio_paths:
            f.write(f"file '{audio_path}'\n")
    
    # Use FFmpeg to concatenate the files with low quality settings
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c:a", "libmp3lame",
        "-q:a", "9",
        "-ac", "1",
        "-ar", "22050",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Clean up list file
    os.remove(list_file)
    
    return output_path

def merge_audio_and_video(video_path, audio_path, output_path, verbose=True, quality="240p"):
    """Merge audio and video files with low quality settings"""
    if verbose:
        print("[INFO] Merging audio and video...")
    
    # First verify files exist
    if not os.path.exists(video_path):
        raise Exception(f"Video file not found at: {video_path}")
    if not os.path.exists(audio_path):
        raise Exception(f"Audio file not found at: {audio_path}")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Use FFmpeg to merge the files with low quality settings
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",  # Faster encoding
        "-crf", "30",  # Lower quality (higher value = lower quality)
        "-s", "426x240",  # 240p resolution
        "-c:a", "aac",
        "-b:a", "64k",  # Low audio bitrate
        "-ac", "1",  # Mono audio
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",  # Overwrite output file if it exists
        output_path
    ]
    
    if verbose:
        print(f"[INFO] Running FFmpeg command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        if verbose:
            print(f"[ERROR] FFmpeg error: {result.stderr}")
        raise Exception("Failed to merge audio and video")
    
    return output_path


def extract_scene_name_from_strcode(manim_code: str) -> str:
    """Extract the name of the Scene class from a Manim code string."""
    try:
        tree = ast.parse(manim_code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in ['Scene', 'MovingCameraScene']:
                        return node.name
        return None
    except Exception as e:
        print(f"Error extracting scene name: {str(e)}")
        return None




    