from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import socket

app = Flask(__name__)
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "service-status"

@app.route("/add", methods=["POST"])
def add_status():
    data = request.json
    if not data or "service_name" not in data:
        return jsonify({"error": "Invalid payload"}), 400
    res = es.index(index=INDEX_NAME, document=data)
    return jsonify({"result": "added", "id": res['_id']}), 201

@app.route("/healthcheck", methods=["GET"])
def healthcheck_all():
    body = {
        "size": 1000,
        "query": {"match_all": {}}
    }
    res = es.search(index=INDEX_NAME, body=body)
    statuses = {}
    for hit in res['hits']['hits']:
        source = hit["_source"]
        svc = source.get("service_name")
        status = source.get("service_status")
        # Use latest status only
        if svc not in statuses or hit["_id"] > statuses[svc]["_id"]:
            statuses[svc] = {"status": status, "_id": hit["_id"]}
    result = {svc: val["status"] for svc, val in statuses.items()}
    # If any service is DOWN, overall is DOWN else UP
    overall = "UP" if all(s == "UP" for s in result.values()) else "DOWN"
    return jsonify({"overall_status": overall, "services": result})

@app.route("/healthcheck/<service_name>", methods=["GET"])
def healthcheck_service(service_name):
    body = {
        "size": 1,
        "query": {
            "match": {
                "service_name": service_name
            }
        },
        "sort": [{"_id": "desc"}]
    }
    res = es.search(index=INDEX_NAME, body=body)
    if res['hits']['total']['value'] == 0:
        return jsonify({"error": "Service not found"}), 404
    status = res['hits']['hits'][0]['_source']['service_status']
    return jsonify({service_name: status})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

