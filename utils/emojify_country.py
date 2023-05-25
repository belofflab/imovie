from data.config import MEDIA_URL
import json

def go(country: str) -> str:
    countries = country.split(',')
    emojies = json.loads(open(MEDIA_URL / 'country.json', 'r', encoding='utf-8').read())
    r_text = ""
    for cnt in countries:
        for text, emoji in emojies.items():
            if cnt.lower() in text:
                r_text += f"{cnt}{emoji} "
                break
    return r_text