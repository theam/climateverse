#!/usr/bin/env python3

import base64
import boto3
import os
import requests

bucket_name = 'climateverse'
directory_path = 'output_images'

github_token = '{GITHUB_TOKEN}'

def list_images_github():
    url = f"https://api.github.com/repos/crisisready/climateverse-scorecards/contents/{directory_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        print(f"Successfully listed images from scorecards repository", flush=True)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images from scorecards repository: {e}", flush=True)
        return None

def retrieve_images_github():
    images_list = list_images_github()

    for item in images_list:
        image_name = item["name"]

        output_dir = f'/app/{directory_path}'
        output_file = f'{output_dir}/{image_name}'

        url = f"https://api.github.com/repos/crisisready/climateverse-scorecards/contents/{directory_path}/{image_name}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_file)

            # Decode the base64 content
            file_content = base64.b64decode(data["content"])

            with open(output_file, 'wb') as file:
                file.write(file_content)

            print(f"Successfully fetched {image_name} from Github", flush=True)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {image_name} from Github: {e}", flush=True)
            return None

    print("All images fetched from Github")

def upload_files_to_s3():

    print("Retrieving images from scorecards repository", flush=True)
    retrieve_images_github()

    # AWS credentials
    aws_creds = {
        'aws_access_key_id': '{AWS_ACCESS_KEY_ID}',
        'aws_secret_access_key': '{AWS_SECRET_ACCESS_KEY}',
        'region_name': 'us-east-1'
    }

    s3_client = boto3.client('s3', **aws_creds)
    try:
        # Remove all files from the bucket before uploading new files
        try:
            objects = s3_client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in objects:
                delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects['Contents']]}
                s3_client.delete_objects(Bucket=bucket_name, Delete=delete_keys)
                print(f"Successfully deleted all files from {bucket_name}", flush=True)
            else:
                print(f"No files to delete in {bucket_name}", flush=True)
        except Exception as e:
            print(f"Error deleting files from S3: {e}", flush=True)

        # Upload files retrieved from Github to S3
        files = os.listdir(directory_path)
        for file in files:
            print(f"Uploading {file} to {bucket_name}", flush=True)
            file_path = os.path.join(directory_path, file)

            try:
                s3_client.upload_file(file_path, bucket_name, file)
                print(f"Successfully uploaded {file} to {bucket_name}", flush=True)
            except Exception as e:
                print(f"Error uploading {file} to S3: {e}", flush=True)

    except Exception as e:
        print(f"Error uploading files to S3: {e}", flush=True)

if __name__ == "__main__":
    upload_files_to_s3()