import json
import requests
import time
import urllib3
import random
from flask import Flask  # , jsonify
from urllib import parse
application = app = Flask(__name__)
namespace = "flask-example"
token = open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hellso There!</h1>"


@app.route("/healthz")
def healthz():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/jobs")
def jobs():
    from uuid import uuid4
    tag = random.choice(["latest", "5", "5.26", "5.22"])
    name = "pi-" + str(uuid4())
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name
        },
        "spec": {
            "parallelism": 1,
            "completions": 1,
            "template": {
                "metadata": {
                    "name": name
                },
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": "openshift/perl" + ":" + tag,
                            "imagePullPolicy": "IfNotPresent",
                            "command": [
                                "perl",
                                "-v"
                                # "-Mbignum=bpi",
                                # "-wle",
                                # "print bpi(3)"
                            ]
                        }
                    ],
                    "restartPolicy": "OnFailure"
                }
            }
        }
    }
    url = "https://192.168.99.100:8443/"
    headers = {
        # Anything but my local minishift token
        "Authorization": "Bearer " + token
    }
    friv = {"headers": headers, "verify": False}
    req = requests.post(
        url + "apis/batch/v1/namespaces/" + namespace + "/jobs",
        data=json.dumps(job),
        **friv
    )
    if not req.ok:
        raise Exception(req.text)
    else:
        resp = req.json()

        def get_job():
            return requests.get(
                url + "apis/batch/v1/namespaces/" + namespace + "/jobs/" + resp['metadata']['name'],
                **friv
            ).json()

        def check_job(job):
            if not job['status']:
                return False
            if 'completionTime' not in resp['status']:
                return False
            return True

        while not check_job(resp):
            time.sleep(0.1)
            resp = get_job()
        base_api = url + "api/v1/namespaces/" + namespace
        data = requests.get(
            base_api + "/events?fieldSelector=involvedObject.name" + parse.quote("=" + resp["metadata"]["name"] + ",involvedObject.namespace=" + namespace + ",involvedObject.kind=Job,involvedObject.uid=" + resp["metadata"]["uid"]),  # noqa
            **friv
        )
        pod = data.json()['items'][0]['message'].split("Created pod: ")[1]
        pod_data = requests.get(base_api + "/pods/" + pod + "/log", **friv)
        return "<body><pre>" + pod_data.text + "</pre></body>"


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    application.run(host='0.0.0.0')


# oc policy add-role-to-user edit -z default
