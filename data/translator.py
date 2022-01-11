from googletrans import Translator

translator = Translator()


def translate(text):
    return translator.translate(str(text), dest='ru').text
