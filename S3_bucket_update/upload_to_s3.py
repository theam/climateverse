#!/usr/bin/env python3

import os
import re
import requests
import boto3
from botocore.exceptions import NoCredentialsError

# AWS credentials
aws_creds = {
    'aws_access_key_id': 'aws_access_key_id',
    'aws_secret_access_key': 'aws_secret_access_key',
    'region_name': 'us-east-1'
}

bucket_name = 'climateverse'
directory_path = 'output_images'
google_sheet_url = 'https://sheets.googleapis.com/v4/spreadsheets/1xtn_CGaKM1k69lAYzwXB2mi1TCR344dkE2Id_WzuO5M/values/C5:C96?key=AIzaSyCqMZtB78_St_oOr_ro2Kiz98gpoB9bBg0'

def get_google_sheet_data():
    try:
        response = requests.get(google_sheet_url)
        response.raise_for_status()
        data = response.json()
        return data['values']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return None

def upload_files_to_s3():
    s3_client = boto3.client('s3', **aws_creds)
    try:
        files = os.listdir(directory_path)
        data = get_google_sheet_data()
        if not data:
            return

        for file in files:
            match = re.match(r'^dataset_(\d+)', file)
            if match:
                index = int(match.group(1))
                metadata_value = data[index][0]  # Adjusting index to match spreadsheet row

                print(f"Uploading {file} to {bucket_name} with metadata: {metadata_value}")
                file_path = os.path.join(directory_path, file)

                try:
                    s3_client.upload_file(
                        file_path, bucket_name, file,
                        ExtraArgs={'Metadata': {'uniqueID': metadata_value}}
                    )
                    print(f"Successfully uploaded {file} to {bucket_name}")
                except NoCredentialsError:
                    print("Credentials not available")
    except Exception as e:
        print(f"Error uploading files to S3: {e}")

if __name__ == "__main__":
    upload_files_to_s3()