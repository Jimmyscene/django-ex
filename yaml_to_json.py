import yaml
import json
base = "openshift/templates/flask."
with open(base + "yaml") as f:
    data = yaml.load(f.read())
    with open(base + "json", 'w+') as f2:
        json.dump(data, f2)