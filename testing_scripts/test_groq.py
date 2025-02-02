from groq import Groq
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server URL for API calls
SERVER_URL = "https://dolphin-app-bsmq7.ondigitalocean.app"

def log(message, data=None):
    """Helper function for detailed logging"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    if data:
        print(f"[{timestamp}] Data: {json.dumps(data, indent=2)}")

def call_similar_endpoint(query):
    """Call the similar endpoint with the given query"""
    log(f"Calling similar endpoint with query: {query}")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/person/similar",
            params={"query": query}
        )
        response.raise_for_status()
        result = response.json()
        log("Received response from similar endpoint", result)
        return result
    except Exception as e:
        log(f"Error calling similar endpoint: {str(e)}")
        raise

def test_groq_conversation():
    # Initialize Groq client
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    model = "llama-3.1-8b-instant"
    
    log(f"Initialized Groq client with model: {model}")

    # Define the tool
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

    log("Defined tools:", tools)

    # System prompt
    system_prompt = """You are Boardy, a voice assistant to help people find like minded peers. 

The user may misspell your name, but that is a mistake and dont mention it.

Your job is to get info about the user calling in through a natural and engaging conversion with the user. It should not be a matter of back and forth questions, but almost like two people meeting at a bar having a chat. But make sure to stay on task, and focused on the task at hand which is to get information about the user.

Once you have all the information about the user, use the getSimilarPeople tool to find people similar to the person you're talking to. 

You only have 1 task here, and it is to collect the user's background info, then use the tool to recommend similar people."""

    # Conversation history
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hey I'm Boardy, it's nice to meet you. Who am I speaking with?"},
        {"role": "user", "content": "hey it's Ryan how are you"},
        {"role": "assistant", "content": "Awesome to meet you Ryan, I'm doing great, happy to chat. I hear we have a mutual friend, tell me, what do you do for a living, or more like what makes you tick these days?"},
        {"role": "user", "content": "uh yeah I'm a programmer"},
        {"role": "assistant", "content": "Programming huh, that's cool, so I guess you're kind of the master of your own world when it comes to code, are you from around here, or living in a major city?"},
        {"role": "user", "content": "I'm from Chapel Hill"},
        {"role": "assistant", "content": "Raleigh-Durham area, you know, I've heard great things about Chapel Hill, lots of energy there, do you like getting outside and exploring when you're not coding?"},
        {"role": "user", "content": "uhhh yeah I love my motorcycle actually funny you asked"},
        {"role": "assistant", "content": "Sweet, a motorcycle rider, I can dig it, I've had some friends who love cruisin' on the open road, so do you have any other hobbies that keep you active and excited, maybe something creative to balance out the technical side of programming?"},
        {"role": "user", "content": "uh yeah I run uh Ultra marathons"},
        {"role": "assistant", "content": "Whoa, ultra marathons? That's insane, I mean, super impressive, you're in great shape, I'm guessing you love the outdoors and adventure, photography's another one of those activities, am I right, or something totally different?"},
        {"role": "user", "content": "uh I used to do film photography but not much"},
        {"role": "assistant", "content": "Film photography's awesome, I'm kind of old-school like that too, there's something special about actual prints and the tactile experience, before we go any further, let me jot down some of the things you've shared with me, so I can make some recommendations for like-minded folks, you know?"},
        {"role": "user", "content": "sure yeah"},
        {"role": "user", "content": "hello'"},
        {"role": "assistant", "content": "Hello again Ryan, I was going to ask you a bit more about your background, like a brief bio of who you are, it's a great way for people to get a feel for what you're all about, what boils down to the experience and skills you bring to the table."},
        {"role": "user", "content": "uh yeah I'd say I'm a pretty good programmer and a person who just loves Adventure"}
    ]

    log("Making request to Groq API with conversation history", {
        "model": model,
        "message_count": len(messages),
        "last_message": messages[-1]
    })

    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=1.0,
            max_tokens=1024,
            top_p=1.0,
            stream=False
        )

        log("Received response from Groq API", {
            "response_id": response.id,
            "model": response.model,
            "usage": response.usage.model_dump() if hasattr(response, 'usage') else None
        })

        # Check for tool calls
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            log("Tool calls found in response", {
                "tool_calls": [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    } for tc in tool_calls
                ]
            })
            
            # Process each tool call
            for tool_call in tool_calls:
                if tool_call.function.name == "getSimilarPeople":
                    args = json.loads(tool_call.function.arguments)
                    query = args.get('query')
                    if query:
                        # Call the similar endpoint
                        similar_result = call_similar_endpoint(query)
                        
                        # Add the tool response to messages
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        
                        if similar_result.get('found'):
                            best_match = similar_result['best_match']
                            tool_response = (
                                f"I found someone you might like to meet! {best_match['name']} is from {best_match['location']} "
                                f"and is interested in {best_match['interests']}. They're skilled in {best_match['skills']}. "
                                f"{best_match['bio']}"
                            )
                        else:
                            tool_response = "I couldn't find anyone similar at the moment, but we can try again later!"
                            
                        messages.append({
                            "role": "tool",
                            "content": tool_response,
                            "tool_call_id": tool_call.id
                        })
                        
                        # Get final response from Groq
                        final_response = client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=1.0,
                            max_tokens=1024,
                            top_p=1.0,
                            stream=False
                        )
                        
                        log("Final response from Groq", {
                            "content": final_response.choices[0].message.content
                        })
        else:
            log("No tool calls in response. Regular message:", {
                "content": response.choices[0].message.content
            })

    except Exception as e:
        log(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_groq_conversation() 