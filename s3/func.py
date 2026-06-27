import json
import boto3

# initialize client with aws botot3 to access/interact with aws service
s3_client = boto3_client('s3')
# define what response should boto3 return to cleint
response = s3_client.list['Buckets']
for bucket in response ['Buckets']:
    print(bucket['Name'])