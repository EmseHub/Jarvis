import elevenlabs

# elevenlabs.set_api_key("API-KEY")


def play_speech(question):

    try:
        # audio = generate(
        #     # api_key="YOUR_API_KEY", (Defaults to os.getenv(ELEVEN_API_KEY))
        #     text="Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!",
        #     voice="Rachel",
        #     model="eleven_multilingual_v2",
        # )

        audio = elevenlabs.generate(text=question, voice="Callum", model="eleven_multilingual_v2")

        # print(elevenlabs.voices())

        # voice = elevenlabs.clone(
        #     # api_key="YOUR_API_KEY", (Defaults to os.getenv(ELEVEN_API_KEY))
        #     name="Alex",
        #     description="An old American male voice with a slight hoarseness in his throat. Perfect for news",  # Optional
        #     files=["./sample_0.mp3", "./sample_1.mp3", "./sample_2.mp3"],
        # )

        # audio = elevenlabs.generate(text="Hi! I'm a cloned voice!", voice=voice)

        elevenlabs.save(audio, "elevenlabs_test.wav")

        elevenlabs.play(audio=audio, use_ffmpeg=True)

        print(f'"{question} erfolgreich generiert!')

    except elevenlabs.api.error.UnauthenticatedRateLimitError:
        print("Elevenlabs Limit erreicht!")

    except Exception as inst:

        print(type(inst))  # the exception type
        print(inst)  # __str__ allows args to be printed directly,
        return
