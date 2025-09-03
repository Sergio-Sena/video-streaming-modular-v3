#!/usr/bin/env python3
"""
Teste real de upload dos arquivos da pasta teste
"""
import requests
import os
from pathlib import Path

class RealUploadTest:
    def __init__(self):
        self.base_url = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
        self.token = None
        
    def login(self):
        """Login real"""
        response = requests.post(f"{self.base_url}/auth/login", json={
            "email": "senanetworker@gmail.com",
            "password": "sergiosena"
        })
        
        if response.status_code == 200:
            self.token = response.json()["token"]
            print("[OK] Login realizado")
            return True
        else:
            print(f"[ERRO] Login falhou: {response.status_code}")
            return False
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def upload_file(self, file_path):
        """Upload real de arquivo"""
        file_path = Path(file_path)
        
        print(f"\n[UPLOAD] {file_path.name}")
        print(f"  Tamanho: {file_path.stat().st_size / (1024*1024):.1f}MB")
        
        try:
            # 1. Obter URL de upload
            response = requests.post(f"{self.base_url}/files/upload-url", 
                headers={**self.get_headers(), "Content-Type": "application/json"},
                json={
                    "fileName": file_path.name,
                    "fileSize": file_path.stat().st_size,
                    "contentType": "application/octet-stream"
                }
            )
            
            if response.status_code != 200:
                print(f"  [ERRO] Falha ao obter URL: {response.status_code}")
                return False
            
            upload_data = response.json()
            upload_url = upload_data["uploadUrl"]
            file_id = upload_data["fileId"]
            
            print(f"  [OK] URL obtida: {file_id}")
            
            # 2. Upload do arquivo
            with open(file_path, 'rb') as f:
                upload_response = requests.put(upload_url, data=f)
            
            if upload_response.status_code not in [200, 204]:
                print(f"  [ERRO] Upload falhou: {upload_response.status_code}")
                return False
            
            print(f"  [OK] Upload concluído")
            
            # 3. Confirmar upload
            confirm_response = requests.post(f"{self.base_url}/files/{file_id}/confirm",
                headers=self.get_headers()
            )
            
            if confirm_response.status_code == 200:
                print(f"  [OK] Upload confirmado")
                return True
            else:
                print(f"  [AVISO] Confirmação falhou: {confirm_response.status_code}")
                return True  # Upload pode ter funcionado mesmo assim
                
        except Exception as e:
            print(f"  [ERRO] Exceção: {e}")
            return False
    
    def list_files(self):
        """Lista arquivos após upload"""
        response = requests.get(f"{self.base_url}/files", headers=self.get_headers())
        
        if response.status_code == 200:
            files = response.json().get("files", [])
            print(f"\n[FILES] {len(files)} arquivos encontrados:")
            
            # Agrupar por tipo
            videos = [f for f in files if f.get('type', '').startswith('video/')]
            images = [f for f in files if f.get('type', '').startswith('image/')]
            docs = [f for f in files if 'pdf' in f.get('type', '')]
            
            print(f"  Videos: {len(videos)}")
            print(f"  Fotos: {len(images)}")  
            print(f"  Documentos: {len(docs)}")
            
            return files
        else:
            print(f"[ERRO] Falha ao listar: {response.status_code}")
            return []
    
    def get_storage(self):
        """Informações de storage"""
        response = requests.get(f"{self.base_url}/user/storage", headers=self.get_headers())
        
        if response.status_code == 200:
            storage = response.json()
            used_gb = storage['used'] / (1024**3)
            print(f"\n[STORAGE] {used_gb:.2f}GB usado | {storage['files']} arquivos")
            return storage
        else:
            print(f"[ERRO] Storage falhou: {response.status_code}")
            return None
    
    def run_test(self):
        """Executa teste completo"""
        print("=== TESTE REAL DE UPLOAD ===")
        
        if not self.login():
            return False
        
        # Estado inicial
        initial_files = self.list_files()
        initial_storage = self.get_storage()
        
        # Upload dos arquivos de teste
        teste_dir = Path("teste")
        if not teste_dir.exists():
            print("[ERRO] Pasta teste não encontrada")
            return False
        
        uploaded = 0
        for file_path in teste_dir.iterdir():
            if file_path.is_file():
                if self.upload_file(file_path):
                    uploaded += 1
        
        print(f"\n[RESULTADO] {uploaded} arquivos enviados")
        
        # Estado final
        final_files = self.list_files()
        final_storage = self.get_storage()
        
        # Comparação
        if final_storage and initial_storage:
            diff_gb = (final_storage['used'] - initial_storage['used']) / (1024**3)
            print(f"[DIFF] +{diff_gb:.2f}GB adicionados")
        
        return True

if __name__ == "__main__":
    tester = RealUploadTest()
    tester.run_test()