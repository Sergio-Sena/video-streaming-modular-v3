// Amazon Cognito Authentication Module
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';

class CognitoAuth {
    constructor() {
        this.poolData = {
            UserPoolId: 'us-east-1_XXXXXXXXX', // Será configurado
            ClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx'  // Será configurado
        };
        this.userPool = new CognitoUserPool(this.poolData);
        this.currentUser = null;
    }

    // Login com email/senha
    async login(email, password) {
        return new Promise((resolve, reject) => {
            const authenticationData = {
                Username: email,
                Password: password,
            };
            
            const authenticationDetails = new AuthenticationDetails(authenticationData);
            const userData = {
                Username: email,
                Pool: this.userPool,
            };
            
            const cognitoUser = new CognitoUser(userData);
            
            cognitoUser.authenticateUser(authenticationDetails, {
                onSuccess: (result) => {
                    this.currentUser = cognitoUser;
                    const token = result.getIdToken().getJwtToken();
                    localStorage.setItem('authToken', token);
                    resolve({ success: true, token });
                },
                onFailure: (err) => {
                    reject({ success: false, error: err.message });
                },
                mfaRequired: (codeDeliveryDetails) => {
                    // MFA será implementado se necessário
                    resolve({ mfaRequired: true, user: cognitoUser });
                }
            });
        });
    }

    // Verificar se está logado
    isAuthenticated() {
        const token = localStorage.getItem('authToken');
        if (!token) return false;
        
        // Verificar se token não expirou
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch {
            return false;
        }
    }

    // Logout
    logout() {
        if (this.currentUser) {
            this.currentUser.signOut();
        }
        localStorage.removeItem('authToken');
        this.currentUser = null;
    }

    // Obter token atual
    getToken() {
        return localStorage.getItem('authToken');
    }
}

export default new CognitoAuth();