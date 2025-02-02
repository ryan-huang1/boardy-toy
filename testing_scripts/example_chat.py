from llm import LLMGeneration

def main():
    # Initialize the LLM generation class
    llm = LLMGeneration()
    
    # Initialize conversation history with system prompt
    messages = [
        {
            "role": "system",
            "content": llm.get_system_prompt()
        },
        {
            "role": "assistant",
            "content": "Hey I'm Boardy, it's nice to meet you. Who am I speaking with?"
        }
    ]
    
    print("\n=== Starting Conversation ===")
    print("Assistant: Hey I'm Boardy, it's nice to meet you. Who am I speaking with?")
    print("\nType 'quit' to end the conversation")
    
    while True:
        # Get user input
        user_message = input("\nYou: ").strip()
        
        # Check if user wants to quit
        if user_message.lower() == 'quit':
            print("\nEnding conversation. Goodbye!")
            break
            
        # Add user message to history
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate and stream response
        print("Assistant: ", end="", flush=True)
        response = llm.generate_response(messages)
        assistant_message = ""
        
        for chunk in response:
            print(chunk, end="", flush=True)
            assistant_message += chunk
            
        # Add assistant's response to history
        messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        print("\n")

if __name__ == "__main__":
    main() 