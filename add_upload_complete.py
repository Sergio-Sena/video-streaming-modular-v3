import re

# Ler arquivo
with open('backend/auth-service/src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar endpoint antes da rota de upload-url
upload_complete_code = '''
@app.post("/files/upload-complete")
async def upload_complete_endpoint(request: dict, current_user: dict = Depends(verify_token)):
    """Notify upload completion"""
    try:
        file_id = request.get('fileId')
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID required")
        
        if is_video_file(file_id):
            try:
                public_key = copy_to_public_bucket(file_id, user_id)
                return {'message': 'Upload complete', 'isVideo': True, 'publicKey': public_key}
            except Exception as e:
                return {'message': 'Upload complete', 'isVideo': True, 'error': str(e)}
        
        return {'message': 'Upload complete', 'isVideo': False}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''

# Inserir antes de @app.post("/files/upload-url")
pattern = r'(@app\.post\("/files/upload-url"\))'
replacement = upload_complete_code + r'\1'
new_content = re.sub(pattern, replacement, content)

# Salvar
with open('backend/auth-service/src/main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Endpoint upload-complete adicionado")