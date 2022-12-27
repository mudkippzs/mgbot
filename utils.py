import csv
import json
import random
import requests

def validate_json(json_obj, fields):
    valid = False
    if not isinstance(json_obj, dict):
        return False
    
    for field in fields:
        if field in json_obj:
            valid = True

        try:
            if json_obj[field] in [True, False]:
                valid = True
        except:
            pass

    return valid

def load_json_config(file):
    """Read a json file to a dict."""
    with open(file) as f:
        return json.load(f)


def write_json_config(file, config):
    """Write a dict to a json file."""
    with open(file, 'w') as f:
        json.dump(config, f, indent=4)

def write_csv_file(file, data):
    with open(file, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(data)    

def get_highest_dict_key(dictionary):
    return max(dictionary, key=lambda k: dictionary[k])

def translate_string(string, language, api_key):    
    target_language = "en"
    source_language = language
    resultFormat = "text"
    url = "https://libretranslate.com/translate"
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "q": string,
        "source": source_language,
        "target": target_language,
        "format": "text",
        "api_key": "dcc0245d-bf43-4c82-b6d1-25d67b997678"
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    return response.json()["translatedText"]

def tenor(search_term, api_key, lmt=5):
        """Get a gif from Tenor based on a keyword string."""

        # get the top 8 GIFs for the search term
        r = requests.get(f"https://tenor.googleapis.com/v2/search?q={search_term}&key={api_key}&limit={lmt}")

        if r.status_code == 200:
            # load the GIFs using the urls for the smaller GIF sizes
            top_8gifs = json.loads(r.content)

            # get the top 8 results from the search results
            top_8gifs = top_8gifs["results"]

            random.shuffle(top_8gifs)

            # get the preview version of the GIF using the random integer we generated earlier to select a random result from the top 8
            preview_gif = top_8gifs[0]["media_formats"]["gif"]["url"]

            # send the gif in chat as an embed with a local source and title of our choosing
            embed = discord.Embed(title="eMGee responds...")
            embed.set_image(url=preview_gif)
            return embed
        return False

def get_emoji(emotion):
    if emotion == "neutral":
        return random.choice([
            "😐"
        ])

# Halloween Emojis

    # if emotion == "joy":
    #     return random.choice(["😀", "😁", "😂", "🤣", "😏", "😄", "🤪", "😋", "☺️", "😎", "😏", "🤠", "🤤", "🤗", "😌", "👾", "👾", "🧙", "🧙", "🎃"])
    # if emotion == 'fear':
    #     return random.choice(["😨", "😧", "😰", "😦", "😳", "😱", "🥶", "😥", "😓", "😧","👻", "👻", "🎃"])
    # if emotion == 'disgust':
    #     return random.choice(["🤢", "🤮", "😖", "😫", "😩", "😵‍💫", "😬", "😒", "🧟", "🧟", "🎃"])
    # if emotion == 'sadness':
    #     return random.choice(["😔", "😥", "😢", "😭", "🤧", "😭", "🥺", "😞", "🧚", "🧚", "🎃"])

    # if emotion == 'anger':
    #     return random.choice(["👿", "😡", "🤬", "😤", "👿", "😠", "💢", "🤖", "🤖", "🎃"])

    # if emotion == 'surprise':
    #     return random.choice(["🤯", "😲", "🙀", "😵", "🥴", "🧎‍♀️", "😵", "😮", "😯", "👽", "👽", "🧞", "🧞", "🎃"])

    if emotion == "joy":
        return random.choice(["😀", "😁", "😂", "🤣", "😏", "😄", "🤪", "😋", "☺️", "😎", "😏", "🤠", "🤤", "🤗", "😌", "🎅"])
    if emotion == 'fear':
        return random.choice(["😨", "😧", "😰", "😦", "😳", "😱", "🥶", "😥", "😓", "😧", "🎅"])
    if emotion == 'disgust':
        return random.choice(["🤢", "🤮", "😖", "😫", "😩", "😵‍💫", "😬", "😒", "🎅"])
    if emotion == 'sadness':
        return random.choice(["😔", "😥", "😢", "😭", "🤧", "😭", "🥺", "😞", "🎅"])

    if emotion == 'anger':
        return random.choice(["👿", "😡", "🤬", "😤", "👿", "😠", "💢", "🎅"])

    if emotion == 'surprise':
        return random.choice(["🤯", "😲", "🙀", "😵", "🥴", "🧎‍♀️", "😵", "😮", "😯", "🎅"])

FORMATTING_CHARS = {
    "COLOURS": {
        "BLACK": "\u001b[30m",
        "RED": "\u001b[31m",
        "GREEN": "\u001b[32m",
        "YELLOW": "\u001b[33m",
        "BLUE": "\u001b[34m",
        "MAGENTA": "\u001b[95m",
        "CYAN": "\u001b[106m",
        "WHITE": "\u001b[37m",
        "RESET": "\u001b[0m"
    },
    "STYLES": {
        "BOLD": "\u001b[1m",
        "UNDERLINE": "\u001b[4m",
        "BLINK": "\u001b[5m",
        "INVERT": "\u001b[7m",
        "RESET": "\u001b[0m"
    }
}
