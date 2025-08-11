#!/usr/bin/env python3
"""
Service Monitor Script for rbcapp1
Monitors httpd, rabbitmq, and postgresql services
"""

import json
import os
import socket
import subprocess
import time
from datetime import datetime
import requests
import psycopg2
import pika


class ServiceMonitor:
    def __init__(self):
        self.services = ['httpd', 'rabbitmq', 'postgresql']
        self.host_name = socket.gethostname()
        self.json_dir = os.path.join(os.path.expanduser('~'), 'rbcapp_monitoring_data', 'json_data')
        os.makedirs(self.json_dir, exist_ok=True)
        
    def check_httpd_service(self):
        """Check if httpd service is running"""
        try:
            # Try to connect to httpd service
            httpd_host = os.getenv('HTTPD_HOST', 'httpd')
            httpd_port = int(os.getenv('HTTPD_PORT', '80'))
            
            response = requests.get(f'http://{httpd_host}:{httpd_port}', timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"HTTPd check failed: {e}")
            return False
    
    def check_rabbitmq_service(self):
        """Check if RabbitMQ service is running"""
        try:
            rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
            rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
            
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
            )
            connection.close()
            return True
        except Exception as e:
            print(f"RabbitMQ check failed: {e}")
            return False
    
    def check_postgresql_service(self):
        """Check if PostgreSQL service is running"""
        try:
            postgres_host = os.getenv('POSTGRES_HOST', 'postgresql')
            postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
            postgres_user = os.getenv('POSTGRES_USER', 'postgres')
            postgres_password = os.getenv('POSTGRES_PASSWORD', 'password')
            
            conn = psycopg2.connect(
                host=postgres_host,
                port=postgres_port,
                user=postgres_user,
                password=postgres_password,
                database='postgres',
                connect_timeout=5
            )
            conn.close()
            return True
        except Exception as e:
            print(f"PostgreSQL check failed: {e}")
            return False
    
    def get_service_status(self, service_name):
        """Get status of a specific service"""
        if service_name == 'httpd':
            return 'UP' if self.check_httpd_service() else 'DOWN'
        elif service_name == 'rabbitmq':
            return 'UP' if self.check_rabbitmq_service() else 'DOWN'
        elif service_name == 'postgresql':
            return 'UP' if self.check_postgresql_service() else 'DOWN'
        else:
            return 'DOWN'
    
    def get_rbcapp1_status(self):
        """Get overall rbcapp1 status based on all services"""
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
        
        # Create JSON files for each service
        json_files = []
        for service_name, status in service_statuses.items():
            payload = self.create_json_payload(service_name, status)
            filepath = self.write_json_file(payload)
            json_files.append(filepath)
            print(f"{service_name}: {status}")
        
        # Create JSON file for rbcapp1 overall status
        rbcapp1_payload = self.create_json_payload('rbcapp1', rbcapp1_status)
        rbcapp1_file = self.write_json_file(rbcapp1_payload)
        json_files.append(rbcapp1_file)
        
        print("-" * 50)
        print(f"rbcapp1 Overall Status: {rbcapp1_status}")
        print(f"JSON files created in: {self.json_dir}")
        
        return json_files, rbcapp1_status, service_statuses


def main():
    """Main function"""
    monitor = ServiceMonitor()
    
    # Run monitoring
    json_files, rbcapp1_status, service_statuses = monitor.monitor_services()
    
    # Display summary
    print("\n" + "="*50)
    print("MONITORING SUMMARY")
    print("="*50)
    print(f"rbcapp1 Status: {rbcapp1_status}")
    print("Service Details:")
    for service, status in service_statuses.items():
        print(f"  - {service}: {status}")
    print(f"\nJSON files created: {len(json_files)}")
    
    return json_files


if __name__ == "__main__":
    main()
