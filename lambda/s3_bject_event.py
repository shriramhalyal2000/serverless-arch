import json
import boto3
import os

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# Best practice: Use environment variables for resources
DESTINATION_SNS_ARN = os.environ.get('DESTINATION_SNS_ARN')

def lambda_handler(event, context):
    try:
        # 1. Parse the SNS records
        for record in event['Records']:
            sns_message_raw = record['Sns']['Message']
            sns_message = json.loads(sns_message_raw)
            
            # 2. Extract S3 details from the EventBridge payload structure
            # EventBridge S3 notifications structure: sns_message['detail']['bucket']['name']
            bucket_name = sns_message['detail']['bucket']['name']
            object_key = sns_message['detail']['object']['key']
            
            print(f"Processing object {object_key} from bucket {bucket_name}")
            
            # 3. Retrieve metadata using HeadObject
            response = s3_client.head_object(
                Bucket=bucket_name,
                Key=object_key
            )
            
            # S3 user-defined metadata is stored in the 'Metadata' key
            metadata = response.get('Metadata', {})
            
            # 4. Construct the payload for the next subscriber
            notification_payload = {
                "bucket": bucket_name,
                "key": object_key,
                "metadata": metadata,
                "content_type": response.get('ContentType'),
                "content_length": response.get('ContentLength')
            }
            
            # 5. Publish to the second SNS topic
            sns_response = sns_client.publish(
                TopicArn=DESTINATION_SNS_ARN,
                Subject="S3 Object Metadata Extracted",
                Message=json.dumps(notification_payload)
            )
            
            print(f"Successfully published metadata to SNS. MessageId: {sns_response['MessageId']}")
            
    except Exception as e:
        print(f"Error processing pipeline: {str(e)}")
        raise e