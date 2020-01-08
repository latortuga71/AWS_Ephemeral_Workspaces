import json
import boto3
import sys

def create_alarm(Id):
    client = boto3.client('cloudwatch')
    try:
        resp = client.put_metric_alarm( 
                                    AlarmName='WorkSpace_Disconnected_Id_{}'.format(Id),
                                    AlarmDescription='Created By Create_Alarm_Lambda_Func Triggered when new workspace is created.',
                                    ActionsEnabled=True,
                                    OKActions=[], ## empty for now
                                    AlarmActions=['arn:aws:sns:us-east-1:862402190812:Log0ff_Lambda'], ## arn for lambda function being called is here this sns arn calls the lambda function
                                    InsufficientDataActions=[], # empty for now
                                    MetricName='SessionDisconnect',
                                    Namespace='AWS/WorkSpaces',
                                    Statistic='Average',
                                    Dimensions=[{'Value':Id,'Name':'WorkspaceId'}],
                                    Period=60,
                                    EvaluationPeriods=1,
                                    DatapointsToAlarm=1,
                                    Threshold=1,
                                    ComparisonOperator='GreaterThanOrEqualToThreshold',
                                    TreatMissingData='missing'
                                    )
        print("Successfully created alarm..")
        print(resp)
    except:
        print("Error could not create alarm...")
        import traceback
        print("FAILED Printing STDERR BELOW..\n")
        traceback.print_exc()
        sys.exit(1)

def lambda_handler(event, context):
    try:
      Id = event['detail']['responseElements']['pendingRequests'][0]['workspaceId']
    except:
        print("ERROR Could not extract WorkSpace ID Exiting!")
        sys.exit(1)

    create_alarm(Id)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully Created Alarm for workspace: {}'.format(Id))
    }
