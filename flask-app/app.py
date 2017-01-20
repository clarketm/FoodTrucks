import os
import sys
import time
import re
import base64

import requests
from elasticsearch import Elasticsearch, exceptions
from flask import Flask, jsonify, request, render_template

if os.getenv('BONSAI_URL'):
    bonsai = os.getenv('BONSAI_URL')
    auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
    host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')
    es_header = [{
        'host': host,
        'port': 443,
        'use_ssl': True,
        'http_auth': (auth[0],auth[1])
    }]
    es = Elasticsearch(es_header)
else:
    es = Elasticsearch('es')

app = Flask(__name__)


def load_data_in_es():
    """ creates an index in elasticsearch """
    url = "http://data.kingcounty.gov/resource/gkhn-e8mn.json"
    r = requests.get(url)
    data = r.json()
    print "Loading data in elasticsearch ..."
    for id, truck in enumerate(data):
        res = es.index(index="bellevuedata", doc_type="truck", id=id, body=truck)
    print "Total trucks loaded: ", len(data)


def safe_check_index(index, retry=20):
    """ connect to ES with retry """
    if not retry:
        print "Out of retries. Bailing out..."
        sys.exit(1)
    try:
        status = es.indices.exists(index)
        return status
    except exceptions.ConnectionError as e:
        print "Unable to connect to ES. Retrying in 20 secs..."
        time.sleep(60)
        safe_check_index(index, retry - 1)


def check_and_load_index():
    """ checks if index exits and loads the data accordingly """
    if not safe_check_index('bellevuedata'):
        print "Index not found..."
        load_data_in_es()


###########
### APP ###
###########
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/debug')
def test_es():
    resp = {}
    try:
        msg = es.cat.indices()
        resp["msg"] = msg
        resp["status"] = "success"
    except:
        resp["status"] = "failure"
        resp["msg"] = "Unable to reach ES"
    return jsonify(resp)


def format_fooditems(string):
    items = [x.strip().lower() for x in string.split(":")]
    return items


@app.route('/search')
def search():
    key = request.args.get('q')
    if not key:
        return jsonify({
            "status": "failure",
            "msg": "Please provide a query"
        })
    try:
        res = es.search(
            index="bellevuedata",
            body={
                "query": {"match": {"name": key}},
                "size": 750  # max document size
            })
    except Exception as e:
        return jsonify({
            "status": "failure",
            "msg": "error in reaching elasticsearch"
        })
    # filtering results
    vendors = set([x["_source"]["name"] for x in res["hits"]["hits"]])
    temp = {v: [] for v in vendors}
    fooditems = {v: "" for v in vendors}
    for r in res["hits"]["hits"]:
        name = r["_source"]["name"]
        if 'latitude' in r["_source"] and 'longitude' in r["_source"]:
            truck = {
                # "hours": r["_source"].get("dayshours", "NA"),
                # "schedule": r["_source"].get("schedule", "NA"),
                "address": r["_source"].get("address", "NA"),
                # "location": r["_source"]["location"]
                "location": {
                    'latitude': r["_source"].get('latitude'),
                    'longitude': r["_source"].get('longitude'),
                }
            }
            fooditems[name] = r["_source"]["name"]
            temp[name].append(truck)

    # building up results
    results = {"trucks": []}
    for v in temp:
        results["trucks"].append({
            "name": v,
            "fooditems": format_fooditems(fooditems[v]),
            "branches": temp[v],
            # "drinks": fooditems[v].find("COLD TRUCK") > -1
        })
    hits = len(results["trucks"])
    locations = sum([len(r["branches"]) for r in results["trucks"]])

    return jsonify({
        "trucks": results["trucks"],
        "hits": hits,
        "locations": locations,
        "status": "success"
    })


def start(port=5000):
    check_and_load_index()
    # app.run(debug=True) # for dev
    app.run(host='0.0.0.0', port=port)  # for prod


if __name__ == "__main__":
    start()
