# AWS_Ephemeral_Workspaces
One of many solutions for creating ephemeral workspaces in AWS

## Read the PDF

All the information on the setup and workflow is in the pdf file, all 3 lambda function are used but create a self contained system for completely tearing down and rebuilding workpaces. Making them ephemeral! This is useful in situations where if a user is disconnected for more than 10 minutes or logs off the workspace is terminated deleting all data on disk.
