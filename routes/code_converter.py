def extract_code_from_response(response: str) -> str:
    """
    Extracts only the code part from a response containing Python code within code blocks.

    Args:
        response (str): The response containing code within ```python ... ``` or ``` ... ```.

    Returns:
        str: The raw code without the surrounding code block markers.
    """
    response = response.strip()
    
    # Check for a Python-specific code block
    if response.startswith("```python") and response.endswith("```"):
        return response[len("```python"): -len("```")].strip()
    
    # Check for a generic code block
    if response.startswith("```") and response.endswith("```"):
        return response[3:-3].strip()
    
    # Return the response as-is if no code block markers are found
    return response


