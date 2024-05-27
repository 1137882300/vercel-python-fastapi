#!/usr/bin/env python
import typing

import pydantic
from fastapi import Header, HTTPException
from fastapi.routing import APIRouter
from openai import AsyncClient
import requests

router = APIRouter()


class ChatArgs(pydantic.BaseModel):
    model: str
    messages: typing.List[typing.Dict[str, str]]


@router.post("/proxy/v1")
async def openai_api(args: ChatArgs, authorization: str = Header(...)):
    api_key = authorization.split(" ")[1]
    client = AsyncClient(base_url="https://api.openai.com",
                         api_key=api_key)
    return await client.chat.completions.create(
        model=args.model,
        messages=args.messages,
    )


@router.post("/proxy")
def proxy(request: dict):
    url = request.get("url")
    headers = request.get("headers")
    body = request.get("body")

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/proxy/v2")
async def openai_proxy(authorization: str = Header(...), args: dict = None):
    try:
        api_key = authorization.split(" ")[1]
        base_url = "https://api.openai.com"
        # endpoint = "/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        url = f"{base_url}"
        response = requests.post(url, json=args, headers=headers)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error proxying request: {str(e)}")
