#!/usr/bin/env python3
import requests

def test_site():
    print("TESTE DO SITE")
    print("=" * 20)
    
    url = "https://videos.sstechnologies-cloud.com"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            print("\nConteudo detectado:")
            if "login" in content:
                print("- Pagina de login: SIM")
            if "email" in content:
                print("- Campo email: SIM") 
            if "password" in content:
                print("- Campo senha: SIM")
            if "react" in content or "vite" in content:
                print("- App React: SIM")
            if "drive" in content and "online" in content:
                print("- Drive Online: SIM")
                
            print(f"\nTamanho da pagina: {len(response.text)} chars")
            
            # Mostrar inicio do HTML
            print(f"\nInicio do HTML:")
            print(response.text[:500])
            
        else:
            print(f"ERRO: Status {response.status_code}")
            
    except Exception as e:
        print(f"ERRO: {e}")
    
    print(f"\nACESSE MANUALMENTE: {url}")
    print("Credenciais: senanetworker@gmail.com / sergiosena")

if __name__ == "__main__":
    test_site()