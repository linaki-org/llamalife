# Importing the required library (ollama)
import ollama
import json
import pickle
from time import sleep

# Initializing an empty list for storing the chat messages and setting up the initial system message
chat_messages = []
system_message = 'You are now a point and click generator. You will answer every question I ask in json format, only json like this : {"text" : "You are in the cave", "options" : [{"text" : "go upstairs", "destination" : "firstFloor"}]}'
# Defining a function to create new messages with specified roles ('user' or 'assistant')
def create_message(message, role):
    return {
        'role': role,
        'content': message
    }


# Starting the main conversation loop
def chat():
    # Calling the ollama API to get the assistant response
    ollama_response = ollama.chat(model='mistral', messages=chat_messages, stream=True, options={"temperature" : 0})

    # Preparing the assistant message by concatenating all received chunks from the API
    assistant_message = ''
    for chunk in ollama_response:
        assistant_message+=chunk["message"]["content"]
        if assistant_message.replace("\n", "").replace(" ", "").endswith("]}"):
            break


    # Adding the finalized assistant message to the chat log
    chat_messages.append(create_message(assistant_message, 'assistant'))
    return assistant_message


# Function for asking questions - appending user messages to the chat logs before starting the `chat()` function
def ask(message):
    chat_messages.append(
        create_message(message, 'user')
    )
    return chat()

def write(text):
    for char in text:
        print(char, end="")
    print()

chat_messages.append(create_message(system_message, 'system'))
prompt="Start the story "+input("Where do you want to start the story ? Answer like this : in a castle  : ")
while True:
    response=ask(prompt)
    newResponse=""
    started=False
    for line in response.split("\n"):
        if line.replace(" ", "")!="":
            newResponse+=line+"\n"
            started=True
        elif started:
            break
    try:
        data=json.loads(newResponse)
    except json.decoder.JSONDecodeError:
        print("Regenerating...")
        response = ask("This is not valid json. Regenerate it in valid json")
        newResponse = ""
        started = False
        for line in response.split("\n"):
            if line.replace(" ", "") != "":
                newResponse += line + "\n"
                started = True
            elif started:
                break
        try:
            data = json.loads(newResponse)
        except json.decoder.JSONDecodeError:
            print("Unexpected Mistral response")
            print(response)
    try:
        write(data["text"])
        write("What do you want to do ?")
        for index, option in enumerate(data["options"]):
            write(str(index)+" : "+option["text"])
        while True:
            choosed=input("Make your choice : ")
            if choosed=="save":
                print("Saving game in save.lll")
                file=open("save.lll", "wb")
                pickle.dump(chat_messages, file)
                file.close()
                print("Saved !!!")
                continue
            if not choosed.isdigit():
                prompt = choosed
                break
            choosed=int(choosed)
            if choosed>=len(data["options"]):
                write("Your index is out of range.")
                continue
            prompt = "I choose to " + data["options"][choosed]["text"]
            break
    except Exception as e:
        print("OOPS ! An error occured")
        print(e)

