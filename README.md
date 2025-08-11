# rbcapp1 - Service Monitoring & Data Processing Setup

## Overview

This project provides:

1. Ansible playbook to install and configure three services:
   - Apache httpd
   - RabbitMQ
   - PostgreSQL

2. Python script (`monitor_services.py`) to monitor service status and write JSON status files.

3. Python Flask REST API (`webservice/app.py`) to accept status JSON and store/retrieve data in Elasticsearch.

4. Python script (`filter_sales.py`) to filter real estate sales data below average price per sqft.

---

## Setup Instructions

### Prerequisites

- Linux environment (VM or WSL on Mac)
- Python 3.x
- Ansible installed on control machine (Mac)
- Elasticsearch running locally or reachable at `http://localhost:9200`
- `sales-data.csv` placed under `data_processing/`

---

### 1. Install Services with Ansible

```bash
cd rbcapp1/ansible
ansible-playbook -i inventory playbook.yml --ask-become-pass

