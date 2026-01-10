from web import *
from weather import *
import asyncio


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
    print("Proccessing Delimiter")
    #this is text that was already output to user, which would be before the delimiter
    output=message.split("<<<")[0]
    
    #this is the message in the delimiter, which would be after <<< but before >>>
    delimination=message.split("<<< ")[1].split(" >>>")[0]
    
    #this is the thoights to pass onto next ai, which come after >>>
    thoughts=message.split(">>>")[1]
    
    action, paramaters = delimination.split(": ")
    
    if action == "Search":
        #this is where to handle search
        print("Calling Search Delimiter")
        searchOut=asyncio.run(search(paramaters))
        return f"Search Module: {searchOut}\nWESTLEY Thinking:\n{thoughts}"
    elif action == "Image":
        print("Calling Image Delimiter")
        #this is where to handle image gen
        return f"{action} Module is currently unavalible.\nWESTLEY Thinking:\n{thoughts}"
    elif action == "Weather":
        #this is where to handle search
        print("Calling Weather Delimiter")
        weatherOut=getWeather(paramaters)
        return f"Weather Module:\n{weatherOut}.\nWESTLEY Thinking:\n{thoughts}"
    elif action == "Think":
		print("Think Delimiter")
        return f"WESTLEY Thinking:\n{thoughts}"
    else:
		print(f"Invald Delimiter {action} called with paramaters {paramaters}")
        return f"{action} Module does not exist! If you think this function could be of consistant use, ask the user for it to be implemented.\nWESTLEY Thinking:\n{thoughts}"



#SEARCH





#IMAGE


