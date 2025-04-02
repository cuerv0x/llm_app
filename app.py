# You can find this code for Chainlit python streaming here (https://docs.chainlit.io/concepts/streaming/python)

# OpenAI Chat completion
import os
from openai import AsyncOpenAI  # importing openai for API usage
import chainlit as cl  # importing chainlit for our app
from chainlit.prompt import Prompt, PromptMessage  # importing prompt tools
from chainlit.playground.providers import ChatOpenAI  # importing ChatOpenAI tools
from dotenv import load_dotenv

load_dotenv()

# ChatOpenAI Templates
system_template = """You are a cheerful and entertaining AI companion who delights in sharing clever wordplay and humorous quips while providing valuable assistance!
Your messages sparkle with personality through the liberal use of fun emojis! 🌟 ✨
"""

user_template = """{input}
Please provide a thoughtful, step-by-step response and weave in a playful pun or joke that fits the topic.
Keep your answer entertaining and captivating! 🎭 ✨
"""


@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
settings = {
    "model": "gpt-4",  # Using GPT-4 for more creative and nuanced responses
    "temperature": 0.7,  # Higher temperature for more creative responses
    "max_tokens": 1000,  # Increased token limit for longer responses
    "top_p": 0.9,  # Slightly lower top_p for more focused but still creative text
    "frequency_penalty": 0.5,  # Encourages more varied word choice
    "presence_penalty": 0.5,  # Encourages the model to talk about new topics
}

cl.user_session.set("settings", settings)



@cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    client = AsyncOpenAI()

    print(message.content)

    prompt = Prompt(
        provider=ChatOpenAI.id,
        messages=[
            PromptMessage(
                role="system",
                template=system_template,
                formatted=system_template,
            ),
            PromptMessage(
                role="user",
                template=user_template,
                formatted=user_template.format(input=message.content),
            ),
        ],
        inputs={"input": message.content},
        settings=settings,
    )

    print([m.to_openai() for m in prompt.messages])

    msg = cl.Message(content="")

    # Call OpenAI
    async for stream_resp in await client.chat.completions.create(
        messages=[m.to_openai() for m in prompt.messages], stream=True, **settings
    ):
        token = stream_resp.choices[0].delta.content
        if not token:
            token = ""
        await msg.stream_token(token)

    # Update the prompt object with the completion
    prompt.completion = msg.content
    msg.prompt = prompt

    # Send and close the message stream
    await msg.send()
