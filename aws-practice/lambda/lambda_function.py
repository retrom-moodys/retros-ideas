import json

import boto3

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('retro-practice')


def lambda_handler(event, _context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        s3_object = s3_client.get_object(Bucket=bucket, Key=key)
        data = json.loads(s3_object['Body'].read().decode('utf-8'))
        users = data if isinstance(data, list) else [data]
        for user in users:
            if table.get_item(Key={'useremail': user['useremail'], 'userage': int(user['userage'])}).get('Item'):
                continue

            table.put_item(Item={
                'useremail': user['useremail'],
                'userage': int(user['userage']),
                'userentry': int(user['userentry']),
                'username': user['username'],
            })

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing complete'})
    }
