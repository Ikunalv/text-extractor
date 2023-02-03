import json


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def load_settings():
        file_path = "config/config.json"
        try:
            with open(file_path) as f:
                d = json.load(f)

        except:
            raise FileNotFoundError("Config file not found at path '{}'".format(file_path))
        print(" Loading configurations from file {} ...".format(file_path))
        return d
