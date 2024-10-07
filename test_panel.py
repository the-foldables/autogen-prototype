from time import sleep
import panel as pn

pn.extension(design="material")

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    sleep(.1)
    if user == "User":
        yield {
            "user": "arm_bot",
            "avatar": "🦾",
            "object": "Hey, leg_bot! Did you hear the user?",

        }
        instance.respond()
    elif user == "arm_bot":
        user_message = instance.objects[-2]
        user_contents = user_message.object
        yield {
            "user": "leg_bot",
            "avatar": "🦿",
            "object": f'Yeah! They said "{user_contents}"'
        }

def callback_simple(contents: str, user: str, instance: pn.chat.ChatInterface):
    message = f"Echoing {user}: {contents}"
    return message

chat_interface = pn.chat.ChatInterface(callback=callback, callback_exception='verbose')
chat_interface.send(
    "Enter a message in the TextInput below and receive an echo!",
    user="System",
    respond=False,
)
chat_interface.servable()
