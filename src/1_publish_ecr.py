import boto3
import os
import subprocess
from pathlib import Path
from datetime import datetime
from botocore.exceptions import ClientError

PROJECT_ROOT = Path(__file__).parent.parent

AWS_REGION = "eu-north-1" 
ECR_REPO_NAME = "awscvgenerator"
AWS_ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
ECR_URI = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO_NAME}"

def run_command(command, cwd=None, capture_output=False):
    """Run a command and raise an exception if it fails"""
    return subprocess.run(
        command, 
        shell=True, 
        cwd=cwd, 
        check=True,
        text=True,
        capture_output=capture_output
    )

def ensure_ecr_repository_exists():
    """Create ECR repository if it doesn't exist"""
    ecr_client = boto3.client('ecr', region_name=AWS_REGION)
    try:
        ecr_client.describe_repositories(repositoryNames=[ECR_REPO_NAME])
        print(f"ECR repository {ECR_REPO_NAME} already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            print(f"Creating ECR repository {ECR_REPO_NAME}...")
            ecr_client.create_repository(
                repositoryName=ECR_REPO_NAME,
                imageScanningConfiguration={'scanOnPush': True},
                encryptionConfiguration={'encryptionType': 'AES256'}
            )
            print(f"Created ECR repository {ECR_REPO_NAME}")
        else:
            raise

def get_version_tag():
    """Get version from git tag or generate timestamp-based version"""
    try:
        # Try to get the latest git tag
        result = run_command("git describe --tags --abbrev=0", capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If no git tag exists, use timestamp
        return f"v{datetime.now().strftime('%Y%m%d-%H%M%S')}"

try:
    VERSION = get_version_tag()
    
    # Step 1: Ensure ECR Repository exists
    print("Checking ECR repository...")
    ensure_ecr_repository_exists()

    # Step 2: Authenticate with ECR
    print("Authenticating with ECR...")
    auth_command = f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {ECR_URI}"
    run_command(auth_command)

    # Step 3: Build Docker Image
    print(f"Building Docker image version {VERSION}...")
    run_command(f"docker build -t {ECR_REPO_NAME}:{VERSION} -f src/app/Dockerfile .", cwd=PROJECT_ROOT)

    # Step 4: Tag the Images (both version-specific and latest)
    print("Tagging Docker images...")
    run_command(f"docker tag {ECR_REPO_NAME}:{VERSION} {ECR_URI}:{VERSION}")
    run_command(f"docker tag {ECR_REPO_NAME}:{VERSION} {ECR_URI}:latest")

    # Step 5: Push to ECR
    print("Pushing Docker images to ECR...")
    run_command(f"docker push {ECR_URI}:{VERSION}")
    run_command(f"docker push {ECR_URI}:latest")

    # Step 6: Clean up old images (optional)
    print("Cleaning up local Docker images...")
    try:
        run_command(f"docker rmi {ECR_REPO_NAME}:{VERSION}")
        run_command(f"docker rmi {ECR_URI}:{VERSION}")
        run_command(f"docker rmi {ECR_URI}:latest")
    except subprocess.CalledProcessError:
        print("Warning: Could not remove some Docker images")

    print(f"✅ Docker images pushed successfully!")
    print(f"   Version: {VERSION}")
    print(f"   Repository: {ECR_URI}")

except subprocess.CalledProcessError as e:
    print(f"❌ Error: Command failed with exit status {e.returncode}")
    print(f"Command: {e.cmd}")
    if e.stdout:
        print(f"Output: {e.stdout}")
    if e.stderr:
        print(f"Error: {e.stderr}")
    exit(1)
