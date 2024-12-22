import pyttsx4


engine = pyttsx4.init()
engine.setProperty("rate", int(engine.getProperty("rate")) * 1.05)
# engine.setProperty("volume", int(engine.getProperty("volume")) * 0.75)
voices = engine.getProperty("voices")
# for voice in voices:
#     print(voice.id)
engine.setProperty("voice", voices[0].id)


def speak_text(text):
    # engine = pyttsx4.init()
    engine.say(text)
    engine.runAndWait()
