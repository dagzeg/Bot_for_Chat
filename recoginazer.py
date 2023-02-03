import speech_recognition as sr
import os
import ffmpeg
import subprocess
from wave import Wave_read

# Класс для перевода голоса в текст
class Сonvect:

    def __init__ (self, path_to_file: str, language: str = "ru-Ru"):
        self.language = language # назначение языка
        subprocess.run(['ffmpeg', '-v', 'quiet', '-i', path_to_file, path_to_file.replace('.ogg', '.wav')]) # преобразование скаченного файла в формат wav с помощью утилиты ffmpeg
        self.wav_file = path_to_file.replace('.ogg', '.wav') #замена расширения у файла

    def audio_to_text(self) -> str:
        rec = sr.Recognizer() #класс распознования

        with sr.AudioFile(self.wav_file) as source: # берем преобразованный файл
            audio = rec.record(source) # записываем в класс speech_recognition.AudioData
            rec.adjust_for_ambient_noise(source, duration=0.5) # фильтр для шума
        return rec.recognize_google(audio, language = self.language) # получаем результат перевода текста с помощью библиотеки google и возвращаем в функцию
# удаляем расшифрованный файл
    def __del__(self):
        os.remove(self.wav_file)
