import boto3
import zipfile
import os
import shutil

def update_cleanup_lambda():
    """Atualizar Lambda de cleanup"""
    
    # Criar diretório temporário
    temp_dir = "temp_cleanup"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Copiar arquivos
        shutil.copy("src/cleanup.py", f"{temp_dir}/lambda_function.py")
        
        # Criar ZIP
        zip_filename = "cleanup-update.zip"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(f"{temp_dir}/lambda_function.py", "lambda_function.py")
        
        # Atualizar Lambda
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_filename, 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName='drive-online-video-cleanup',
                ZipFile=zip_file.read()
            )
        
        print("Lambda cleanup atualizada com sucesso!")
        
    finally:
        # Limpeza
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)

if __name__ == "__main__":
    update_cleanup_lambda()