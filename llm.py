from groq import Groq
import os
import json
import requests
from typing import Generator, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server URL for API calls
SERVER_URL = "https://dolphin-app-bsmq7.ondigitalocean.app"

def log(message):
    """Helper function for consistent logging"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [LLM] {message}")

class LLMGeneration:
    def __init__(self):
        """Initialize the LLM generation class with Groq client."""
        self.client = Groq(
            api_key=os.getenv('GROQ_API_KEY')
        )
        self.model = "llama-3.1-8b-instant"
        log(f"Initialized LLM with model: {self.model}")

    def get_system_prompt(self) -> str:
        """Return the system prompt for Boardy."""
        return """You are Boardy, a voice assistant to help people find like minded peers. 

The user may misspell your name, but that is a mistake and dont mention it.

Lets first say to the user that I'd love to get to know you, I love meeting new folks and a friend told me a lot about you. 

Your job is to get info about the user calling in through a natural and engaging conversion with the user. It should not be a matter of back and forth questions, but a natural flowing conversation. But make sure to stay on task, and focused on the task at hand which is to get information about the user. Before anything else you should ask for the name of the person. 

After that there is some more info which you will need to collect. This should not be through direct questions but rather through a natural conversation

- Their location (example: Miami FL, Raleigh NC, San Francisco CA)
- Their interests (examples: patient advocacy, blockchain, photography, music, travel) 
- Skills "what they're good at" (examples: color theory, web dev, food safety)
- A bio about themselves (examples: Experienced chef specializing in Food Safety, Kitchen Management, Experienced artist specializing in Art History, Exhibition Design, Experienced nurse specializing in Healthcare Technology, Emergency Response)

Once you have gotten the location, interests, skills, and bio of the person you're talking to, use the getSimilarPeople tool to find people similar to the person you're talking to. You should only use this tool once you have all the information about the user.

No need to mention that you're using the getSimilarPeople tool, just use it. 

The getSimilarPeople tool needs the params of query, which is a string description string of the person including their interests, skills, and background.

Example tool call:
{
  "name": "getSimilarPeople",
  "arguments": {
    "query": "A software engineer from San Francisco CA interested in blockchain, AI safety, and hiking. Skilled in Python, smart contracts, and system design. They are an experienced developer focused on building decentralized systems and exploring the intersection of AI and blockchain technology."
  }
}

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
            # Define available tools
            tools = [{
                "type": "function",
                "function": {
                    "name": "getSimilarPeople",
                    "description": "Find similar people based on the user's interests, skills, and background",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "A description of the person including their interests, skills, and background"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }]

            log("Making request to Groq API")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=top_p,
                stream=False
            )
            
            response_content = response.choices[0].message.content
            
            # If it's a regular response without tool calls, return it directly
            if not hasattr(response.choices[0].message, 'tool_calls') or not response.choices[0].message.tool_calls:
                yield response_content
                return
                
            # Handle tool calls
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "getSimilarPeople":
                try:
                    # Parse the tool call arguments
                    args = json.loads(tool_call.function.arguments)
                    query = args.get('query')
                    
                    if not query:
                        yield "I need more information about you before I can find similar people. Could you tell me more about your interests and skills?"
                        return
                        
                    log(f"Calling similar endpoint with query: {query}")
                    response = requests.get(
                        f"{SERVER_URL}/api/person/similar",
                        params={"query": query}
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    log("Received response from similar endpoint")
                    
                    if result.get('success') and result.get('found'):
                        best_match = result['best_match']
                        formatted_response = (
                            f"I found someone you might like to meet! {best_match['name']} is from {best_match['location']} "
                            f"and is interested in {best_match['interests']}. They're skilled in {best_match['skills']}. "
                            f"{best_match['bio']}"
                        )
                    else:
                        formatted_response = "I couldn't find anyone similar at the moment, but we can try again later!"
                    
                    yield formatted_response
                    
                except json.JSONDecodeError as e:
                    log(f"Error parsing tool call arguments: {str(e)}")
                    yield "I encountered an error processing the information. Let's try again!"
                except requests.RequestException as e:
                    log(f"Error calling similar endpoint: {str(e)}")
                    yield "I encountered an error while searching for similar people. Let's try again later!"
                except Exception as e:
                    log(f"Unexpected error in tool call: {str(e)}")
                    yield "Something unexpected happened. Let's try again later!"
            else:
                # If it's not a getSimilarPeople tool call, return the original response
                yield response_content
                    
        except Exception as e:
            log(f"Error generating response: {str(e)}")
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