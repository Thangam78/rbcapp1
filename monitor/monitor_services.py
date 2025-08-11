#!/usr/bin/env python3
import json
import subprocess
import socket
from datetime import datetime

SERVICES = ["apache2", "rabbitmq-server", "postgresql"]

def check_service_status(service_name):
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        status = "UP" if result.stdout.strip() == "active" else "DOWN"
    except Exception:
        status = "DOWN"
    return status

def main():
    hostname = socket.gethostname()
    for service in SERVICES:
        status = check_service_status(service)
        data = {
            "service_name": service,
            "service_status": status,
            "host_name": hostname
        }
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{service}-status-{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Wrote status for {service} to {filename}")

if __name__ == "__main__":
    main()

