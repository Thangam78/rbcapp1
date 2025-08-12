# rbcapp1 Monitoring System

## Overview
This project provides a service monitoring solution for `rbcapp1`, which depends on three services:
- Apache HTTP Server (`apache2`)
- RabbitMQ (`rabbitmq-server`)
- PostgreSQL (`postgresql`)

The monitoring solution includes:
- A Python script to locally check service status and create JSON status files.
- A Flask REST API to expose service health status and insert data into Elasticsearch.
- An Ansible playbook to perform installation verification, disk space checking with alerts, and REST API based status checking.

---

## Prerequisites

- Elasticsearch instance accessible (default at `192.168.64.1:9200`)

- Ansible installed on the control machine

- Email system configured on hosts for disk space alerting (e.g., sendmail or postfix)

- Services (`apache2`, `rabbitmq-server`, `postgresql`) installed or installable

- Python 3.8 or higher

- Required Python packages:

  ```bash
  pip install requests psycopg2-binary pika flask elasticsearch
---

## Service Monitor Script (service_monitor.py)

- Usage
Run the script locally to check the status of services:
```bash
 python3 service_monitor.py
```

## REST API (app.py)
- Configuration
  Set environment variables to override defaults (optional):
  ```bash
  export ELASTICSEARCH_HOST=your_elasticsearch_host
  export ELASTICSEARCH_PORT=9200
  ```
## Run the API
  ```bash
  python3 app.py
  ```
## Available Endpoints
- GET /healthcheck — Returns status of all monitored services plus overall rbcapp1 status.
- GET /healthcheck/<service_name> — Returns status of a specific service (httpd, rabbitmq, postgresql, rbcapp1).
- POST /add — Accepts JSON data to manually add monitoring data to Elasticsearch.
- GET /history — Returns historical monitoring data from Elasticsearch. Supports service_name and size query parameters.

## Ansible Playbook (assignment.yml)
- Inventory File (inventory)
  ```ini
  localhost ansible_connection=local ansible_become=true
  ```
## Playbook Actions
- Run the playbook with the action variable set accordingly:
  Verify and install service (example installs apache2 if missing)
  ```bash
  ansible-playbook assignment.yml -i inventory -e action=verify_install
  ```
    Check disk usage on hosts and email alert if usage > 80%:
  ```bash
  ansible-playbook assignment.yml -i inventory -e action=check-disk
  ```
    Check status of rbcapp1 and list down services via REST API:
  ```bash
  ansible-playbook assignment.yml -i inventory -e action=check-status
  ```
## Configuration Notes
- Replace the alert_email variable inside the playbook with your email address to receive disk alerts.
- Replace rest_api_url in the playbook with the base URL of your running Flask REST API if not running on localhost.
- Modify the inventory file to include real hosts for production use.

## Troubleshooting & Tips
- Ensure Elasticsearch is running and accessible at the specified host and port.
- Verify all Python dependencies are installed in your virtual environment.
- Confirm Ansible inventory and playbook YAML syntax are correct (pay close attention to indentation and quoting).
- For email alerts, ensure the mail system (e.g., sendmail or postfix) is configured and working on your hosts.

