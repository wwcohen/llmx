#!/usr/bin/python3.8

# test mistral API

import os

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = os.environ["MISTRAL_API_KEY"]
model = "open-mixtral-8x7b"

client = MistralClient(api_key=api_key)

chat_response = client.chat(
    model=model,
    messages=[ChatMessage(role="user", content="What's some good vegan restaurants in Pittsburgh??")]
)

print(chat_response.choices[0].message.content)
