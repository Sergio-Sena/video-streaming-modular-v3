// Correção rápida CORS para produção
const headers = {
    'Access-Control-Allow-Origin': '*', // Permite qualquer origem
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
    'Content-Type': 'application/json'
};