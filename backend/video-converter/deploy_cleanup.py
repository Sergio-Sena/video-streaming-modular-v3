import boto3
import zipfile
import json

def create_cleanup_function():
    """Criar função de cleanup"""
    
    lambda_client = boto3.client('lambda')
    
    # Criar zip com o código de cleanup
    with zipfile.ZipFile('cleanup-deployment.zip', 'w') as zip_file:
        zip_file.write('src/cleanup.py', 'cleanup.py')
    
    # Ler zip
    with open('cleanup-deployment.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    function_name = 'drive-online-video-cleanup'
    
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role='arn:aws:iam::969430605054:role/video-streaming-lambda-role',
            Handler='cleanup.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Video cleanup after MediaConvert completion',
            Timeout=300,
            MemorySize=512
        )
        print(f"Função {function_name} criada!")
        
        # Dar permissão ao EventBridge
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='eventbridge-permission',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com'
        )
        print("Permissão EventBridge adicionada")
        
        return response
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    create_cleanup_function()