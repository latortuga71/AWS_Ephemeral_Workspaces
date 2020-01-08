import json
import boto3
import sys

def del_alarm(Id):
    client = boto3.client('cloudwatch')
    try: 
      response = client.delete_alarms(
      AlarmNames=['WorkSpace_Disconnected_Id_{}'.format(Id)])
      print("Success")
    except:
      print("ERROR COULD NOT DELETE ALARM")
      sys.exit(1)



def lambda_handler(event, context):
    print(event)
    try:
      Id = event['detail']['requestParameters']['terminateWorkspaceRequests'][0]['workspaceId']
      print("Successfully Deleted Alarm!")
    except:
        print("ERROR Could not get workspace Id Exiting!")
        sys.exit(1)
    del_alarm(Id)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully Deleted alarm for workspace {}'.format(Id))
    }
