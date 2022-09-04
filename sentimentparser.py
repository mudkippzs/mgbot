"""
1. Create a Sentiment Analyzer using GPT3 that takes a text string as input and returns a json or tuple as output.
2. The output should be a structured set of values in the range of -1.0 to 1.0 and include the dimensions: joy, fear, disgust, sadness, anger, surprise.

JSON output example:
{ "joy": -0.9969352437035242, "fear": -0.4081494313347054, "disgust": -0.20717554409011085, "sadness": 0.7191569540831366, "anger": -0.46032758038040944, "surprise": -0.8758254105195562 }

Tuple output example: 
(0.5, 0.7, 0.3, -0.5, -0.8, 0.9)
"""
import openai
import json
import random
from utils import *

config = load_json_config("config.json")
openai.api_key = config["jarvis_key"]


def get_sentiment(text):
    prompt = "1. Analyze the sentiment and emotional content in the following text string. 2.Return a scoring as a csv string. Use the following template: joy: 0.0, fear: 0.0, disgust: 0.0, sadness: 0.0, anger: 0.0, surprise: 0.0. Bound values in the range of -1.0 to 1.0." + \
        f"\n\nTEXT STRING: {text}"
    response = openai.Completion.create(
        model="text-curie-001",
        prompt=prompt,
        temperature=0.90,
        max_tokens=500,
        top_p=1,
        frequency_penalty=1.91,
        presence_penalty=1.61
    )
    sentiment = response['choices'][0]['text']
    return sentiment


def format_sentiment(sentiment_string):
    d = {k[0]: k[1].strip() for k in [v.split(":") for v in [s.strip()
                                                             for s in sentiment_string.split(",")]]}
    return d


def get_sentiment_score(text):
    validation = False
    timeout = 0
    while validation == False:
        if timeout > 3:
            break
        timeout += 1
        sentiment = get_sentiment(text)
        try:
            sentiment = format_sentiment(sentiment)
        except (IndexError, ValueError):
            continue
        else:
            validation = validate_sentiment(sentiment)

    if validation == False:
        return
    #print(f"\n\n\nText: {text}\n\nSentiment: {sentiment}")

    return sentiment['joy'], sentiment['fear'], sentiment['disgust'], sentiment['sadness'], sentiment['anger'], sentiment['surprise']


def validate_sentiment(sentiment):
    if len(sentiment) != 6:
        #print(
        #    f"Incorrect sentiment object size. Expected: 6, Got: {len(sentiment)}")
        return False
    emotionlist = ['joy', 'fear', 'disgust', 'sadness', 'anger', 'surprise']
    for emotion in emotionlist:
        if emotion in sentiment.keys():
            continue
        else:
            #print(f"Missing: {emotion} from sentiment object.")
            return False

    for k, v in sentiment.items():
        try:
            if float(v) > 1.0 or float(v) < -1.0:
                #print("Sentiment value out of range")
                return False
        except ValueError:
            return False
    return True


if __name__ == "__main__":
    test_strings = [
        "I am happy to be here today.",
        "It looks interesting but the smell is so bad.",
        "You suck, you're not very useful.",
        "Why did the chicken cross the road?.",
        "It's really quite shrimple.",
        "The frog is sitting on the log.",
        "I'm not satisfied, you've hurt me.",
        "The dingus over there did it lol",
        "Is that really how you think?", "Relatable as fuck",
        "Well, if you paint your nails, you'll look like a faggot so.",
        "tale as old as time",
        "It's true",
        "girl leave boy",
        "Unless I'm just seeing the wrong thing in that last imagine.",
        "boy stick a 12 gauge in his fucking mouth",
        "Yep",
        "Someday soon 😊",
        "this is why im outside of the entire thing",
        "seen too many of my old bros nearly neck or shoot themselves over women",
        "Be a bro, give them a hand(y).",
        "i spent the better portion of my mid to late teens",
        "trying to make sure one of my old bros who got really fucked by life",
        "doesnt neck himself",
        "The key is to stop caring about your partners",
        "If you don't feel love then you'll be fine",
        "and i succeeded, he didnt neck himself, he grew out of it",
        "and now hes doing better",
        "and i am no longer needed",
        "A handy is a hand job mate. It was a sex joke.",
        "i know it was",
        "but you can abstract hand job to action that helps",
        "and that was my action that helped",
    ]
    for string in test_strings:
        score = get_sentiment_score(string)
        if score:
            print(score)
        else:
            print(f"Timeout Reached - Skipping: {string}")
