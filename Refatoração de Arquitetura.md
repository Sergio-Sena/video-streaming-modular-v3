🎬 DOCUMENTAÇÃO TÉCNICA COMPLETA - REFAZER
Video Streaming SStech - Arquitetura Modular
📋 ÍNDICE
Visão Geral

Arquitetura

Microserviços

Fluxo de Dados

Infraestrutura AWS

Deploy

Monitoramento

Segurança

Suporte e Contato

🎯 VISÃO GERAL
Objetivo
Plataforma de streaming de vídeos com upload, conversão automática e reprodução otimizada, com foco em segurança de uso pessoal, incluindo MFA.

Características Principais
✅ Autenticação Segura (Email/Senha + MFA)

✅ Upload Direto (arquivos até 5TB via URL pré-assinada)

✅ Conversão Automática (qualquer formato → MP4)

✅ CDN Global (CloudFront)

✅ Arquitetura Serverless e Event-Driven (100% AWS)

Tecnologias
Backend: Python 3.11 (AWS Lambda)

Frontend: JavaScript Vanilla (S3 + CloudFront)

Banco de Dados: Amazon Cognito (para gerenciamento de usuários)

Storage: S3 + CloudFront

Conversão: AWS MediaConvert

Mensageria: Amazon SNS e SQS (para fluxo assíncrono)

Monitoramento: CloudWatch e Amazon EventBridge

🏗️ ARQUITETURA
Diagrama de Arquitetura
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ FRONTEND │ │ API GATEWAY │ │ AWS SNS │
│ │ │ │ │ (Topic) │
│ ┌───────────┐ │ │ ┌──────────────┐ │ │ ┌─────────────┐ │
│ │ HTML/JS │◄──┼──────►│ │ /auth │◄┼─────►│ │ VIDEO_UPLOAD│ │
│ │ CSS │ │ │ │ /videos │ │ │ └─────────────┘ │
│ └───────────┘ │ │ └──────────────┘ │ │ │ │
│ │ │ │ │ │ │ │
└─────────────────┘ └─────────┼────────┘ └───────┼─────────┘
│ ▲ ▼ ▲ ▼
│ │ ┌──────────────────┐ │ ┌─────────────┐
▼ │ │ COGNITO USER │ │ │ CONVERSION │
┌─────────────┐ │ │ POOL │ │ │ SERVICE │
│ S3 BUCKET │ │ └──────────┬───────┘ │ │ (Lambda) │
│ (Static Host)│ │ │ │ │ └─────────────┘
└─────────────┘ │ │ │ │ │
▼ │ ▼ │ ▼
┌─────────────┴──┐ ┌──────────────────┐ ┌─────────────┐
│ S3 BUCKETS │ │ MEDIACONVERT │ │ SQS Queue │
│ ┌───────────┐ │ │ │ │ │
│ │ Principal │ │ │ ┌───────────┐ │ │ ┌─────────┐ │
│ │ Temp │◄─┼─►│ │ Conversão │◄───┼─►│ │ Events │ │
│ └───────────┘ │ │ └───────────┘ │ │ └─────────┘ │
└────────────────┘ └──────────────────┘ └─────────────┘
▲
│
┌────────┴────────┐
│ EVENTBRIDGE │
└─────────────────┘
Fluxo de Dados

1. Usuario → CloudFront → S3 (Frontend)
2. Login → Cognito User Pool (Autenticação + MFA) → Tokens JWT
3. Upload → API Gateway (solicita URL pré-assinada) → Frontend faz upload direto para S3
4. Conversão → S3 Event → SNS Topic → SQS Queue → Lambda Trigger → MediaConvert
5. Streaming → CloudFront → Usuario
   🔧 MICROSERVIÇOS
6. AUTH SERVICE
   Responsabilidade
   Todo o fluxo de autenticação e gerenciamento de usuários é agora responsabilidade do Amazon Cognito User Pool. Ele lida com o registro, login com e-mail e senha, e o desafio de MFA. O serviço não é mais uma função Lambda customizada.

Endpoints: O API Gateway está integrado com o Cognito para autenticação.

