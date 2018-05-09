$ErrorActionPreference = "Stop"
$PROJECT_NAME = "flask-example"
python .\yaml_to_json.py
oc delete all --selector app=$PROJECT_NAME
oc delete secret --selector app=$PROJECT_NAME
oc new-app -f openshift/templates/flask.yaml -p SOURCE_REPOSITORY_URL=https://github.com/Jimmyscene/django-ex.git
# oc start-build $PROJECT_NAME