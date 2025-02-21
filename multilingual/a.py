!pip install googletrans
pip install googletrans==4.0.0-rc1
from googletrans import Translator, LANGUAGES

# Get user input
text = input("What text would you like to translate? >> ")

# Create a translator object
translator = Translator()

# Loop through all available languages and translate
for code, language in LANGUAGES.items():
    try:
        translation = translator.translate(text, dest=code)
        print(f"{language.capitalize()} ({code}): {translation.text}")
    except Exception as e:
        print(f"Error translating to {language} ({code}): {e}")
