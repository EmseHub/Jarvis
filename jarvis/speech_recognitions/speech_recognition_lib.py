import speech_recognition as sr

from chatbot import settings
from helpers.helpers import play_audio_file


sr_recognizer = sr.Recognizer()
input_device_index = settings.get("input_device_index")

# Mikrofone auflisten
# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     if name.startswith("Mikrofon"):
#         print(f'Name des Mikrofons: "{name}" ------ Index: {index}')


def recognize_speech():
    audio_as_text = ""
    try:
        with sr.Microphone(input_device_index) as mic_source:

            # wait for a second to let the recognizer adjust the energy threshold based on the surrounding noise level

            # sr_recognizer.adjust_for_ambient_noise(mic_source, duration=0.5)

            print("Aufnahme läuft...")
            play_audio_file("jarvis/assets/listening.wav", is_blocking=True)

            audio_input = sr_recognizer.listen(mic_source, timeout=None, phrase_time_limit=4)
            print("Spracheingabe erkannt, starte Recognition...")

            audio_as_text = sr_recognizer.recognize_google(audio_input, language="de-DE")
            # audio_as_text = sr_recognizer.recognize_google_cloud(audio_input, language="de-DE")
            audio_as_text = audio_as_text.strip()
            print("Erkannte Spracheingabe: ", audio_as_text)

    except sr.RequestError as e:
        print(
            "Request gescheitert: Zur Spracheingabe konnten keine Ergebnisse angefordert werden (Key ungültig? Besteht keine Verbindung zum Internet?):",
            e,
        )

    except sr.UnknownValueError as e:
        print("Keine Worte in Spracheingabe ermittelt...")
        # print("UnknownValueError")

    except sr.WaitTimeoutError as e:
        print("Keine Spracheingabe... (Timeout)")

    except Exception as e:
        print("Unerwarteter Fehler bei der Spracherkennung:", e)

    finally:
        return audio_as_text
