import json


def is_json_serializable(obj):
    try:
        json.dumps(obj)
    except TypeError:
        return False
    return True
