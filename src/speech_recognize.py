from pydub import AudioSegment
import speech_recognition as sr
import os
import tempfile

class Transcriber:
    def __init__(self, language):
        self.recognizer = sr.Recognizer()
        self.language = language

    def transcribe(self, ogg_path):
        try:
            fd, wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            audio = AudioSegment.from_file(ogg_path, format="ogg")
            audio.export(wav_path, format="wav")

            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=self.language)

            os.remove(wav_path)
            return text
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
