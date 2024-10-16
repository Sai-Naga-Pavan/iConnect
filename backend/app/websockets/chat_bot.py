import base64
import json
import os
from fastapi import WebSocket
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


llm_client_chat = InferenceClient(
    model="facebook/blenderbot-400M-distill",
    token=HF_TOKEN,  # Authentication token
    timeout=120,     # Set a timeout for requests
)

llm_client_image = InferenceClient(
    model="black-forest-labs/FLUX.1-dev",
    token=HF_TOKEN,
    timeout=120
)

image_keywords = ["image", "create", "draw", "picture", "photo", "generate", "make"]

def detect_intent(user_message):
    if any(keyword in user_message.lower() for keyword in image_keywords):
        return "generate_image"
    
    return "chat"

async def call_llm(inference_client: InferenceClient, prompt: str):
    try:
        # Call the model to generate a response
        response = inference_client.post(
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": 200},  # Define max tokens for the response
                "task": "text-generation",
            },
        )
        # Parse and return the generated text
        return json.loads(response.decode())[0]["generated_text"]

    except Exception as e:
        # Handle any errors during the request
        print(f"Error calling the model: {e}")
        return "Error occurred during inference."

async def call_image_model(prompt: str):
    try:
        response = llm_client_image.post(
            json={
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 50,  # Adjust according to model capabilities
                    "guidance_scale": 7.5,      # Control the creativity of the image generation
                },
            },
        )
        
        print(response)
        image_base64 = base64.b64encode(response).decode("utf-8")

        # Create a data URI for the image
        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print(f"Error calling the image model: {e}")
        return "Error occurred while generating the image."


async def chat_bot_function(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    try:
        while True:
            user_message = await websocket.receive_text()  # Receive message from the user
            print(f"User message: {user_message}")
            
            bot_message = "Sorry, something went wrong."

             # Detect the intent of the user's message
            intent = detect_intent(user_message)
                
            # Call the appropriate model based on the detected intent
            if intent == "generate_image":
                    # Call the image model
                    bot_message = await call_image_model(user_message)
                    print(f"Image response: {bot_message}")
            else:
                    prompt = f"Your name is iConnect Bot, help the user with the following question: {user_message}"
                    bot_message = await call_llm(llm_client_chat, prompt)
                    print(f"Chat response: {bot_message}")

            # Send bot's response back to the user
            await websocket.send_text(bot_message)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()