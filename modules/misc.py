import os
import json

def default_app():
    with open('database/see.json') as f:
        dic = json.load(f)
    return dic['default_app']

def list_apps():
    default_app_tmp = default_app()
    list_of_apps = os.listdir('program')
    new_l = []
    for x in list_of_apps:
        if x != "__pycache__" and x != default_app_tmp:
            new_l.append(x)
    return new_l