import os
from io import BytesIO
from gtts import gTTS

from helpers.helpers import play_audio_file


def speak_text_OLD(text):
    # https://gtts.readthedocs.io/en/latest/module.html#playing-sound-directly
    mp3_fp = BytesIO()
    tts = gTTS(text=text, lang="de", slow=False)
    tts.write_to_fp(mp3_fp)
    # Load `mp3_fp` as an mp3 file in
    # the audio library of your choice
    # play_audio_file(mp3_fp)


def speak_text(text, is_blocking=True):
    tts = gTTS(text=text, lang="de", tld="es", slow=False)
    # audiofile_path = "tts.mp3"
    audiofile_path = os.path.dirname(__file__) + "_tts.mp3"
    tts.save(audiofile_path)
    play_audio_file(audiofile_path, is_blocking=is_blocking)
    os.remove(audiofile_path)
