# dependency_check.py
import sys
import subprocess
import pkg_resources
import importlib
import os

def check_python_version():
    print(f"Python Version: {sys.version}")

def check_manim_installation():
    try:
        import manim
        print(f"Manim Version: {manim.__version__}")
    except ImportError:
        print("ERROR: Manim is not installed!")
    except Exception as e:
        print(f"ERROR checking Manim: {str(e)}")

def check_system_dependencies():
    dependencies = ['ffmpeg', 'latex']
    for dep in dependencies:
        try:
            result = subprocess.run(['which', dep], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{dep} found at: {result.stdout.strip()}")
            else:
                print(f"ERROR: {dep} not found!")
        except Exception as e:
            print(f"ERROR checking {dep}: {str(e)}")

def check_python_packages():
    required_packages = [
        'numpy',
        'scipy',
        'pillow',
        'cairo',
        'pycairo',
        'pangocairo',
        'flask'
    ]
    
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"{package} Version: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"ERROR: {package} is not installed!")
        except Exception as e:
            print(f"ERROR checking {package}: {str(e)}")

def check_manim_config():
    config_paths = [
        os.path.expanduser("~/.config/manim/manim.cfg"),
        "/etc/manim/manim.cfg",
        os.path.join(os.getcwd(), "manim.cfg")
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            print(f"Manim config found at: {path}")
            return
    print("WARNING: No manim.cfg found!")

if __name__ == "__main__":
    print("=== Starting Dependency Check ===")
    print("\n1. Python Version:")
    check_python_version()
    
    print("\n2. Manim Installation:")
    check_manim_installation()
    
    print("\n3. System Dependencies:")
    check_system_dependencies()
    
    print("\n4. Python Packages:")
    check_python_packages()
    
    print("\n5. Manim Configuration:")
    check_manim_config()
    
    print("\n=== Dependency Check Complete ===")