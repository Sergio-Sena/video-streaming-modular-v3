#!/usr/bin/env python3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_frontend_login():
    print("TESTANDO LOGIN NO FRONTEND")
    print("=" * 30)
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Acessar o site
        print("1. Acessando o site...")
        driver.get("https://videos.sstechnologies-cloud.com")
        time.sleep(3)
        
        print(f"   Titulo: {driver.title}")
        print(f"   URL atual: {driver.current_url}")
        
        # Procurar campos de login
        print("\n2. Procurando campos de login...")
        
        try:
            email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email']")
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Login'), button:contains('Entrar')")
            
            print("   Campos encontrados!")
            
            # Preencher e submeter
            print("\n3. Preenchendo credenciais...")
            email_field.clear()
            email_field.send_keys("senanetworker@gmail.com")
            
            password_field.clear()
            password_field.send_keys("sergiosena")
            
            print("   Clicando em login...")
            login_button.click()
            
            time.sleep(5)
            
            # Verificar se logou
            print("\n4. Verificando resultado...")
            print(f"   URL pos-login: {driver.current_url}")
            
            # Procurar indicadores de sucesso
            if "dashboard" in driver.current_url.lower() or "videos" in driver.page_source.lower():
                print("   SUCESSO! Login realizado")
                
                # Procurar aba de videos
                try:
                    videos_tab = driver.find_element(By.XPATH, "//*[contains(text(), 'Vídeos') or contains(text(), 'Videos')]")
                    print("   Aba Videos encontrada!")
                except:
                    print("   Aba Videos nao encontrada")
                    
            else:
                print("   FALHA! Login nao realizado")
                print(f"   Conteudo da pagina: {driver.page_source[:500]}...")
                
        except Exception as e:
            print(f"   ERRO ao encontrar campos: {e}")
            print(f"   HTML da pagina: {driver.page_source[:1000]}...")
            
    except Exception as e:
        print(f"ERRO geral: {e}")
        
    finally:
        try:
            driver.quit()
        except:
            pass

def test_simple_request():
    print("\nTESTE SIMPLES DE REQUISICAO")
    print("=" * 30)
    
    try:
        response = requests.get("https://videos.sstechnologies-cloud.com", timeout=10)
        print(f"Status: {response.status_code}")
        
        if "login" in response.text.lower():
            print("Pagina de login detectada")
        if "email" in response.text.lower():
            print("Campo email detectado")
        if "password" in response.text.lower():
            print("Campo password detectado")
            
        # Procurar por React
        if "react" in response.text.lower() or "_app" in response.text:
            print("Aplicacao React detectada")
            
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    test_simple_request()
    
    # Tentar teste com Selenium apenas se disponivel
    try:
        test_frontend_login()
    except ImportError:
        print("\nSelenium nao disponivel - instale com: pip install selenium")
    except Exception as e:
        print(f"\nErro no teste Selenium: {e}")