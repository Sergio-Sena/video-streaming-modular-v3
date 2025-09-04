import boto3
from datetime import datetime, timedelta

def check_lambda_logs():
    """Verificar logs da Lambda"""
    
    # Cliente CloudWatch Logs
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    # Nome do log group da Lambda
    log_group_name = '/aws/lambda/drive-online-auth-service'
    
    # Buscar logs das últimas 10 minutos
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=10)
    
    try:
        # Buscar eventos de log
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000),
            filterPattern='[DELETE]'  # Filtrar apenas logs de DELETE
        )
        
        print(f"=== LOGS DA LAMBDA (últimos 10 minutos) ===")
        print(f"Encontrados {len(response['events'])} eventos de DELETE")
        
        for event in response['events']:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            print(f"[{timestamp}] {message}")
            
    except Exception as e:
        print(f"Erro ao buscar logs: {e}")
        
        # Tentar listar log groups disponíveis
        try:
            log_groups = logs_client.describe_log_groups()
            print("\\nLog groups disponíveis:")
            for group in log_groups['logGroups']:
                if 'drive-online' in group['logGroupName']:
                    print(f"  - {group['logGroupName']}")
        except Exception as e2:
            print(f"Erro ao listar log groups: {e2}")

if __name__ == "__main__":
    check_lambda_logs()