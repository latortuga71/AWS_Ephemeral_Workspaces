import json
import boto3
import time
import logging
import sys
import datetime

def get_userName(workspace_Id):
    client = boto3.client('workspaces')
    try:
      resp = client.describe_workspaces(WorkspaceIds=[workspace_Id],Limit=1) #// call this func in boto3
      username = resp['Workspaces'][0]["UserName"]
      bundle_id = resp['Workspaces'][0]["BundleId"]
      directory_id = resp['Workspaces'][0]["DirectoryId"]
    ### if more information is needed pull from json response and add to list as function returns list 
      get_userName_result = [username,bundle_id,directory_id]
      return get_userName_result
    except:
        import traceback
        print("FAILED Printing STDERR BELOW..\n")
        traceback.print_exc()
        print("\n")
        print("Error Retrieving Username and BundleId, Check WorkspaceID provided.")
        return None
    
def check_if_reConnect(workspace_Id):
    client = boto3.client('cloudwatch')
    fifteen_mins = datetime.datetime.now() - datetime.timedelta(minutes=15)
    fifteen_mins_ago = fifteen_mins.isoformat()
    now = datetime.datetime.now().isoformat()
    try:
      resp = client.get_metric_statistics(
        Namespace='AWS/WorkSpaces',
        MetricName='ConnectionSuccess',
        Dimensions=[{'Value': '{}'.format(workspace_Id),'Name': 'WorkspaceId'}],
        StartTime=fifteen_mins_ago,
        EndTime=now,
        Period=60,
        Statistics=['Average']
                                          )
      print("Data Recieved from ConnectionSuccess Metric Query Below")
      print(resp)
      metric_data = resp['Datapoints']
      print("Number of successful connections logged in past 15 minutes below")
      total_successful_connections = 0
      for x in resp['Datapoints']:
          print(x['Average'])
          total_successful_connections += int(x['Average'])
      print("Total Successful Connections {}".format(total_successful_connections))
      if total_successful_connections >= 1:
          print("User Reconnected Successfully {} times before 15 minutes...Stopping WorkSpaceTermination!".format(total_successful_connections))
          return True
      else:
        print("User did not reconnect")
        return False
    except:
        print("Failed to request metric data")
        print("ERROR COLLECTION METRIC DATA, CANNOT DETERMINE IF USER ATTEMPTED TO RECONNECT QUITTING WORKSPACE TERMINATION ")
        return False
    
def term(workspace_Id):
    try:
      client = boto3.client('workspaces')
      resp = client.terminate_workspaces(TerminateWorkspaceRequests = [{'WorkspaceId':workspace_Id}])
      return True
    except:
        import traceback
        print("FAILED Printing STDERR BELOW..\n")
        traceback.print_exc()
        print("\n")
        print("Failed to Terminate Workspace check workspace ID provided".format(workspace_Id))
        return False
    
def create(username,bundle_id,directory_id):
    client = boto3.client('workspaces')
    try:
      resp = client.create_workspaces(Workspaces=[{"DirectoryId":directory_id,'UserName':username,'BundleId':bundle_id,
      'WorkspaceProperties':{'RunningMode':"AUTO_STOP",'RootVolumeSizeGib':80,'UserVolumeSizeGib':10,'ComputeTypeName':'VALUE'}}])       ## SPECIFY CREATED BUNDLE AND ASSIGN SAME USER THAT WAS ON TERMED MACHINE
      if resp['FailedRequests']:
        print("Failed to create new workspace...")
        print(resp)
        return False
      print(resp)
      print("Successfully Initated creation of new workspace with bundleId {} user {} directory {}\n".format(bundle_id,username,directory_id))
      print(resp)
      print("\n")
      return True
    except:
      import traceback
      print("FAILED Printing STDERR BELOW..\n")
      traceback.print_exc()
      print("\n")
      print("Failed to create new workspace...")
      return False




def lambda_handler(event, context):
    Message_data = event['Records'][0]['Sns']['Message']
    Message_json = json.loads(Message_data)
    Id = Message_json.get('Trigger', {}).get('Dimensions', [{}])[0].get('value') ## workspace ID
    User_bundle_info = get_userName(Id)
    if User_bundle_info:   # list of user unformation bundleId and username for use to recreate workspace.
      username = User_bundle_info[0]
      bundle = User_bundle_info[1]
      directory = User_bundle_info[2]
      print("Successfully got username and bundleId...Username: {}...BundleId: {} DirectoryId: {}".format(username,bundle,directory))
      print("Sleeping for 10 minutes to see if user has Successfully reconnected since Disconnect occured")
      for x in range(0,600):
        time.sleep(1)
        print("Sleeping for {} seconds...".format(x))
      print("Attemping metric connection successful check")
      recon_check = check_if_reConnect(Id)
      if recon_check == False:
        term_result = term(Id)
        if term_result == True:
          print ("Successfully Terminated WorkspaceID {}".format(Id))
          print("Sleeping for 4 minutes the attempting to RECREATE workspace")
          for x in range(0,240):
            time.sleep(1)
            print("Sleeping for {} seconds...".format(x))
          print("Attemping to re create workspace from bundle..")
          create_result = create(username,bundle,directory)
          if create_result == True:
            print("Done...")
          else:
            print("Failed to Create Workspace Sending Notification Of error")
            sys.exit(1)

        else:
          print("Failed to Terminate WorkspaceID {} Sending notification via text .. and exiting function".format(Id))
          sys.exit(1)
      else:
        print("User Reconnected, Aborting WorkSpace Termination")
        sys.exit()
    else:
      print("Failed to get username and bundleId...Sending notification via text.. and exiting function.")
      sys.exit(1)
    
    
    
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
