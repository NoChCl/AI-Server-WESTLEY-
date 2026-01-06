import asyncio
from pyppeteer import launch
from weather import *


def isDeliniated(text):
    if "<<<" in text:
        return True
    else:
        return False



def getDelimitors():
    d=""
    
    d+='''
If additional information is required to answer the question, you may search the internet.  
To request a search, use the delimiters with the ACTION_NAME being "Search".
The action_input should be the exact query you want to look up.'''
    
    d+='''
If you would like to use more reasoning and have longer and more of a chance to ponder before outputing a final answer, you may do so.
To do so, use the delimiters with the ACTION_NAME being "Think".
Delimiters must have a action_input so we will have that be "None".
The full implemetation should be "<<< Think: None >>>" followed by whatever reasoning reqired.'''
    
    d+='''
You have the ability to check the weather and forcase.
To do so, use the delimiters with the ACTION_NAME being "Weather".
The action_input should specify weather you want "Current" or "Forecast" (this is the Type), followed by the location you are requesting weather for.
The action_input by default asumes the location is in the United States.
The action_input should be structured in a format of "Type - Town, State", and seperated by a comma.
If you need weather for a location outside the United States, you say it in the form of "Type - Town, State, Country"'''
    
    
    d+="""
If image generation is required, you can do so.  
To request image generation, use the delimiters with the ACTION_NAME being "Image".
The action_input should be the exact discription of the image you would like to generate."""
    
    return d



def delimiterLogic(message):
    #this is text that was already output to user, which would be before the delimiter
    output=message.split("<<<")[0]
    
    #this is the message in the delimiter, which would be after <<< but before >>>
    delimination=message.split("<<< ")[1].split(" >>>")[0]
    
    #this is the thoights to pass onto next ai, which come after >>>
    thoughts=message.split(">>>")[1]
    
    action, paramaters = delimination.split(": ")
    
    if action == "Search":
        #this is where to handle search
        print("Calling Search delimiter")
        return f"{action} Module is currently unavalible.\nWESTLEY Thinking:\n{thoughts}"
    elif action == "Image":
        print("Calling Image delimiter")
        #this is where to handle image gen
        return f"{action} Module is currently unavalible.\nWESTLEY Thinking:\n{thoughts}"
    elif action == "Weather":
        #this is where to handle search
        print("Calling Weather delimiter")
        weatherOut=getWeather(paramaters)
        return f"Weather Module:\n{weatherOut}.\nWESTLEY Thinking:\n{thoughts}"
    elif action == "Think":
        return f"WESTLEY Thinking:\n{thoughts}"
    else:
        return f"{action} Module does not exist! If you think this function could be of consistant use, ask the user for it to be implemented.\nWESTLEY Thinking:\n{thoughts}"



#SEARCH


def doSearch(firstChunk, responseObj, prompt, context, personality, model="qwen2.5:14b"):
    interaction = getFullPrompt(personality, context, prompt)
    
    while True:
        fullMessage = firstChunk
        for line in responseObj.iter_lines():
            if not line:
                continue
            chunk = line.decode("utf-8").removeprefix("data: ").strip()
            if not chunk or chunk == "[DONE]":
                continue
            content = json.loads(chunk)["choices"][0]["text"]
            fullMessage += content
        
        interaction+=fullMessage
        
        query = fullMessage[len("Search"):].strip()
        print(f"WESTLEY requested search: {query}")
        searchResults = handleSearch(query)
        
        interaction +="\nSearch: "+searchResults
        
        responseObj = getResponse(interaction, model)
        
        isSearch, firstChunk = requestSearch(responseObj)
        
        if not isSearch:
            break
        
        
    return firstChunk, responseObj
    
    
async def performSearch(query, max_results=5):
    """
    Launches a headless browser and searches DuckDuckGo for the query.
    Returns a list of result dictionaries with title, link, and snippet.
    """
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.goto(f"https://duckduckgo.com/?q={query}")

    # Wait until results are loaded
    await page.waitForSelector(".result__a", timeout=8000)

    results = await page.evaluate(f"""() => {{
        const items = Array.from(document.querySelectorAll('.result'));
        return items.slice(0, {max_results}).map(item => {{
            const title = item.querySelector('.result__a')?.innerText || '';
            const link = item.querySelector('.result__a')?.href || '';
            const snippet = item.querySelector('.result__snippet')?.innerText || '';
            return {{ title, link, snippet }};
        }});
    }}""")

    await browser.close()
    return results


def handleSearch(query):
    """
    Called by doSearch(). Performs a live internet search and returns formatted text.
    """
    try:
        results = asyncio.get_event_loop().run_until_complete(performSearch(query))
    except RuntimeError:
        # In case event loop is already running (e.g., inside async environment)
        results = asyncio.run(performSearch(query))
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return "No results found."

    formatted = []
    for r in results:
        formatted.append(f"{r['title']}\n{r['snippet']}\n{r['link']}")
    return "\n\n".join(formatted)
    





#IMAGE


