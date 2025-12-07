"""
Complete Plain-Python Twilio Toolkit for Visuae Phoneline
========================================================
This single file includes:

1. EXTENSION HANDLER — simple Python logic to map extension → target
2. ROUTER — produces TwiML based on entered extension
3. TWIML UPLOADER — saves/updates a TwiML App in Twilio (so Twilio knows
   where your TwiML lives)

NO Flask. NO webserver. This is the simplest possible full chain.

Usage Steps:
------------
1. Host your TwiML somewhere (can be a static XML file or Twilio Function)
2. Set environment variables:
     TWILIO_ACCOUNT_SID
     TWILIO_AUTH_TOKEN
     VOICE_URL  ← the URL where Twilio should GET/POST to get your TwiML

3. Run:
     python phoneline_toolkit.py

This will:
- Generate TwiML for extension routing
- Upload or update a TwiML App in Twilio named "Visuae Phoneline"
- Bind your Twilio App so your numbers can point to it
"""

from twilio.twiml.voice_response import VoiceResponse, Gather, Dial
from twilio.rest import Client
import os

# -----------------------------------
# 1. EXTENSION MAP
# -----------------------------------
EXTENSIONS = {
    "100": "Ethan",
    "123": "Conall",
}

# -----------------------------------
# 2. TWIML GENERATORS (extension router)
# -----------------------------------

def generate_welcome_twiml():
    resp = VoiceResponse()
    gather = Gather(action="/route", num_digits=3, timeout=10)
    gather.say("Welcome to Visuae phone line. Please enter the three digit extension now.")
    resp.append(gather)
    resp.say("No input detected. Goodbye.")
    resp.hangup()
    return str(resp)

def route_extension(digits: str):
    resp = VoiceResponse()

    if digits in EXTENSIONS:
        name = EXTENSIONS[digits]
        dial = Dial()
        dial.client(name)
        resp.append(dial)
        return str(resp)

    resp.say("That extension does not exist.")
    resp.redirect("/voice")
    return str(resp)


# -----------------------------------
# XML GENERATOR (produces standalone .xml files)
# -----------------------------------
import pathlib

def save_xml(filename: str, xml_string: str):
    """Save TwiML as a plain XML file."""
    path = pathlib.Path(filename)
    path.write_text(xml_string, encoding="utf-8")
    print(f"Saved XML → {path.resolve()}")

# Generate two XML files: welcome.xml and route.xml template
if __name__ == "__main__":
    # Save the welcome prompt XML
    save_xml("welcome.xml", generate_welcome_twiml())

    # Save each extension's routing XML
    for ext, name in EXTENSIONS.items():
        xml = route_extension(ext)
        save_xml(f"route_{ext}.xml", xml)

# -----------------------------------
# 3. TWIML APP UPLOADER (sync to Twilio)
# -----------------------------------
TWILIO_ACCOUNT_SID = os.environ.get("AAD32813798C7A45196B19E88B55FF1F7")
TWILIO_AUTH_TOKEN = os.environ.get("D9A92A93100972DCBE44D4AECCCAA22E")
VOICE_URL = os.environ.get("")  # URL where your TwiML is hosted


def sync_twiml_app():
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        raise RuntimeError("Missing Twilio credentials.")
    if not VOICE_URL:
        raise RuntimeError("VOICE_URL environment variable is missing.")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    apps = client.applications.list(friendly_name="Visuae Phoneline")

    if apps:
        app = apps[0]
        updated = client.applications(app.sid).update(
            voice_url=VOICE_URL,
            voice_method="POST"
        )
        print("Updated existing TwiML App:", updated.sid)
    else:
        created = client.applications.create(
            friendly_name="Visuae Phoneline",
            voice_url=VOICE_URL,
            voice_method="POST"
        )
        print("Created new TwiML App:", created.sid)


# -----------------------------------
# Demo + uploader trigger
# -----------------------------------
if __name__ == "__main__":
    print("--- Welcome TwiML ---")
    print(generate_welcome_twiml())

    print("Routing Ethan (100)")
    print(route_extension("100"))

    print("--- Routing invalid extension ---")
    print(route_extension("000"))

    print("--- Syncing TwiML App to Twilio ---")
    sync_twiml_app()
    print("Done.")