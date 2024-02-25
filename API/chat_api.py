from fastapi import APIRouter, Depends, HTTPException, Body, status, Header, Query
from typing import Optional, List
import json
from Schema.schema import InitializeData, ChatData
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from connections.mongo_db import db_client
from datetime import datetime
from openai import OpenAI
from Constants.utils import get_chat_history_buffer_memory

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)
client = OpenAI(base_url="https://e181-2402-3a80-428-c461-2484-fb60-97eb-ec72.ngrok-free.app/v1", api_key="not-needed")

name = ""

def generate_chat_completion(data):
    room_id = data["userid"]
    prompt = data["query"]
    room_data = db_client.get_last_history(room_id, 10)
    conversation_length = 0 if room_data is None else (len(room_data['history']) - 1)//2
    print(room_data)
    if room_data is None:
        conversation_response = f"Hi {name}, I am Derm AI. How can i help you?"

        new_room_data = {
            'roomid': room_id,
            'followUpQuestions': None,
            'history': [
                {'role': "system", 'content': "You are a dermatology assistant. Only answer question from that", 'timestamp': str(datetime.now())},
            ],
            'conversation_history': [
                {'role': "assistant", 'content': conversation_response, 'timestamp': str(datetime.now())},
            ],
        }

        db_client.create_room(new_room_data)
        # history = [
        #     {'role': "assistant", 'content': "Hi, I am Derm AI. How can i help you?", 'timestamp': str(datetime.now())},
        # ]

        # db_client.append_message_to_room(room_id, history,str(datetime.now()))
        
        return conversation_response
    else:
        message = [{'role': entry['role'], 'content': entry['content']} for entry in room_data["history"]]
        message.append({'role': "user", 'content': prompt})
        print(message)
        completion = client.chat.completions.create(
        model="local-model",
        messages= message,
        # [
            # {"role": "system", "content": "Always use medical terms."},
            # {"role": "user", "content": "Introduce yourself."},
            # {"role": "assistant", "content": "I am Bot."},
            # {"role": "user", "content": "What am I?"}
        # ],
        temperature=0.7,
        )

        print(completion.choices[0].message)
        conversation_response = completion.choices[0].message.content
        if conversation_response == "":
            conversation_response = "513 Bad response"
        history = [
            {'role': "user", 'content': prompt, 'timestamp': str(datetime.now())},
            {'role': "assistant", 'content': conversation_response, 'timestamp': str(datetime.now())},
        ]

        db_client.append_message_to_room(room_id, history,str(datetime.now()))
        
        return conversation_response


@router.post("/initialize")
async def intialize_user_chat(data: InitializeData = Body(..., description="Image data")):
    response = data
    
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=response)

@router.post("/query")
async def chat_completion(data: ChatData = Body(..., description="Image data")):
    response = generate_chat_completion(data.dict())
    
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=response)