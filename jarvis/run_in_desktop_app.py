import json
import tkinter
import struct
import time

import pvporcupine
import pyaudio

from helpers.helpers import get_random_item_in_list
from chatbot import settings, get_response
from nlu_pipeline.intent_matching import intents_runtime
from speech_recognitions.speech_recognition_lib import recognize_speech
from speech_synthesis.local import pyttsx_lib
from speech_synthesis.api import gtts_lib


input_device_index = settings.get("input_device_index")


def get_intent_responses(tag_name):
    return next(intent for intent in intents_runtime if intent["tag"] == tag_name).get("responses")


wake_word_responses = get_intent_responses("wake_up")
exit_assistant_responses = get_intent_responses("exit_assistant")
farewell_responses = get_intent_responses("farewell")

# speak_text = gtts_lib.speak_text
speak_text = pyttsx_lib.speak_text


def conversation_flow():
    tagged_tokens = intent = state_running_task = {}

    speak_text(get_random_item_in_list(wake_word_responses))

    while True:
        # message = input().strip()
        message = recognize_speech()

        if not message:
            continue

        elif message.lower() == "task":
            print(json.dumps(state_running_task, indent=4))
            continue

        elif message.lower() == "tokens":
            print(json.dumps(tagged_tokens, indent=4))
            continue

        elif message.lower() == "exit":
            exit_msg = f"{get_random_item_in_list(exit_assistant_responses)} {get_random_item_in_list(farewell_responses)}"
            print(f"> {exit_msg}")
            speak_text(exit_msg)
            return False

        response, diagnostic, is_exit_assistant = get_response(message)

        tagged_tokens = diagnostic.get("tagged_tokens")
        intent = diagnostic.get("intent")
        state_running_task = diagnostic.get("state_running_task")

        print("---Gefundener Intent---\n", intent.get("tag"))

        if is_exit_assistant:
            exit_msg = f"{response} {get_random_item_in_list(farewell_responses)}"
            print(f"> {exit_msg}")
            speak_text(exit_msg)
            return False

        print(f"> {response}")
        speak_text(response)

        if not state_running_task:
            return True


def run_wake_word_detection():

    my_porcupine = None
    my_py_audio = None
    audio_stream = None

    print("---Wake-Word-Detection läuft---")

    try:
        keyword_paths = ["jarvis/speech_recognitions/pv_keyword_files/jarvis_windows.ppn"]
        my_porcupine = pvporcupine.create(keyword_paths=keyword_paths)
        # my_porcupine = pvporcupine.create(keywords=["jarvis"])
        my_py_audio = pyaudio.PyAudio()

        # pvporcupine.KEYWORDS

        # TODO Audio-Geräte auflisten und auswahl ermöglichen bzw. abbrechen, wenn kein Audio-Device mit Input-Channel

        # audio_device_count = my_py_audio.get_device_count()
        # print(audio_device_count)

        # default_input_device_info = my_py_audio.get_default_input_device_info()
        # default_input_device_name = default_input_device_info.get("name")
        # default_input_device_index = default_input_device_info.get("index")
        # print("Name des Default-Mikrofons: ", default_input_device_name)

        # available_audio_devices = []
        # for index in range(audio_device_count):
        #     available_audio_devices.append(my_py_audio.get_device_info_by_index(index))

        # available_input_devices = [
        #     input_device
        #     for input_device in available_audio_devices
        #     if input_device.get("maxInputChannels") > 0
        # ]

        # if len(available_input_devices) < 2:
        #     print("Kein Mikrofon angeschlossen. Beende Programm.")
        #     return

        # print("available_input_devices:\n", json.dumps(available_input_devices, indent=4))

        # Open an audio stream for the wake word detector
        audio_stream = my_py_audio.open(
            rate=my_porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=my_porcupine.frame_length,
        )

        iteration_count = 0

        while True:

            # if iteration_count > 500:
            #     speak_text("Beende System wegen Timeout.")
            #     break

            iteration_count += 1
            # Read a single audio frame from the stream
            pcm = audio_stream.read(my_porcupine.frame_length)
            # Convert the PCM data to a list of samples
            pcm = struct.unpack_from("h" * my_porcupine.frame_length, pcm)
            # Process the audio frame and get the keyword index
            keyword_index = my_porcupine.process(pcm)

            # print(keyword_index)

            # Kein Treffer ist -1
            if keyword_index >= 0:
                print("---Wake-Word erkannt---")
                is_continue_listening = conversation_flow()

                if is_continue_listening:
                    time.sleep(1)
                    print("---Wake-Word-Detection läuft---")
                else:
                    break

    except Exception as e:
        print(e)

    finally:
        if my_porcupine is not None:
            my_porcupine.delete()

        if audio_stream is not None:
            audio_stream.close()

        if my_py_audio is not None:
            my_py_audio.terminate()


def run_chatbot_in_desktop_app_BAK():

    tagged_tokens = intent = state_running_task = {}

    opening_messsage = (
        "Okay, lass uns per Terminal chatten!\n"
        + '[Eingabe "task": Stand des aktuell bearbeiteten Tasks ausgeben]\n'
        + '[Eingabe "tokens": Ermittelte Tokens der letzten Nachricht ausgeben]\n'
        + '[Eingabe "exit": Chat beenden]'
    )
    print(opening_messsage)

    while True:
        # message = input().strip()
        message = recognize_speech()

        if not message:
            continue

        elif message.lower() == "task":
            print(json.dumps(state_running_task, indent=4))

        elif message.lower() == "tokens":
            print(json.dumps(tagged_tokens, indent=4))
            continue

        elif message.lower() == "exit":
            print("> Danke! Bis bald!")
            break

        response, diagnostic = get_response(message)

        tagged_tokens = diagnostic.get("tagged_tokens")
        intent = diagnostic.get("intent")
        state_running_task = diagnostic.get("state_running_task")

        print("---Gefundener Intent---\n", intent.get("tag"))

        print("> " + response)
        pyttsx_lib.speak_text(response)
        # gtts_lib.speak_text(response)


if (__name__) == "__main__":
    # run_chatbot_in_desktop_app()

    # print(pvporcupine.KEYWORDS)

    run_wake_word_detection()

    # window = tkinter.Tk()

    # window.title("Wikipedia")
    # window.geometry("800x400")
    # label = tkinter.Label(window, text="J.A.R.V.I.S.")
    # label.pack(side="top", expand=1, fill="x")  # Anordnung durch Place-Manager

    # button = tkinter.Button(window, text="OK", command=window.destroy)
    # button.pack(side="bottom")

    # window.mainloop()
