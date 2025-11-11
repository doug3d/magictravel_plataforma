/**
 * Auth Modal Manager
 * Gerencia o modal de login/cadastro
 */

class AuthModal {
    constructor() {
        this.modal = null;
        this.overlay = null;
        this.onSuccessCallback = null;
        this.currentTab = 'login';
        
        this.init();
    }
    
    init() {
        // Aguarda o DOM carregar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
    }
    
    setupElements() {
        this.modal = document.getElementById('authModal');
        this.overlay = document.getElementById('authOverlay');
        
        if (!this.modal || !this.overlay) {
            console.error('Auth modal elements not found');
            return;
        }
        
        // Event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Fechar modal
        const closeBtn = document.getElementById('closeAuthModal');
        closeBtn?.addEventListener('click', () => this.close());
        
        // Fechar ao clicar no overlay
        this.overlay?.addEventListener('click', () => this.close());
        
        // Fechar com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
        
        // Tabs
        const loginTab = document.getElementById('loginTab');
        const registerTab = document.getElementById('registerTab');
        
        loginTab?.addEventListener('click', () => this.switchTab('login'));
        registerTab?.addEventListener('click', () => this.switchTab('register'));
        
        // Formulário de login
        const loginForm = document.getElementById('loginForm');
        loginForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        // Formulário de cadastro
        const registerForm = document.getElementById('registerForm');
        registerForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
    }
    
    /**
     * Abre o modal
     * @param {Function} onSuccess - Callback chamado após login bem-sucedido
     */
    open(onSuccess = null) {
        this.onSuccessCallback = onSuccess;
        this.modal?.classList.add('active');
        this.overlay?.classList.add('active');
        
        // Foca no primeiro campo
        setTimeout(() => {
            const firstInput = this.modal?.querySelector('input:not([type="hidden"])');
            firstInput?.focus();
        }, 100);
    }
    
    /**
     * Fecha o modal
     */
    close() {
        this.modal?.classList.remove('active');
        this.overlay?.classList.remove('active');
        this.clearErrors();
        this.resetForms();
    }
    
    /**
     * Verifica se o modal está aberto
     */
    isOpen() {
        return this.modal?.classList.contains('active');
    }
    
    /**
     * Troca entre tabs (login/cadastro)
     */
    switchTab(tab) {
        this.currentTab = tab;
        
        const loginTab = document.getElementById('loginTab');
        const registerTab = document.getElementById('registerTab');
        const loginContent = document.getElementById('loginContent');
        const registerContent = document.getElementById('registerContent');
        
        if (tab === 'login') {
            loginTab?.classList.add('active');
            registerTab?.classList.remove('active');
            loginContent?.classList.add('active');
            registerContent?.classList.remove('active');
        } else {
            loginTab?.classList.remove('active');
            registerTab?.classList.add('active');
            loginContent?.classList.remove('active');
            registerContent?.classList.add('active');
        }
        
        this.clearErrors();
    }
    
    /**
     * Mostra erro no formulário
     */
    showError(message, formType = 'login') {
        const errorElement = document.getElementById(`${formType}Error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }
    
    /**
     * Limpa mensagens de erro
     */
    clearErrors() {
        const loginError = document.getElementById('loginError');
        const registerError = document.getElementById('registerError');
        
        if (loginError) {
            loginError.textContent = '';
            loginError.style.display = 'none';
        }
        
        if (registerError) {
            registerError.textContent = '';
            registerError.style.display = 'none';
        }
    }
    
    /**
     * Reseta os formulários
     */
    resetForms() {
        document.getElementById('loginForm')?.reset();
        document.getElementById('registerForm')?.reset();
    }
    
    /**
     * Ativa estado de loading em um botão
     */
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<span class="spinner-small"></span> Processando...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }
    
    /**
     * Handler de login
     */
    async handleLogin() {
        const email = document.getElementById('loginEmail')?.value;
        const password = document.getElementById('loginPassword')?.value;
        const submitBtn = document.querySelector('#loginForm button[type="submit"]');
        
        this.clearErrors();
        
        // Validação básica
        if (!email || !password) {
            this.showError('Preencha todos os campos', 'login');
            return;
        }
        
        this.setButtonLoading(submitBtn, true);
        
        try {
            // Usa o api.js, mas sem passar pelo interceptor de 403
            // (senão criaria um loop)
            const response = await fetch('/customers/auth', {
                method: 'POST',
                headers: window.api.getHeaders(),
                body: JSON.stringify({ email, password })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Erro ao fazer login');
            }
            
            const data = await response.json();
            
            // Salva o token
            window.api.setCustomerToken(data.access_token);
            
            // Fecha o modal
            this.close();
            
            // Mostra notificação
            this.showNotification(`Bem-vindo, ${data.name}! ✨`);
            
            // Chama callback de sucesso (retry da operação)
            if (this.onSuccessCallback) {
                await this.onSuccessCallback();
                this.onSuccessCallback = null;
            }
            
            // Recarrega o carrinho
            if (window.cartManager) {
                await window.cartManager.loadCart();
            }
            
        } catch (error) {
            console.error('Erro no login:', error);
            this.showError(error.message || 'Erro ao fazer login. Tente novamente.', 'login');
        } finally {
            this.setButtonLoading(submitBtn, false);
        }
    }
    
    /**
     * Handler de cadastro
     */
    async handleRegister() {
        const name = document.getElementById('registerName')?.value;
        const email = document.getElementById('registerEmail')?.value;
        const password = document.getElementById('registerPassword')?.value;
        const submitBtn = document.querySelector('#registerForm button[type="submit"]');
        
        this.clearErrors();
        
        // Validação básica
        if (!name || !email || !password) {
            this.showError('Preencha todos os campos', 'register');
            return;
        }
        
        if (password.length < 6) {
            this.showError('A senha deve ter pelo menos 6 caracteres', 'register');
            return;
        }
        
        this.setButtonLoading(submitBtn, true);
        
        try {
            // Usa o api.js, mas sem passar pelo interceptor de 403
            const response = await fetch('/customers/', {
                method: 'POST',
                headers: window.api.getHeaders(),
                body: JSON.stringify({ name, email, password })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Erro ao criar conta');
            }
            
            const data = await response.json();
            
            // Salva o token
            window.api.setCustomerToken(data.access_token);
            
            // Fecha o modal
            this.close();
            
            // Mostra notificação
            this.showNotification(`Conta criada com sucesso! Bem-vindo, ${data.name}! 🎉`);
            
            // Chama callback de sucesso (retry da operação)
            if (this.onSuccessCallback) {
                await this.onSuccessCallback();
                this.onSuccessCallback = null;
            }
            
            // Recarrega o carrinho
            if (window.cartManager) {
                await window.cartManager.loadCart();
            }
            
        } catch (error) {
            console.error('Erro no cadastro:', error);
            this.showError(error.message || 'Erro ao criar conta. Tente novamente.', 'register');
        } finally {
            this.setButtonLoading(submitBtn, false);
        }
    }
    
    /**
     * Mostra notificação temporária
     */
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'auth-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Inicializa o gerenciador do modal globalmente
window.authModal = new AuthModal();

