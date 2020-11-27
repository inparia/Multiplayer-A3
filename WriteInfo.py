import json
import boto3


def writeInfo(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Player')
    PlayerID = event['PlayerID']['S']
    AWR = event['AWR']['S']
    Win = event['Win']['S']
    Lose = event['Lose']['S']
    table.put_item(Item={'PlayerID': PlayerID, 'AWR' : AWR, 'Win' : Win, 'Lose' : Lose})
    
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }