# rbcapp1 Monitoring System

This repository provides a complete monitoring solution for the **rbcapp1** application and its dependent services:

- Apache2 (httpd)
- RabbitMQ
- PostgreSQL

It includes a Python service monitoring script, a Flask REST API for status reporting and data insertion into Elasticsearch, and an Ansible playbook for automated service management and health checks.

---

## Contents

- `service_monitor.py` — Python script to monitor services locally and create JSON status files.
- `app.py` — Flask REST API exposing healthcheck endpoints and allowing data insertion into Elasticsearch.
- `assignment.yml` — Ansible playbook performing service installation verification, disk space checks with email alerts, and service status querying.
- `inventory` — Ansible inventory file for localhost testing.

---

## Prerequisites

- Python 3.8 or higher
- Required Python packages:

  ```bash
  pip install requests psycopg2-binary pika flask elasticsearch


Service Monitor Script
Usage
Run the script to check service statuses locally:

bash
Copy
Edit
python3 service_monitor.py
JSON status files are created in:

bash
Copy
Edit
~/rbcapp_monitoring_data/json_data/
