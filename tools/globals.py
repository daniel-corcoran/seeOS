import json
def getGlobalConfig():
    with open('database/see.json') as f:
        see_config = json.load(f)
    return see_config

def default_app():
    see_config = getGlobalConfig()
    default_app = see_config['default_app']
    return default_app