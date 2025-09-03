import boto3
import zipfile

def update_converter():
    """Atualizar função mediaconvert-trigger com código correto"""
    
    lambda_client = boto3.client('lambda')
    
    # Criar zip com o código correto
    with zipfile.ZipFile('mediaconvert-trigger-update.zip', 'w') as zip_file:
        zip_file.write('backend/video-converter/src/converter.py', 'mediaconvert_trigger.py')
    
    # Ler zip
    with open('mediaconvert-trigger-update.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    # Atualizar função
    response = lambda_client.update_function_code(
        FunctionName='mediaconvert-trigger',
        ZipFile=zip_content
    )
    
    print("Função mediaconvert-trigger atualizada!")
    return response

if __name__ == "__main__":
    update_converter()