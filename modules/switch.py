# Switch the current running application
import json
def switch(target):
    target = target.replace('.x', '')
    with open("database/see.json") as f:
        data = json.load(f)
        data['default_app'] = target


    with open("database/see.json", "w") as f:
        json.dump(data, f)
