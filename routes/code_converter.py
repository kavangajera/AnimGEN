def extract_code_from_response(response: str) -> str:
    """
    Extracts only the code part from a response containing Python code within code blocks.

    Args:
        response (str): The response containing code within ```python ... ```.

    Returns:
        str: The raw code without the surrounding code block markers.
    """
    if response.startswith("```python") and response.endswith("```"):
        return response[9:-3].strip()
    return response.strip()

