import csv
import json


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
