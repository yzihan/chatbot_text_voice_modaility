from openai import OpenAI # type: ignore
import os
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)
    
 ##############################################################################################################################################
 ## Below are the functions to set openai model parameters and send to openai
 ##############################################################################################################################################

def send_prompt(prompt, model = "gpt-3.5-turbo", is_json=False):
    if is_json:
        response = client.chat.completions.create(
            model= model, 
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
    else:
        response = client.chat.completions.create(
            model= model, 
            messages=[{"role": "user", "content": prompt}]
        )
    
    resp =response.choices[0].message.content
    return resp


def send_messages(messages, model = "gpt-3.5-turbo", is_json=False):
    if is_json:
        response = client.chat.completions.create(
            model= model, 
            response_format={ "type": "json_object" },
            messages=messages
        )
    else:
        response = client.chat.completions.create(
            model= model, 
            messages=messages
        )
    
    resp =response.choices[0].message.content
    return resp




def send_audio(file, model="whisper-1"):
    """
    file = open("xxx.mp3", "rb")
    """
    response = client.audio.translations.create(
        model= model, 
        file=file,
    )
    
    resp =response.text
    return resp
