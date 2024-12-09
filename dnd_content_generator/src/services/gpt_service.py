# gpt_service.py
import asyncio
import openai
import random
from src.services.logger import logger
from src.utils import load_config

async def post_to_gpt(messages, temp = 0.27):
    config = load_config("src/config/config.json")
    client = openai.AsyncOpenAI(api_key=config['gpt-api']['api-key'])

    model_name = config["app-settings"]["models"][0]
    conversation = [{"role": "user", "content": config.get("primer", "") + "\n\n" + messages}]
    logger.info(f"temp: {temp}")
    try:        
        # Use the modern async call for chat completions        
        response = await client.chat.completions.create(
            model=model_name,
            messages=conversation,
            max_tokens=config["app-settings"].get("max-tokens", 7000),
            temperature=temp,
            top_p=0.9,
            n=1
        )
        reply = response.choices[0].message.content
        logger.info(f"""Prompt: {conversation} \n\nResponse: {reply}""")
        return reply.strip()
    except Exception as e:
        logger.error(f"GPT request failed: {e}")
        return None

class GPTService:
    def __init__(self):
        pass

    async def send_prompt_async(self, prompt, temp=0.27):
        return await post_to_gpt(prompt, temp)
