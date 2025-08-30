import json
import boto3
import uuid
from datetime import datetime, timedelta

def handler(event, context):
    """Handler para reset de senha via SNS"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Resposta para OPTIONS
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        body = json.loads(event['body'])
        email = body.get('email')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'success': False, 'message': 'Email obrigatório'})
            }
        
        # Gerar código de reset
        reset_code = str(uuid.uuid4())[:8].upper()
        
        # Enviar via SNS
        sns_client = boto3.client('sns')
        
        message = f"""
Solicitação de Reset de Senha - Video Streaming SStech

Email solicitante: {email}
Código de reset: {reset_code}
Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Para redefinir sua senha, use o código acima na aplicação.
Válido por 24 horas.

Se você não solicitou este reset, ignore este email.
        """
        
        response = sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:969430605054:video-streaming-password-reset',
            Message=message,
            Subject='Reset de Senha - Video Streaming SStech'
        )
        
        print(f"SNS Message ID: {response['MessageId']}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True, 
                'message': 'Email de reset enviado com sucesso',
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        print(f"Erro no reset: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': 'Erro interno'})
        }