Segurança: O Cognito gerencia de forma nativa o hash de senhas e a emissão de tokens JWT, garantindo maior segurança e conformidade.

2. VIDEO SERVICE (videos_service.py)
   Responsabilidade
   Este serviço tem uma única e forte responsabilidade: gerar URLs pré-assinadas para o upload de vídeos no S3. O fluxo de dados do vídeo em si não passa mais por este serviço.

Endpoint
POST /videos/upload-url - Gera uma URL de upload temporária e segura.

Lógica de Roteamento
Python

def handler(event, context):
file_name = event['fileName']
bucket_name = 'video-temp-conversion'

    # Gera a URL pré-assinada
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket_name, 'Key': file_name},
        ExpiresIn=3600  # URL expira em 1 hora
    )

    return success_response({'uploadUrl': response})

Configuração Lambda
Runtime: Python 3.11

Handler: videos_service.handler

Timeout: 10s (fluxo mais rápido, não há upload de dados)

Memory: 128MB (menos processamento)

3. MEDIACONVERT TRIGGER (mediaconvert_trigger.py)
   Responsabilidade
   Inicia a conversão automática do vídeo ao receber uma notificação de um novo arquivo no S3.

Trigger
SQS Queue, alimentada pelo SNS Topic.

Processo
Python

# 1. Recebe evento do SQS, que foi notificado pelo SNS.

# 2. Configura e inicia o job do MediaConvert.

# 3. Define a saída como MP4 no bucket principal.

# 4. Envia logs para CloudWatch.

4. CONVERSION COMPLETE (conversion_complete.py)
   Responsabilidade
   Limpa o arquivo original do bucket temporário após a conclusão bem-sucedida da conversão.

Trigger
EventBridge Rule, acionada pelo evento de conclusão do MediaConvert.

Processo
Python

# 1. Recebe evento do EventBridge de conclusão do MediaConvert.

# 2. Verifica se o status = 'COMPLETE'.

# 3. Deleta o arquivo original do S3 Temp.

# 4. Log da operação.

📊 FLUXO DE DADOS DETALHADO

1. FLUXO DE AUTENTICAÇÃO E MFA
   ┌─────────────┐ ┌─────────────────┐ ┌─────────────┐
   │ Usuario │ │ Amazon Cognito │ │ API Gateway │
   └──────┬──────┘ └──────┬──────────┘ └───────┬─────┘
   │ 1. Insere dados │ │
   │ (e-mail/senha) │ │
   ├─────────────────►│ │
   │ │ 2. Valida │ │
   │ │ credenciais │ │
   │ │ 3. Envia desafio│ │
   │◄─────────────────┤ MFA │
   │ 4. Insere código │ │
   │ MFA │ │
   ├─────────────────►│ │
   │ │ 5. Emite Tokens │ │
   │◄─────────────────┤ JWT │
2. FLUXO DE UPLOAD E CONVERSÃO
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │ Frontend │ │ Video Lambda│ │ S3 Temp │ │ MediaConvert│
   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
   │ 1. POST /videos/upload-url (token JWT) │ │
   ├─────────────────►│ │ │
   │ │ 2. Gera URL │ │
   │◄─────────────────┤ pré-assinada │
   │ 3. Upload direto │ │
   ├────────────────────────────────────►│ 4. Evento S3: 'ObjectCreated'
   │ │ ├─────────────────► SNS Topic
   │ │ │ │
   │ │ │ │ 5. Evento SNS → SQS Queue
   │ │ │ 6. Invoca Lambda│
   │ │ │ (via SQS) │
   │ │ │ 7. Cria Job │
   │ │ │ MediaConvert │
   │ │ │◄─────────────────┤
   │ │ │ │ 8. Converte e salva MP4
   │ │ │ │ em S3 Principal
   ☁️ INFRAESTRUTURA AWS
   Serviços Utilizados
