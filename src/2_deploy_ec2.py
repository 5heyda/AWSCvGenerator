import boto3
import time
import os
from pathlib import Path
from dotenv import load_dotenv
import json
from botocore.exceptions import ClientError

# Load environment variables from .env file
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / '.env')

# Get environment variables with defaults
AWS_REGION = os.getenv('AWS_REGION', 'eu-north-1')
ECR_REPO_NAME = os.getenv('ECR_REPO_NAME', 'awscvgenerator')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
APP_PORT = os.getenv('APP_PORT', '80')

def get_terraform_outputs():
    """Read Terraform outputs from terraform.tfstate"""
    try:
        with open(PROJECT_ROOT / 'terraform' / 'terraform.tfstate') as f:
            state = json.load(f)
            outputs = state.get('outputs', {})
            return {
                'instance_id': outputs.get('instance_id', {}).get('value'),
                'public_ip': outputs.get('public_ip', {}).get('value')
            }
    except FileNotFoundError:
        raise Exception("Terraform state file not found. Have you run terraform apply?")

def get_instance_id_from_terraform():
    """Get EC2 instance ID from Terraform state"""
    try:
        with open('terraform/terraform.tfstate') as f:
            state = json.load(f)
            outputs = state.get('outputs', {})
            return outputs.get('ec2_instance_id', {}).get('value')
    except Exception as e:
        print(f"❌ Error reading Terraform state: {str(e)}")
        return None

def deploy_to_ec2(instance_id=None):
    """Deploy application to EC2 instance"""
    if not instance_id:
        print("❌ Error: No instance ID provided")
        return False
        
    try:
        ec2_client = boto3.client('ec2', region_name=AWS_REGION)
        
        # Check if instance exists and is running
        response = ec2_client.describe_instances(
            InstanceIds=[instance_id]
        )
        
        if not response['Reservations']:
            print(f"❌ Error: Instance {instance_id} not found")
            return False
            
        instance = response['Reservations'][0]['Instances'][0]
        state = instance['State']['Name']
        
        if state != 'running':
            print(f"❌ Error: Instance {instance_id} is not running (current state: {state})")
            return False
            
        print(f"✅ Instance {instance_id} is running")
        return True
        
    except ClientError as e:
        print(f"❌ Error during deployment: {str(e)}")
        return False

def main():
    # Try to get instance ID from different sources
    instance_id = (
        os.getenv('EC2_INSTANCE_ID') or 
        get_instance_id_from_terraform()
    )
    
    if not instance_id:
        print("❌ Error: No EC2 instance ID found in environment or Terraform state")
        exit(1)
    
    print(f"Deploying to EC2 instance {instance_id}...")
    
    if deploy_to_ec2(instance_id):
        print("✅ Deployment successful!")
    else:
        print("❌ Deployment failed!")
        exit(1)

if __name__ == "__main__":
    main()
