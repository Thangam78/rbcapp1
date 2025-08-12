#!/usr/bin/env python3
"""
REST API for rbcapp1 Monitoring System
Provides endpoints for health checking and data insertion to Elasticsearch
"""

from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import os
from datetime import datetime
from monitor_services import ServiceMonitor  # Using systemctl-based version

app = Flask(__name__)

# Elasticsearch configuration
ES_HOST = os.getenv('ELASTICSEARCH_HOST', '192.168.64.1')
ES_PORT = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
ES_INDEX = 'rbcapp-monitoring'

# Initialize Elasticsearch client
es = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'])

# Initialize service monitor
monitor = ServiceMonitor()


def ensure_elasticsearch_index():
    """Ensure Elasticsearch index exists"""
    try:
        if not es.indices.exists(index=ES_INDEX):
            mapping = {
                "mappings": {
                    "properties": {
                        "service_name": {"type": "keyword"},
                        "service_status": {"type": "keyword"},
                        "host_name": {"type": "keyword"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
            es.indices.create(index=ES_INDEX, body=mapping)
            print(f"Created Elasticsearch index: {ES_INDEX}")
    except Exception as e:
        print(f"Error creating Elasticsearch index: {e}")


@app.route('/add', methods=['POST'])
def add_data():
    """POST /add — Adds monitoring data to Elasticsearch"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['service_name', 'service_status', 'host_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        response = es.index(index=ES_INDEX, body=data)
        return jsonify({
            'message': 'Data successfully added to Elasticsearch',
            'elasticsearch_id': response['_id'],
            'data': data
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/healthcheck', methods=['GET'])
def healthcheck_all():
    """GET /healthcheck — Get status of all services"""
    try:
        rbcapp1_status, service_statuses = monitor.get_rbcapp1_status()

        # Store each service status in Elasticsearch
        for service_name, status in service_statuses.items():
            payload = monitor.create_json_payload(service_name, status)
            es.index(index=ES_INDEX, body=payload)

        # Store overall status
        rbcapp1_payload = monitor.create_json_payload('rbcapp1', rbcapp1_status)
        es.index(index=ES_INDEX, body=rbcapp1_payload)

        return jsonify({
            'rbcapp1_status': rbcapp1_status,
            'services': service_statuses,
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/healthcheck/<service_name>', methods=['GET'])
def healthcheck_service(service_name):
    """GET /healthcheck/{serviceName} — Get status of specific service"""
    try:
        valid_services = monitor.services + ['rbcapp1']
        if service_name not in valid_services:
            return jsonify({
                'error': f'Invalid service name. Valid services: {valid_services}'
            }), 400

        if service_name == 'rbcapp1':
            status, _ = monitor.get_rbcapp1_status()
        else:
            status = monitor.get_service_status(service_name)

        payload = monitor.create_json_payload(service_name, status)
        es.index(index=ES_INDEX, body=payload)

        return jsonify({
            'service_name': service_name,
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """GET /history — Returns historical monitoring data"""
    try:
        service_name = request.args.get('service_name')
        size = int(request.args.get('size', 10))

        query = {
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        if service_name:
            query["query"] = {"match": {"service_name": service_name}}

        response = es.search(index=ES_INDEX, body=query)

        results = [hit['_source'] for hit in response['hits']['hits']]

        return jsonify({
            'total': response['hits']['total']['value'],
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'rbcapp1 Monitoring API',
        'version': '1.0',
        'endpoints': {
            'POST /add': 'Add monitoring data to Elasticsearch',
            'GET /healthcheck': 'Get status of all services',
            'GET /healthcheck/<service>': 'Get status of specific service',
            'GET /history': 'Get historical monitoring data'
        },
        'valid_services': monitor.services + ['rbcapp1']
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("Starting rbcapp1 Monitoring REST API...")
    print(f"Elasticsearch: {ES_HOST}:{ES_PORT}")
    print(f"Index: {ES_INDEX}")

    import time
    for i in range(30):
        try:
            if es.ping():
                print("✓ Elasticsearch is ready")
                break
        except:
            print(f"Waiting for Elasticsearch... ({i+1}/30)")
            time.sleep(2)
    else:
        print("✗ Could not connect to Elasticsearch")

    ensure_elasticsearch_index()

    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