3. Amazon Cognito
   ┌─────────────────────────────────────────────────────────────┐
   │                   AMAZON COGNITO USER POOL                 │
   ├─────────────────────────────────────────────────────────────┤
   │ User Pool ID: us-east-1_xyz123456                          │
   │ App Client: video-streaming-client                         │
   │ MFA: Ativado (Software Token)                               │
   └─────────────────────────────────────────────────────────────┘
4. AWS Lambda
   ┌─────────────────────────────────────────────────────────────┐
   │                    LAMBDA FUNCTIONS                         │
   ├─────────────────────────────────────────────────────────────┤
   │ Function Name          │ Runtime    │ Handler              │
   ├─────────────────────────────────────────────────────────────┤
   │ video-streaming-upload │ Python3.11 │ videos_service.handler│
   │ mediaconvert-trigger   │ Python3.11 │ mediaconvert_trigger │
   │ conversion-complete    │ Python3.11 │ conversion_complete  │
   └─────────────────────────────────────────────────────────────┘
5. Amazon SNS/SQS
   ┌─────────────────────────────────────────────────────────────┐
   │                    SNS TOPIC E SQS QUEUE                   │
   ├─────────────────────────────────────────────────────────────┤
   │ SNS Topic: arn:aws:sns:_:_:video-upload-events              │
   │ SQS Queue: arn:aws:sqs:_:_:mediaconvert-trigger-queue      │
   └─────────────────────────────────────────────────────────────┘
6. API Gateway
   ┌─────────────────────────────────────────────────────────────┐
   │                    API GATEWAY                              │
   ├─────────────────────────────────────────────────────────────┤
   │ Resources:                                                  │
   │ ├── /auth      → Cognito User Pool                          │
   │ └── /videos    → video-streaming-upload (com Cognito Auth)│
   └─────────────────────────────────────────────────────────────┘
   Observação: O S3, CloudFront, MediaConvert e as políticas IAM permanecem como no documento original, com a exceção de que as políticas IAM para as Lambdas devem ser ajustadas para permissões de menor privilégio.

🚀 DEPLOY
A estrutura de arquivos e scripts de deploy permanecem semelhantes, mas os scripts e comandos aws cli serão adaptados para refletir as novas integrações:

O deploy_refactored.bat agora também gerencia a configuração do Cognito, SNS, SQS e EventBridge.

Os comandos de deploy para as Lambdas e Frontend permanecem, mas a lógica de autenticação é migrada para o Cognito.

📊 MONITORAMENTO
As métricas e logs do CloudWatch serão os mesmos, com a adição de métricas do Amazon Cognito, como número de logins, logins com falha e eventos de MFA.

Métricas do Cognito: Usuários registrados, logins bem-sucedidos, MFA ativados.

SQS: mensagens na fila, mensagens processadas com sucesso/falha.

EventBridge: contagem de eventos de conclusão do MediaConvert.

🔒 SEGURANÇA
A segurança é o ponto mais forte da nova arquitetura.

Autenticação Avançada:

MFA Obrigatório: O Cognito garante que um segundo fator de autenticação seja necessário, aumentando significativamente a segurança da conta, mesmo em caso de comprometimento da senha.

Credenciais de Teste: O Cognito substitui a necessidade de credenciais estáticas no Secrets Manager, gerindo senhas de forma criptografada.

Autorização Robusta:

Autorizador Nativo do API Gateway: O API Gateway valida os tokens JWT gerados pelo Cognito de forma nativa e eficiente, sem a necessidade de uma Lambda para essa tarefa.

Dados e Upload:

URL Pré-assinada do S3: O frontend recebe uma URL temporária e segura para fazer o upload diretamente para o S3, evitando que os dados do vídeo passem pela infraestrutura de API e Lambda. Isso minimiza a superfície de ataque e reduz os custos de transferência.

Políticas de Menor Privilégio: As permissões IAM para as funções Lambda devem ser revisadas para conceder apenas o acesso estritamente necessário (ex: s3:PutObject para o mediaconvert_trigger em vez de s3:\*).

📞 SUPORTE E CONTATO
As informações de contato e URLs permanecem as mesmas, mas a documentação interna para as credenciais de teste agora se refere ao fluxo de usuário do Cognito.
