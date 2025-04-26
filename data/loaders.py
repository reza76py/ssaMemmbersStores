import json
import os

def save_to_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def load_from_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return []
