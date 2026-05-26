#GENERALFUNCTIONS

def check_float(data):
    """checks if data fed is datatype 'float'"""
    try:
        float(data)
        return True
    except (ValueError, TypeError):
        return False

def check_key(dictionary, key):
    try:
        i = dictionary[key]
        return True
    except KeyError:
        return False
