import boto3
from datetime import datetime, timedelta

def check_all_logs():
    """Verificar todos os logs da Lambda"""
    
    # Cliente CloudWatch Logs
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    # Nome do log group da Lambda
    log_group_name = '/aws/lambda/drive-online-auth-service'
    
    # Buscar logs das últimas 30 minutos
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    try:
        # Buscar eventos de log
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000)
        )
        
        print(f"=== TODOS OS LOGS DA LAMBDA (últimos 30 minutos) ===")
        print(f"Encontrados {len(response['events'])} eventos")
        
        # Mostrar apenas os últimos 20 eventos
        recent_events = response['events'][-20:] if len(response['events']) > 20 else response['events']
        
        for event in recent_events:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            print(f"[{timestamp}] {message}")
            
    except Exception as e:
        print(f"Erro ao buscar logs: {e}")

if __name__ == "__main__":
    check_all_logs()