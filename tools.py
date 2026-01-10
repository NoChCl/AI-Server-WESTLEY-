from sentence_transformers import SentenceTransformer
from delimiters import *
import requests, json, time, pickle, faiss, numpy, os


OLLAMA_URL = "http://localhost:11434"


# Load embedding model once
embedModel = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384  # embedding size for MiniLM



def getContext(currentUserPrompt, personalityName, topK=5):
    print("Getting Relevent Context")

    # File names
    textFile = personalityName + ".pkl"
    indexFile = personalityName + ".index"

    # Load chat history
    try:
        chatHistory = pickle.load(open(textFile, "rb"))
    except:
        return ""

    # Load FAISS index
    if not os.path.exists(indexFile):
        return ""

    index = faiss.read_index(indexFile)

    # Embed query
    queryVec = embedModel.encode([currentUserPrompt])
    queryVec = numpy.array(queryVec, dtype="float32")

    # Search topK
    distances, indices = index.search(queryVec, topK)

    # Collect relevant history
    relvHistory = ""
    for idx in indices[0]:
        if 0 <= idx < len(chatHistory):
            relvHistory += chatHistory[idx] + "\n"
    return relvHistory



def getFullPrompt(personality, context, prompt):
    
    return f"""
{personality}

All questions must be answer truthfully and to the best of your knowlage.
If you are ever unsure about any information, respond with "I don't know".

You may request external actions at any point in a response using a dedicated escape delimiter in the form of <<< ACTION_NAME: action_input >>>.
Text before the delimiters is the only text that is user-visible output.
Text inside is strictly read by the action being preformed.
Text on the tail end is to be used for writing notes to yourself to clarify reasoning for action or giving extra context.
Try to answer any response in as few calls to external tools as possible.

Bellow is a list of functions avalible that use the delimiters discribed above:

{getDelimitors()}

End delimited functions list.

Use the following conversation history to guide your response. If a question asks about past messages,
you may only reference this transcript. If the information isn't there, respond with:
"I don’t know based on the transcript."

=== BEGIN TRANSCRIPT ===
{context}
=== END TRANSCRIPT ===

User: {prompt}
WESTLEY: """



def getResponse(fullPrompt, model="qwen2.5:14b"):
    

    for i in range(10):
        # Send request to Ollama
        payload = {
            "model": model,
            "prompt": fullPrompt,
            "stream": True
        }        
        response = requests.post(f"{OLLAMA_URL}/v1/completions", json=payload, stream=True)
                
        if response is None:
            if i == 9:
                print("WESTLEY: Something went wrong, please try again.")
                return ""
            print("WESTLEY: Something went wrong, atempting again.")
        else:
            break

    return response
    
def proccesing(responseObj, personality, context, prompt, personalityName, model, fm=""):
    mt=""
    yield mt.encode('utf-8')
    fullMessage = ""
    delimited = False
    for line in responseObj.iter_lines():
        if line:
            chunk = line.decode('utf-8').removeprefix('data: ')
            if not chunk or chunk == "[DONE]":
                continue
            content = json.loads(chunk)["choices"][0]["text"]
            
            fullMessage += content
            
            
            if delimited:
                yield mt.encode('utf-8')
                continue

            elif isDeliniated(fullMessage):
                print("Response Delimited")
                delimited=True
                yield content.split("<<<")[0].encode('utf-8')
                
                    
            else: yield content.encode('utf-8')  # <-- encode to bytes
                
            
            
    if delimited:
        
        userOutput=fullMessage.split("<<<")[0]
        
        delimiterOutput = delimiterLogic(fullMessage)
        
        context+=f"WESTLEY: {userOutput}\n"
        context+=f"{delimiterOutput}\n"
        
        fm+=f"\n{delimiterOutput}"
        
        print("Delimiter Complete, Getting New Response")
        responseObj = getResponse(getFullPrompt(personality, context, prompt), model)
        
        fm+=f"\n{fullMessage}"
        
        yield mt.encode('utf-8')
        yield from proccesing(responseObj, personality, context, prompt, personalityName, model, fm)
    else:
        fm+=f"\n{fullMessage}"
        print("Saving History")
        saveHistory(prompt, fm, personalityName)
        print("\n")

    
def saveHistory(prompt, response, personalityName):
    
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    
    # File names for this personality
    textFile = personalityName + ".pkl"
    indexFile = personalityName + ".index"
    
    # --- Load chat history ---
    
    try:
        chatHistory = pickle.load(open(textFile, "rb"))
    except:
        chatHistory = []
        
        
    #make chat history, format is timestamp, user prompt, ai response
    newEntry=f"{timestamp}\nUser: {prompt}\nWESTLEY: {response}\n"
    chatHistory.append(newEntry)

    # Save text history
    with open(textFile, "wb") as f:
        pickle.dump(chatHistory, f)
    
    
    # --- Load or create FAISS index ---
    if os.path.exists(indexFile):
        index = faiss.read_index(indexFile)
    else:
        index = faiss.IndexFlatL2(dimension)

    # Embed and add new entry
    vector = embedModel.encode([newEntry])
    index.add(numpy.array(vector, dtype="float32"))

    # Save FAISS index to disk
    faiss.write_index(index, indexFile)
    
    
def rebuildIndex(personalityName):
    textFile = personalityName + ".pkl"
    indexFile = personalityName + ".index"

    try:
        chatHistory = pickle.load(open(textFile, "rb"))
    except:
        print("No history file to rebuild from.")
        return

    index = faiss.IndexFlatL2(dimension)

    # Embed all history lines
    vectors = embedModel.encode(chatHistory)
    index.add(numpy.array(vectors, dtype="float32"))

    faiss.write_index(index, indexFile)
    print(f"Rebuilt index for {personalityName}, {len(chatHistory)} entries.")
