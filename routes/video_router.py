from flask import Blueprint, request, jsonify
import os
import subprocess

video_routes = Blueprint('video_routes', __name__)

# Define directory for Manim files
MANIM_DIR = os.path.join(os.getcwd(), 'manim_files')

# Ensure directory exists
os.makedirs(MANIM_DIR, exist_ok=True)

# Function to create the Manim code file directly in the 'manim_files' directory
def create_manim_file(code):
    file_path = os.path.join(MANIM_DIR, "scene.py")
    try:
        with open(file_path, "w") as f:
            f.write(code)
        print("[SUCCESS] Manim file created at:", file_path)
    except Exception as e:
        print("[ERROR] Failed to create Manim file:", str(e))
        raise e
    return file_path



# Function to run the Manim command
def run_manim():
    try:
        print("\n[INFO] Running Manim command...")

        # Navigate to the 'manim_files' directory and run the Manim command
        cmd = ["manim", "-pql", "--resolution", "640,360", "scene.py", "HelloWorldScene"]

        # Using subprocess with real-time output and timeout
        process = subprocess.Popen(
            cmd, 
            cwd=MANIM_DIR, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True  # Ensure the output is in a readable string format
        )

        # Stream stdout and stderr in real-time
        for line in iter(process.stdout.readline, ''):
            if line:
                print("[MANIM STDOUT]:", line.strip())

        for line in iter(process.stderr.readline, ''):
            if line:
                print("[MANIM STDERR]:", line.strip())

        process.stdout.close()
        process.stderr.close()
        process.wait(timeout=300)  # Timeout of 5 minutes (adjust as needed)

        if process.returncode != 0:
            print("[ERROR] Manim failed with return code:", process.returncode)
            return f"Manim error: Check logs for details.", 500

        print("[SUCCESS] Manim command completed successfully.")
        return "Video generation successful.", 200

    except subprocess.TimeoutExpired:
        process.kill()
        print("[ERROR] Manim process timed out.")
        return "Manim process timed out.", 500

    except Exception as e:
        print("[ERROR] Exception during Manim execution:", str(e))
        return str(e), 500

# API route to generate video
@video_routes.route('/generate-video', methods=['POST'])
def generate_video_route():
    try:
        print("[INFO] Received request to generate video...")
        data = request.json
        manim_code = data.get('code')
        if not manim_code:
            return jsonify({'error': 'No Manim code provided'}), 400

        create_manim_file(manim_code)
        message, status = run_manim()
        return jsonify({'message': message}), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500
