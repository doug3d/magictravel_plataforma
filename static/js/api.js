/**
 * API Client - Cliente HTTP Centralizado
 * Gerencia todas as requisições HTTP do site com autenticação automática
 */

/**
 * Erro customizado para problemas de autenticação
 */
class AuthenticationError extends Error {
    constructor(message, response) {
        super(message);
        this.name = 'AuthenticationError';
        this.response = response;
    }
}

/**
 * Cliente HTTP centralizado
 */
class ApiClient {
    constructor() {
        // Credencial da loja (do seed)
        this.storeCredential = '6059a3f072994bfc806a18cb098b265e';
        
        // Callback pendente para retry após login
        this.pendingRetry = null;
    }
    
    /**
     * Busca o token de autenticação do customer
     */
    getCustomerToken() {
        return localStorage.getItem('customer_token');
    }
    
    /**
     * Salva o token de autenticação do customer
     */
    setCustomerToken(token) {
        localStorage.setItem('customer_token', token);
    }
    
    /**
     * Remove o token de autenticação (logout)
     */
    clearCustomerToken() {
        localStorage.removeItem('customer_token');
    }
    
    /**
     * Monta os headers padrão para requisições
     */
    getHeaders(customHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            'Store-Credential': this.storeCredential,
            ...customHeaders
        };
        
        // Adiciona token de customer se existir
        const token = this.getCustomerToken();
        if (token) {
            headers['Customer-Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }
    
    /**
     * Intercepta resposta e trata erros
     */
    async handleResponse(response, requestFn) {
        // Sucesso
        if (response.ok) {
            // Se não tem conteúdo, retorna vazio
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                return null;
            }
            return await response.json();
        }
        
        // Erro 403 - Não autenticado
        if (response.status === 403) {
            const errorData = await response.json().catch(() => ({}));
            
            // Se é erro de store credential, não mostra modal
            if (errorData.detail === 'Store credential is invalid') {
                throw new Error('Erro de configuração: credencial da loja inválida');
            }
            
            // Se é erro de customer authorization, abre modal
            if (errorData.detail === 'Unauthorized') {
                // Armazena a função para retry
                this.pendingRetry = requestFn;
                
                // Abre o modal de autenticação
                if (window.authModal) {
                    window.authModal.open(() => {
                        // Callback: retenta a requisição após login
                        return requestFn();
                    });
                }
                
                throw new AuthenticationError('Autenticação necessária', response);
            }
        }
        
        // Outros erros HTTP
        let errorMessage = `Erro ${response.status}`;
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
            // Se não conseguir parsear JSON, usa mensagem padrão
        }
        
        throw new Error(errorMessage);
    }
    
    /**
     * Requisição GET
     */
    async get(url, options = {}) {
        const requestFn = () => this.get(url, options);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(options.headers),
            ...options
        });
        
        return this.handleResponse(response, requestFn);
    }
    
    /**
     * Requisição POST
     */
    async post(url, data = null, options = {}) {
        const requestFn = () => this.post(url, data, options);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: this.getHeaders(options.headers),
            body: data ? JSON.stringify(data) : undefined,
            ...options
        });
        
        return this.handleResponse(response, requestFn);
    }
    
    /**
     * Requisição PUT
     */
    async put(url, data = null, options = {}) {
        const requestFn = () => this.put(url, data, options);
        
        const response = await fetch(url, {
            method: 'PUT',
            headers: this.getHeaders(options.headers),
            body: data ? JSON.stringify(data) : undefined,
            ...options
        });
        
        return this.handleResponse(response, requestFn);
    }
    
    /**
     * Requisição DELETE
     */
    async delete(url, options = {}) {
        const requestFn = () => this.delete(url, options);
        
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this.getHeaders(options.headers),
            ...options
        });
        
        return this.handleResponse(response, requestFn);
    }
    
    /**
     * Retenta a última requisição pendente
     * Chamado após login bem-sucedido
     */
    async retryPendingRequest() {
        if (this.pendingRetry) {
            const retry = this.pendingRetry;
            this.pendingRetry = null;
            return await retry();
        }
        return null;
    }
}

// Inicializa o cliente API globalmente
window.api = new ApiClient();
window.AuthenticationError = AuthenticationError;

