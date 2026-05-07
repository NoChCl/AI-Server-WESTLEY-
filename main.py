from flask import *
from tools import *
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_message():
    model="qwen2.5:14b"
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
    
    rawJson = request.json
    
    if not isinstance(rawJson, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    
    if rawJson.get("interface") == "CLI":
        data = handleCLI(request.json)
    else:
        data = {"error": "Unknown or missing field 'interface'"}

    if "error" in data:
        return jsonify(data), 400
    
    # Extract data
    model = data["model"]
    prompt = data["prompt"]
    personality = data["personality"]
    personalityName = data["personalityName"]
    
    context = getContext(prompt, personalityName)
    
    
        
    print("Streaming Response")
    return Response(proccesing(personality, context, prompt, personalityName, model), mimetype="text/plain", direct_passthrough=True)

    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
