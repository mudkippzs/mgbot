import openai

from utils import *

def post_to_gpt3(payload, args=None):
    config = load_json_config("config.json")
    openai.api_key = config["ai_key"]

    if args == None:
        args = {
            'temp': 0.85,
            'max_tokens': 500,
            'top_p': 1.0,
            'fp': 0.125,
            'pp': 0.125,
        }

    return openai.Completion.create(
        model=config['ai_model_text'],
        prompt=payload,
        temperature=args['temp'],
        max_tokens=args['max_tokens'],
        top_p=args['top_p'],
        frequency_penalty=args['fp'],
        presence_penalty=args['pp']
    )