import boto3
import json

def setup_trigger():
    events_client = boto3.client('events')
    lambda_client = boto3.client('lambda')
    
    rule_name = 'mediaconvert-cleanup-trigger'
    
    try:
        # Criar regra EventBridge
        events_client.put_rule(
            Name=rule_name,
            EventPattern=json.dumps({
                "source": ["aws.mediaconvert"],
                "detail-type": ["MediaConvert Job State Change"],
                "detail": {
                    "status": ["COMPLETE"]
                }
            }),
            State='ENABLED'
        )
        print(f"Regra criada: {rule_name}")
        
        # Adicionar target
        events_client.put_targets(
            Rule=rule_name,
            Targets=[{
                'Id': '1',
                'Arn': 'arn:aws:lambda:us-east-1:969430605054:function:drive-online-video-cleanup'
            }]
        )
        print("Target adicionado")
        
        # Permissao
        try:
            lambda_client.add_permission(
                FunctionName='drive-online-video-cleanup',
                StatementId='mediaconvert-trigger',
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=f'arn:aws:events:us-east-1:969430605054:rule/{rule_name}'
            )
            print("Permissao adicionada")
        except:
            print("Permissao ja existe")
        
        print("SUCESSO: Trigger configurado!")
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    setup_trigger()