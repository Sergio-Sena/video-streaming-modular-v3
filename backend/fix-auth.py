def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
            'Content-Type': 'application/json'
        },
        'body': '{"success": true, "message": "CORS OK", "token": "test-token", "user": {"email": "test@test.com"}}'
    }