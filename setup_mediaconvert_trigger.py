import boto3
import json

def setup_mediaconvert_trigger():
    """Configurar trigger do MediaConvert para Lambda cleanup"""
    
    events_client = boto3.client('events')
    lambda_client = boto3.client('lambda')
    
    # 1. Criar regra EventBridge para MediaConvert
    rule_name = 'mediaconvert-cleanup-trigger'
    
    try:
        events_client.put_rule(
            Name=rule_name,
            EventPattern=json.dumps({
                "source": ["aws.mediaconvert"],
                "detail-type": ["MediaConvert Job State Change"],
                "detail": {
                    "status": ["COMPLETE", "ERROR"]
                }
            }),
            State='ENABLED',
            Description='Trigger cleanup after MediaConvert job completion'
        )
        print(f"✅ Regra criada: {rule_name}")
        
        # 2. Adicionar Lambda como target
        events_client.put_targets(
            Rule=rule_name,
            Targets=[{
                'Id': '1',
                'Arn': 'arn:aws:lambda:us-east-1:969430605054:function:drive-online-video-cleanup'
            }]
        )
        print("✅ Target Lambda adicionado")
        
        # 3. Dar permissão para EventBridge invocar Lambda
        try:
            lambda_client.add_permission(
                FunctionName='drive-online-video-cleanup',
                StatementId='mediaconvert-trigger',
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=f'arn:aws:events:us-east-1:969430605054:rule/{rule_name}'
            )
            print("✅ Permissão adicionada")
        except lambda_client.exceptions.ResourceConflictException:
            print("✅ Permissão já existe")
        
        print("\n🎉 Trigger configurado com sucesso!")
        print("Agora o cleanup será executado automaticamente após conversões")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    setup_mediaconvert_trigger()