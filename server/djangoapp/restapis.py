# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# def get_request(endpoint, **kwargs):
# Add code for get requests to back end
def get_request(endpoint, **kwargs):
    # Use urlencode to safely encode parameters
    params = urlencode(kwargs)

    # Construct the full request URL
    request_url = backend_url + endpoint + ("?" + params if params else "")
    print(f"GET from {request_url}")

    try:
        # Send GET request to the server
        response = requests.get(request_url)
        
        # Check if response is successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code} from the server.")
            return {"status": response.status_code, "message": "Error fetching data"}
    except requests.exceptions.RequestException as e:
        # Log network errors or request exceptions
        print(f"Network exception occurred: {e}")
        return {"status": 500, "message": "Network exception occurred"}

# def analyze_review_sentiments(text):
# request_url = sentiment_analyzer_url+"analyze/"+text
# Add code for retrieving sentiments
def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")

# def post_review(data_dict):
# Add code for posting review
def post_review(data_dict):
    request_url = backend_url+"/insert_review"
    try:
        response = requests.post(request_url,json=data_dict)
        print(response.json())
        return response.json()
    except:
        print("Network exception occurred")