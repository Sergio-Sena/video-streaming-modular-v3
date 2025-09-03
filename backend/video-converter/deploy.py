import boto3
import zipfile
import os
import json

def create_deployment_package():
    """Criar pacote de deployment"""
    
    # Criar zip
    with zipfile.ZipFile('converter-deployment.zip', 'w') as zip_file:
        # Adicionar arquivos Python
        zip_file.write('src/converter.py', 'converter.py')
        zip_file.write('src/cleanup.py', 'cleanup.py')
    
    print("Pacote criado: converter-deployment.zip")

def deploy_lambda():
    """Deploy do Lambda"""
    
    lambda_client = boto3.client('lambda')
    
    # Ler zip
    with open('converter-deployment.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    function_name = 'drive-online-video-converter'
    
    try:
        # Tentar atualizar
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print(f"Lambda {function_name} atualizado!")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        # Criar novo
        print(f"Criando Lambda {function_name}...")
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role='arn:aws:iam::969430605054:role/lambda-execution-role',
            Handler='converter.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Video converter for Drive Online',
            Timeout=900,  # 15 minutes
            MemorySize=1024,
            Environment={
                'Variables': {
                    'MEDIACONVERT_ROLE': 'arn:aws:iam::969430605054:role/MediaConvertServiceRole',
                    'MEDIACONVERT_QUEUE': 'Default'
                }
            }
        )
        print(f"Lambda {function_name} criado!")
    
    return response

def configure_s3_trigger():
    """Configurar trigger S3"""
    
    s3_client = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    
    bucket_name = 'drive-online-storage'
    function_name = 'drive-online-video-converter'
    
    # Dar permissão ao S3 para invocar Lambda
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='s3-trigger-permission',
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=f'arn:aws:s3:::{bucket_name}'
        )
        print("Permissão S3 adicionada")
    except lambda_client.exceptions.ResourceConflictException:
        print("Permissão S3 já existe")
    
    # Configurar notificação S3
    notification_config = {
        'LambdaConfigurations': [
            {
                'Id': 'video-converter-trigger',
                'LambdaFunctionArn': f'arn:aws:lambda:us-east-1:969430605054:function:{function_name}',
                'Events': ['s3:ObjectCreated:*'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name': 'prefix',
                                'Value': 'users/'
                            }
                        ]
                    }
                }
            }
        ]
    }
    
    try:
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_config
        )
        print("Trigger S3 configurado!")
    except Exception as e:
        print(f"Erro ao configurar trigger: {e}")

if __name__ == "__main__":
    print("Iniciando deploy do video converter...")
    
    create_deployment_package()
    deploy_lambda()
    configure_s3_trigger()
    
    print("Deploy concluído!")