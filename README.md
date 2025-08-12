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
