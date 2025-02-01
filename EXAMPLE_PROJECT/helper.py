import threading
import json

lock = threading.Lock()


def manage_chat_history(uuid, content, role):
    with lock:
        try:
            with open('chat_history.json', 'r') as file:
                chat_history = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            chat_history = {}

        entry = {"content": content, "role": role}
        if uuid in chat_history:
            chat_history[uuid].append(entry)
        else:
            chat_history[uuid] = [entry]

        with open('chat_history.json', 'w') as file:
            json.dump(chat_history, file, indent=4)


def get_chat_history(uuid):
    with lock:
        try:
            with open('chat_history.json', 'r') as file:
                chat_history = json.load(file)
            return chat_history.get(uuid, [])
        except (FileNotFoundError, json.JSONDecodeError):
            return [
            ]  # Return an empty list if file is not found or JSON is invalid
