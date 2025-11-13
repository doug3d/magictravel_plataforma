/**
 * Seller Admin Authentication Manager
 * Handles seller authentication and API requests for seller admin panel
 */

class AdminApiClient {
    constructor() {
        this.sellerToken = localStorage.getItem('seller_token');
    }
    
    /**
     * Get seller token
     */
    getSellerToken() {
        return localStorage.getItem('seller_token');
    }
    
    /**
     * Save seller token
     */
    saveSellerToken(token) {
        localStorage.setItem('seller_token', token);
        this.sellerToken = token;
    }
    
    /**
     * Clear seller token
     */
    clearSellerToken() {
        localStorage.removeItem('seller_token');
        this.sellerToken = null;
    }
    
    /**
     * Get headers for admin requests
     */
    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Adicionar Store-Credential se existir no localStorage
        const storeCredential = localStorage.getItem('store_credential');
        if (storeCredential) {
            headers['Store-Credential'] = storeCredential;
        }
        
        // Adicionar Seller-Authorization se existir
        const token = this.getSellerToken();
        if (token) {
            headers['Seller-Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }
    
    /**
     * Make API request
     */
    async _request(method, url, data = null) {
        const options = {
            method,
            headers: this._getHeaders()
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                // Token inválido ou expirado
                this.clearSellerToken();
                window.location.href = '/admin/login';
                throw new Error('Autenticação necessária');
            }
            
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        return response.json();
    }
    
    /**
     * GET request
     */
    async get(url) {
        return this._request('GET', url);
    }
    
    /**
     * POST request
     */
    async post(url, data) {
        return this._request('POST', url, data);
    }
    
    /**
     * PUT request
     */
    async put(url, data) {
        return this._request('PUT', url, data);
    }
    
    /**
     * DELETE request
     */
    async delete(url) {
        return this._request('DELETE', url);
    }
}

/**
 * Admin Auth Manager
 * Handles seller info display and logout
 */
class AdminAuthManager {
    constructor() {
        this.api = new AdminApiClient();
        this.init();
    }
    
    init() {
        // Verificar se está autenticado
        if (!this.api.getSellerToken()) {
            // Se não estiver na página de login, redirecionar
            if (!window.location.pathname.includes('/seller/admin/login')) {
                window.location.href = '/seller/admin/login';
            }
            this.hideLoadingScreen();
            return;
        }
        
        // Carregar informações do seller e então mostrar conteúdo
        this.loadSellerInfo();
        
        // Event listener para logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }
    
    /**
     * Esconde loading screen e mostra conteúdo
     */
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('authLoadingScreen');
        const adminContent = document.getElementById('adminContent');
        
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
        if (adminContent) {
            adminContent.style.display = 'flex';
        }
    }
    
    /**
     * Carregar informações do seller
     */
    async loadSellerInfo() {
        try {
            const response = await fetch('/sellers/me', {
                headers: {
                    'Seller-Authorization': `Bearer ${this.api.getSellerToken()}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Falha ao carregar informações do seller');
            }
            
            const seller = await response.json();
            
            // Verificar se seller tem loja
            if (!seller.store_id || !seller.store_credential) {
                console.error('Seller não tem loja configurada');
                alert('Você precisa criar uma loja antes de acessar o painel admin.');
                this.api.clearSellerToken();
                window.location.href = '/seller/admin/login';
                return;
            }
            
            // Salvar store credential para usar nas próximas requisições
            localStorage.setItem('store_credential', seller.store_credential);
            
            // Atualizar UI com informações do seller
            const sellerEmailEl = document.getElementById('sellerEmail');
            if (sellerEmailEl) {
                sellerEmailEl.textContent = seller.username;
            }
            
            // Atualizar nome da loja
            const storeNameEl = document.getElementById('storeName');
            if (storeNameEl && seller.store_name) {
                storeNameEl.textContent = `🏪 ${seller.store_name}`;
            }
            
            // Autenticação OK, mostrar conteúdo
            this.hideLoadingScreen();
            
            // Disparar evento de que auth está pronto
            window.dispatchEvent(new Event('adminAuthReady'));
        } catch (error) {
            console.error('Erro ao carregar seller:', error);
            // Se falhar, redirecionar para login
            this.api.clearSellerToken();
            window.location.href = '/seller/admin/login';
        }
    }

    
    /**
     * Fazer logout
     */
    logout() {
        if (confirm('Deseja realmente sair do painel admin?')) {
            this.api.clearSellerToken();
            localStorage.removeItem('store_credential');
            window.location.href = '/seller/admin/login';
        }
    }
}

// Instanciar globalmente
window.adminApi = new AdminApiClient();
window.adminAuth = new AdminAuthManager();

