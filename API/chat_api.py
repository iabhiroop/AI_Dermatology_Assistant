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
client = OpenAI(base_url="https://f3fc-115-244-132-22.ngrok-free.app/v1", api_key="not-needed")

name = ""

def generate_chat_completion(data):
    room_id = data["userid"]+"1234"
    prompt = data["query"]
    room_data = db_client.get_last_history(room_id, 100)
    conversation_length = 0 if room_data is None else (len(room_data['history']) - 1)//2
    # print(room_data)
    k=0
    if room_data is None:
        prompt = "Please ask me question to find out necessary symptoms. I would prefer you to use yes or no questions. At most short questions"
        k=1
        new_room_data = {
            'roomid': room_id,
            'followUpQuestions': None,
            'history': [
                {'role': "system", 'content': "You are a rude dermatology assistant. Keep the responses short. Ask the patient about symptoms, validate the model predictions and give a preliminary diagnosis. If the user's symptoms don't match to any of the diseases, explain that if they still feel sick to visit a dermatologist. Four models gives the following output for the patient where keys under 0 is more relevant than those under 1 are less revelent. Only ask question to confirm the disease from these possibilities: " + str(db_client.get_user_data(data["userid"])["diagnosis"]), 'timestamp': str(datetime.now())},
            ],
            'conversation_history': [
                {'role': "assistant", 'content': "You are a dermatology assistant.", 'timestamp': str(datetime.now())},
            ],
        }

        db_client.create_room(new_room_data)
        room_data = db_client.get_last_history(room_id, 100)
    if prompt == "":
        return ""
    his_data = room_data["history"][1:]
    base_system = [{'role': "system", 'content': "You are a rude dermatology assistant. Keep the responses short. Ask the patient about symptoms, validate the model predictions and give a preliminary diagnosis. If the user's symptoms don't match to any of the diseases, explain that if they still feel sick to visit a dermatologist. Four models gives the following output for the patient where keys under 0 is more relevant than those under 1 are less revelent. Only ask question to confirm the disease from these possibilities: " + str(db_client.get_user_data(data["userid"])["diagnosis"])}]
    if k==0:
        message = base_system + [{'role': entry['role'], 'content': entry['content']} for entry in his_data[-20:]]
    else:
        message = base_system
    message.append({'role': "user", 'content': prompt})
    print(message)
    completion = client.chat.completions.create(
    model="local-model",
    messages= message,
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
    # response = dict(db_client.get_user_data(data.userid))
    # del response["_id"]
    print("Outside")
    print(response)
    print()
    # return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=response)
    return response