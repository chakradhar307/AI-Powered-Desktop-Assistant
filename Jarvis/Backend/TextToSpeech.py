import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-JennyNeural")  # Default voice if not set

async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate audio file using edge_tts
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def TTS(Text, func=lambda r=None: True):
    try:
        asyncio.run(TextToAudioFile(Text))
        pygame.mixer.init()
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish or be interrupted by `func`
        while pygame.mixer.music.get_busy():
            if not func():
                break
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error in TTS: {e}")
    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    # Split long text into manageable chunks
    Data = str(Text).split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Data[:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    # Ensure the `Data` directory exists
    if not os.path.exists("Data"):
        os.makedirs("Data")

    while True:
        text_input = input("Enter the text: ")
        if text_input.strip().lower() == "exit":
            print("Exiting program.")
            break
        TextToSpeech(text_input)
