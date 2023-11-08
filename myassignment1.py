import requests
import yaml
import time
import signal

# Global variables to store health check results
results = {}
total_requests = {}

# Function to handle Ctrl+C signal and print final results
def signal_handler(sig, frame):
    print_results()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Function to send HTTP requests and update results
def check_health(endpoints):
    global results
    global total_requests

    for endpoint in endpoints:
        name = endpoint["name"]
        url = endpoint["url"]
        method = endpoint.get("method", "GET")
        headers = endpoint.get("headers", {})
        body = endpoint.get("body", None)

        try:
            response = requests.request(method, url, headers=headers, json=body, timeout=5)
            latency = response.elapsed.total_seconds() * 1000  # in milliseconds
            if 200 <= response.status_code < 300 and latency < 500:
                results[name] = results.get(name, 0) + 1
            total_requests[name] = total_requests.get(name, 0) + 1
        except Exception as e:
            total_requests[name] = total_requests.get(name, 0) + 1

# Function to print availability percentage
def print_results():
    for domain, count in total_requests.items():
        availability = results.get(domain, 0) / count * 100 if count > 0 else 0
        print(f"{domain} has {round(availability)}% availability percentage")

# Main function
def main():
    # Read endpoints from YAML file
    with open("config.yaml", "r") as file:
        endpoints = yaml.safe_load(file)

    try:
        # Continuously check health every 15 seconds
        while True:
            check_health(endpoints)
            print_results()
            time.sleep(15)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
