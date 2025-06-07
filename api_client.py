import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def query_documents(question: str, max_results: int = 5) -> dict:
    """
    Query the documents using the API
    
    Args:
        question: The question to ask
        max_results: Maximum number of results to return
        
    Returns:
        Response from the API
    """
    try:
        data = {
            "question": question,
            "max_results": max_results
        }
        response = requests.post(
            f"{BASE_URL}/query",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        
        return response.json()
    except Exception as e:
        print(f"Error querying documents: {e}")
        raise e