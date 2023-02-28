import requests
import json

# Set the ECS Management API endpoint and credentials
ecs_endpoint = "https://ecs.example.com:4443"
ecs_username = "username"
ecs_password = "password"

# Ask the user for the namespace name, storage quota requirement, bucket name, and versioning preference
namespace_name = input("Enter the namespace name: ")
storage_quota = input("Enter the storage quota requirement (in bytes): ")
bucket_name = input("Enter the bucket name: ")
versioning_enabled = input("Enable versioning for the bucket? (y/n): ")

# Set the namespace and bucket creation API endpoints
namespace_endpoint = f"{ecs_endpoint}/object/namespaces"
bucket_endpoint = f"{ecs_endpoint}/object/buckets"

# Set the headers and data for creating the namespace
namespace_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
namespace_data = {
    "name": namespace_name,
    "default_data_services_vpool": "default",
    "default_policy_group": "default",
    "default_retention": {
        "mode": "compliance",
        "compliance": {
            "lock_enabled": False
        }
    },
    "tags": {}
}

# Send a POST request to create the namespace with the credentials, headers, and data
namespace_response = requests.post(namespace_endpoint, auth=(ecs_username, ecs_password), headers=namespace_headers, data=json.dumps(namespace_data))

# Check if the request was successful
if namespace_response.status_code == 201:
    # Get the namespace ID from the response JSON
    namespace_id = namespace_response.json()["id"]

    # Set the headers and data for creating the bucket
    bucket_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    bucket_data = {
        "namespace": namespace_id,
        "name": bucket_name,
        "versioning_enabled": versioning_enabled.lower() == "y",
        "default_retention": {
            "mode": "compliance",
            "compliance": {
                "lock_enabled": False
            }
        },
        "lifecycle_rules": [
            {
                "type": "object-age",
                "enabled": True,
                "priority": 1,
                "action": {
                    "type": "delete"
                },
                "filter": {
                    "prefix": ""
                },
                "conditions": {
                    "age": {
                        "value": 365,
                        "unit": "days"
                    }
                }
            }
        ],
        "tags": {},
        "default_data_services_vpool": "default",
        "storage_quota": storage_quota
    }

    # Send a POST request to create the bucket with the credentials, headers, and data
    bucket_response = requests.post(bucket_endpoint, auth=(ecs_username, ecs_password), headers=bucket_headers, data=json.dumps(bucket_data))

    # Check if the request was successful
    if bucket_response.status_code == 201:
        # Get the bucket ID and quota size from the response JSON
        bucket_id = bucket_response.json()["id"]
        quota_size = bucket_response.json()["storage_quota"]

        # Print the name of the new bucket and its quota size
        print(f"Created bucket '{bucket_name}' with quota size {quota_size} bytes.")
    else:
        # Print an error message if the bucket creation request was not successful
        print(f"Failed to create bucket '{bucket_name}
