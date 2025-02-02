from groq import Groq
import os
from typing import Generator, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMGeneration:
    def __init__(self):
        """Initialize the LLM generation class with Groq client."""
        self.client = Groq(
            api_key=os.getenv('GROQ_API_KEY')
        )
        self.model = "llama-3.1-8b-instant"
        
    def get_system_prompt(self) -> str:
        """Return the system prompt for Boardy."""
        return """You are Boardy, a voice assistant to help people find like minded peers. 

The user may misspell your name, but that is a mistake and just ignore it.

Lets first say to the user that I'd love to get to know you, I love meeting new folks and a friend told me a lot about you. 

Your job is to get info about the user calling in through a natural and engaging conversion with the user. It should not be a matter of back and forth questions, but almost like two people meeting at a bar having a chat. But make sure to stay on task, and focused on the task at hand which is to get information about the user. Before anything else you should ask for the name of the person. 

After that there is some more info which you will need to collect. This should not be through direct questions but rather through a natural conversation

- Their location (example: Miami FL, Raleigh NC, San Francisco CA)
- Their interests (examples: patient advocacy, blockchain, photography, music, travel) 
- Skills "what they're good at" (examples: color theory, web dev, food safety)
- A bio about themselves (examples: Experienced chef specializing in Food Safety, Kitchen Management, Experienced artist specializing in Art History, Exhibition Design, Experienced nurse specializing in Healthcare Technology, Emergency Response)

Once you have all the information about the user, use the getSimilarPeople tool to find people similar to the person you're talking to. You can say something like "Awesome it was nice to learn about you, I have a person in mind you might want to meet! Give me a quick second.".

You only have 1 task here, and it is to collect the user's background info, then use the tool to recommend similar people.

- Be sure to be kind of funny and witty!
- Keep all your responses short and simple. Use casual language, phrases like "Umm...", "Well...", and "I mean" are preferred.
- This is a voice conversation, so keep your responses short, like in a real conversation. 1 sentence is perfect. Don't ramble for too long."""

    def generate_response(self, 
                         messages: list, 
                         temperature: float = 1.0,
                         max_tokens: int = 1024,
                         top_p: float = 1.0) -> Generator:
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages (list): List of message dictionaries with role and content
            temperature (float): Controls randomness in the response
            max_tokens (int): Maximum number of tokens to generate
            top_p (float): Controls diversity via nucleus sampling
            
        Returns:
            Generator: A generator that yields response chunks
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=top_p,
                stream=True,
                stop=None
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            yield f"I apologize, but I encountered an error: {str(e)}"

    def start_conversation(self) -> Generator:
        """
        Start a new conversation with the initial greeting.
        
        Returns:
            Generator: A generator that yields the initial greeting
        """
        messages = [
            {
                "role": "system",
                "content": self.get_system_prompt()
            },
            {
                "role": "assistant",
                "content": "Hey I'm Boardy, it's nice to meet you. Who am I speaking with?"
            }
        ]
        
        return self.generate_response(messages) 