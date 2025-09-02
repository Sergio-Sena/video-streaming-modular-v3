#!/usr/bin/env python3
"""
Deploy script for auth-service Lambda function
"""
import os
import zipfile
import boto3
import subprocess
import shutil
from pathlib import Path

def create_deployment_package():
    """Create deployment package for Lambda"""
    print("Creating deployment package...")
    
    # Create temp directory
    temp_dir = Path("temp_deploy")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([
        "pip", "install", "-r", "requirements-minimal.txt", 
        "-t", str(temp_dir)
    ], check=True)
    
    # Copy source code
    print("Copying source code...")
    src_dir = Path("src")
    for file in src_dir.rglob("*.py"):
        dest = temp_dir / file.relative_to(src_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest)
    
    # Create zip file
    print("Creating zip file...")
    zip_path = Path("auth-service.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(temp_dir)
                zipf.write(file, arcname)
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print(f"Deployment package created: {zip_path}")
    return zip_path

def deploy_lambda(zip_path: Path, function_name: str = "drive-online-auth-service"):
    """Deploy Lambda function"""
    print(f"Deploying Lambda function: {function_name}")
    
    lambda_client = boto3.client('lambda')
    
    try:
        # Update existing function
        with open(zip_path, 'rb') as f:
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=f.read()
            )
        print("Lambda function updated successfully!")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print("Function not found. Creating new function...")
        
        # Create new function
        with open(zip_path, 'rb') as f:
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.12',
                Role='arn:aws:iam::969430605054:role/drive-online-lambda-role',
                Handler='complete_main.handler',
                Code={'ZipFile': f.read()},
                Description='Drive Online Auth Service',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'DEVELOPMENT_MODE': 'false'
                    }
                }
            )
        print("Lambda function created successfully!")

def main():
    """Main deployment function"""
    print("Starting deployment process...")
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Create and deploy
    zip_path = create_deployment_package()
    deploy_lambda(zip_path)
    
    # Cleanup
    zip_path.unlink()
    print("Deployment completed!")

if __name__ == "__main__":
    main()