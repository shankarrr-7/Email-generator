import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from googletrans import Translator, LANGUAGES
import requests

# pyttsx3 requires system audio drivers — optional import for server deployment
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

def get_supported_languages():
    # Get the supported languages from googletrans
    return list(LANGUAGES.values())

def translate_text(text, target_language):
    try:
        translator = Translator()
        # Use the language code for translation
        lang_code = [code for code, name in LANGUAGES.items() if name == target_language][0]
        translated = translator.translate(text, dest=lang_code)
        return translated.text
    except Exception as e:
        print(f"Error during translation: {e}")
        return "Translation failed."

def text_to_speech(text):
    if not TTS_AVAILABLE:
        return False
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False


def send_email(sender_email, receiver_email, subject, body, attachment_paths=None):
    try:
        # Create a multipart message container
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach the email body as plain text
        message.attach(MIMEText(body, "plain"))

        # Attach files
        if attachment_paths:
            for path in attachment_paths:
                with open(path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                message.attach(part)

        # Use a secure connection (TLS)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            password = os.getenv("EMAIL_PASSWORD", "")
            if not password:
                print("Error: EMAIL_PASSWORD environment variable not set")
                return False
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False