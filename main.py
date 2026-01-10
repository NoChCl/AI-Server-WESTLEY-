from flask import *
from tools import *
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_message():
    
    print("Receved Message")
    
    """
    Receives a JSON payload like:
    {
        "model": "string",
        "prompt": "string",
        "personality": "string",
        "personalityName": "string"
    }
    Passes it to processing logic and returns a response immediately.
    """
    data = request.json

    # Validate the required fields
    required_fields = ["model", "prompt", "personality", "personalityName"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field '{field}'"}), 400
            
    model="qwen2.5:14b"
    
    # Extract data
    model = data["model"]
    prompt = data["prompt"]
    personality = data["personality"]
    personalityName = data["personalityName"]
    
    context = getContext(prompt, personalityName)
    
    print("Getting Response")
    responseObj = getResponse(getFullPrompt(personality, context, prompt), model)

    print("Received Response Object")
    
        
    print("Streaming Response")
    return Response(proccesing(responseObj, personality, context, prompt, personalityName, model), mimetype="text/plain", direct_passthrough=True)

    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
