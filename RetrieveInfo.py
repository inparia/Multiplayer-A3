import json
import boto3

def retrieveInfo(event, context):
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('Player')
  response = table.scan()
  
  return {
    'statusCode' : 200,
    'body' : json.dumps(response)
  }