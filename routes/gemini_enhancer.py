from openai import OpenAI
from dotenv import load_dotenv
import os
import ast
load_dotenv()

def generate_manim_script(prompt: str) -> list:
    """Generate a Manim animation script array based on a user prompt."""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        completion = client.chat.completions.create(
            model="google/gemini-2.0-pro-exp-02-05:free",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    ** You are making script for manim code animations taking general prompt from user and giving script array as output

                    input : {prompt}

                    output : **Don't include empty "" value in script**
                             **Always make script which completes in 20-30 seconds (consider audio is of slow to moderate speed)**
                             JUST GIVE BELOW code form:(NO EXPLAINATION JUST ARRAY)
                             e.g. -> script = ["","",...]
                    """
                }
            ]
        )

        # Extract the script array from the response
        return completion.choices[0].message.content
        
    
    except Exception as e:
        print(f"An error occurred: {e}")
        

# Example usage



def parse_script_string(prompt):
    """
    Parse a string representation of a Python list (like from a code block)
    and return an actual Python list.
    
    Args:
        script_string (str): String representation of a Python list
        
    Returns:
        list: Parsed Python list
    """
    script_string = generate_manim_script(prompt)

    # Clean up the input by removing unnecessary parts
    lines = script_string.strip().split('\n')
    
    # Remove the first line if it contains 'script = ['
    if lines and 'script = [' in lines[0]:
        lines = lines[1:]
    
    # Remove the last line if it only contains ']'
    if lines and lines[-1].strip() == ']':
        lines = lines[:-1]
    
    # Process each line
    result = []
    for line in lines:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Remove leading/trailing quotes and commas
        if line.startswith('"') and line.endswith('",'):
            line = line[1:-2]
        elif line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        elif line.endswith(','):
            line = line[:-1]
            
        # Remove extra quotes if present
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
            
        result.append(line)
    result.pop(0)
    result.pop(0)
    result.pop(len(result)-1)
    result.pop(len(result)-1)

        
    return result



