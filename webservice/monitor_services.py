#!/usr/bin/env python3
"""
Service Monitor Script for rbcapp1
Checks local systemd services: apache2, rabbitmq-server, postgresql
"""

import json
import os
import socket
import subprocess
from datetime import datetime


class ServiceMonitor:
    def __init__(self):
        # These must match your systemctl service names
        self.services = ['apache2', 'rabbitmq-server', 'postgresql']
        self.host_name = socket.gethostname()
        self.json_dir = os.path.join(os.path.expanduser('~'), 'rbcapp_monitoring_data', 'json_data')
        os.makedirs(self.json_dir, exist_ok=True)

    def check_service(self, service_name):
        """Check if a systemd service is active"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            status = result.stdout.strip()
            return status == "active"
        except Exception as e:
            print(f"Service check failed for {service_name}: {e}")
            return False

    def get_service_status(self, service_name):
        """Get UP/DOWN status for a given service"""
        return 'UP' if self.check_service(service_name) else 'DOWN'

    def get_rbcapp1_status(self):
        """Get overall status based on all services"""
        all_services_up = True
        service_statuses = {}

        for service in self.services:
            status = self.get_service_status(service)
            service_statuses[service] = status
            if status == 'DOWN':
                all_services_up = False

        rbcapp1_status = 'UP' if all_services_up else 'DOWN'
        return rbcapp1_status, service_statuses

    def create_json_payload(self, service_name, service_status):
        """Create JSON payload for a service"""
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        payload = {
            'service_name': service_name,
            'service_status': service_status,
            'host_name': self.host_name,
            'timestamp': timestamp
        }
        return payload

    def write_json_file(self, payload):
        """Write JSON payload to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        service_name = payload['service_name']
        filename = f"{service_name}-status-{timestamp}.json"
        filepath = os.path.join(self.json_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(payload, f, indent=2)

        print(f"Created file: {filename}")
        return filepath

    def monitor_services(self):
        """Monitor all services and create JSON files"""
        print(f"Starting service monitoring at {datetime.now()}")
        print(f"Host: {self.host_name}")
        print("-" * 50)

        rbcapp1_status, service_statuses = self.get_rbcapp1_status()

        json_files = []
        for service_name, status in service_statuses.items():
            payload = self.create_json_payload(service_name, status)
            filepath = self.write_json_file(payload)
            json_files.append(filepath)
            print(f"{service_name}: {status}")

        rbcapp1_payload = self.create_json_payload('rbcapp1', rbcapp1_status)
        rbcapp1_file = self.write_json_file(rbcapp1_payload)
        json_files.append(rbcapp1_file)

        print("-" * 50)
        print(f"rbcapp1 Overall Status: {rbcapp1_status}")
        print(f"JSON files created in: {self.json_dir}")

        return json_files, rbcapp1_status, service_statuses


def main():
    monitor = ServiceMonitor()
    json_files, rbcapp1_status, service_statuses = monitor.monitor_services()

    print("\n" + "=" * 50)
    print("MONITORING SUMMARY")
    print("=" * 50)
    print(f"rbcapp1 Status: {rbcapp1_status}")
    print("Service Details:")
    for service, status in service_statuses.items():
        print(f"  - {service}: {status}")
    print(f"\nJSON files created: {len(json_files)}")


if __name__ == "__main__":
    main()
