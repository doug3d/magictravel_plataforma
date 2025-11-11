/**
 * Global Cart Manager
 * Gerencia o estado e interações do carrinho de compras
 */

class CartManager {
    constructor() {
        this.cartData = null;
        this.sidebar = document.getElementById('cartSidebar');
        this.overlay = document.getElementById('cartOverlay');
        this.mainContainer = document.getElementById('mainContainer');
        this.closeBtn = document.getElementById('closeCartBtn');
        this.checkoutBtn = document.getElementById('checkoutBtn');
        this.cartMenuLink = document.getElementById('cartMenuLink');
        this.cartBadge = document.getElementById('cartBadge');
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.closeBtn?.addEventListener('click', () => this.closeCart());
        this.overlay?.addEventListener('click', () => this.closeCart());
        this.checkoutBtn?.addEventListener('click', () => this.handleCheckout());
        
        // Abrir carrinho ao clicar no menu
        this.cartMenuLink?.addEventListener('click', (e) => {
            e.preventDefault();
            this.openCart();
        });
        
        // Carregar carrinho ao iniciar
        this.loadCart();
    }
    
    /**
     * Abre o sidebar do carrinho
     */
    openCart() {
        this.sidebar?.classList.add('open');
        this.overlay?.classList.add('active');
        this.mainContainer?.classList.add('cart-open');
    }
    
    /**
     * Fecha o sidebar do carrinho
     */
    closeCart() {
        this.sidebar?.classList.remove('open');
        this.overlay?.classList.remove('active');
        this.mainContainer?.classList.remove('cart-open');
    }
    
    /**
     * Carrega o carrinho atual do backend
     */
    async loadCart() {
        try {
            this.cartData = await window.api.get('/carts/current');
            this.renderCart();
            
            // Se tiver itens, não abre automaticamente (deixa o badge visível)
            // Usuário pode clicar no badge para abrir
        } catch (error) {
            // Se for erro de autenticação, não mostra erro
            if (error instanceof AuthenticationError) {
                console.warn('Customer não autenticado');
                this.renderEmptyCart();
                return;
            }
            
            console.error('Erro ao carregar carrinho:', error);
            this.renderEmptyCart();
        }
    }
    
    /**
     * Atualiza o badge do carrinho no menu
     */
    updateCartBadge() {
        if (!this.cartBadge) return;
        
        const itemCount = this.getItemCount();
        
        if (itemCount > 0) {
            this.cartBadge.textContent = itemCount;
            this.cartBadge.style.display = 'inline-block';
        } else {
            this.cartBadge.style.display = 'none';
        }
    }
    
    /**
     * Retorna a quantidade total de itens no carrinho
     */
    getItemCount() {
        if (!this.cartData || this.cartData.cart_empty) {
            return 0;
        }
        
        return this.cartData.items.reduce((sum, item) => sum + item.amount, 0);
    }
    
    /**
     * Adiciona um produto ao carrinho
     * @param {string} productCode - Código do produto na Maria API
     * @param {string} parkCode - Código do parque na Maria API
     * @param {number} amount - Quantidade
     */
    async addProduct(productCode, parkCode, amount = 1) {
        try {
            // 1. Converter código externo para ID interno
            const { product_id } = await window.api.get(
                `/products/by-external-code?product_code=${encodeURIComponent(productCode)}&park_code=${encodeURIComponent(parkCode)}`
            );
            
            // 2. Adicionar ao carrinho
            this.cartData = await window.api.post('/carts/', {
                product_id: product_id,
                amount: amount
            });
            
            this.renderCart();
            this.openCart();
            
            // Feedback visual
            this.showNotification('✅ Produto adicionado ao carrinho!');
            
            return true;
        } catch (error) {
            // Se for erro de autenticação, o modal já foi aberto automaticamente
            if (error instanceof AuthenticationError) {
                return false;
            }
            
            console.error('Erro ao adicionar produto:', error);
            alert('Erro ao adicionar produto ao carrinho. Tente novamente.');
            return false;
        }
    }
    
    /**
     * Atualiza a quantidade de um item no carrinho
     * @param {number} productId - ID interno do produto
     * @param {number} amount - Nova quantidade
     */
    async updateAmount(productId, amount) {
        try {
            this.cartData = await window.api.put('/carts/update-amount', {
                product_id: productId,
                amount: amount
            });
            
            this.renderCart();
        } catch (error) {
            // Se for erro de autenticação, o modal já foi aberto automaticamente
            if (error instanceof AuthenticationError) {
                return;
            }
            
            console.error('Erro ao atualizar quantidade:', error);
            alert('Erro ao atualizar quantidade. Tente novamente.');
        }
    }
    
    /**
     * Remove um item do carrinho
     * @param {number} productId - ID interno do produto
     */
    async removeItem(productId) {
        try {
            this.cartData = await window.api.delete(`/carts/${productId}`);
            this.renderCart();
            
            this.showNotification('Item removido do carrinho');
        } catch (error) {
            // Se for erro de autenticação, o modal já foi aberto automaticamente
            if (error instanceof AuthenticationError) {
                return;
            }
            
            console.error('Erro ao remover item:', error);
            alert('Erro ao remover item. Tente novamente.');
        }
    }
    
    /**
     * Formata preço em centavos para string formatada
     * @param {number} cents - Preço em centavos
     */
    formatPrice(cents) {
        const value = cents / 100;
        return value.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    /**
     * Renderiza o carrinho vazio
     */
    renderEmptyCart() {
        document.getElementById('cartEmpty').style.display = 'block';
        document.getElementById('cartItems').style.display = 'none';
        document.getElementById('cartFooter').style.display = 'none';
        this.updateCartBadge();
    }
    
    /**
     * Renderiza o carrinho com itens
     */
    renderCart() {
        if (!this.cartData || this.cartData.cart_empty) {
            this.renderEmptyCart();
            return;
        }
        
        // Atualizar badge
        this.updateCartBadge();
        
        // Esconder empty state
        document.getElementById('cartEmpty').style.display = 'none';
        document.getElementById('cartItems').style.display = 'flex';
        document.getElementById('cartFooter').style.display = 'block';
        
        // Renderizar itens
        const cartItemsContainer = document.getElementById('cartItems');
        cartItemsContainer.innerHTML = this.cartData.items.map(item => `
            <div class="cart-item" data-product-id="${item.product_id}">
                <div class="cart-item-header">
                    <div class="cart-item-name">${item.product_name}</div>
                    <button class="cart-item-remove" onclick="window.cartManager.removeItem(${item.product_id})" title="Remover item">
                        ✕
                    </button>
                </div>
                
                <div class="cart-item-details">
                    <div class="cart-item-quantity">
                        <button class="quantity-btn" onclick="window.cartManager.updateAmount(${item.product_id}, ${item.amount - 1})" ${item.amount <= 1 ? 'disabled' : ''}>
                            −
                        </button>
                        <span class="quantity-value">${item.amount}</span>
                        <button class="quantity-btn" onclick="window.cartManager.updateAmount(${item.product_id}, ${item.amount + 1})">
                            +
                        </button>
                    </div>
                    
                    <div class="cart-item-price">
                        <div class="item-unit-price">R$ ${this.formatPrice(item.price)} cada</div>
                        <div class="item-total-price">R$ ${this.formatPrice(item.price * item.amount)}</div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Calcular e mostrar total
        const total = this.cartData.items.reduce((sum, item) => sum + (item.price * item.amount), 0);
        document.getElementById('cartTotal').textContent = `R$ ${this.formatPrice(total)}`;
    }
    
    /**
     * Handler do botão "Continuar"
     */
    handleCheckout() {
        console.log('=== CHECKOUT DEBUG ===');
        console.log('Cart Data:', this.cartData);
        console.log('Items:', this.cartData?.items);
        
        if (this.cartData?.items) {
            const total = this.cartData.items.reduce((sum, item) => sum + (item.price * item.amount), 0);
            console.log('Total (centavos):', total);
            console.log('Total (BRL):', this.formatPrice(total));
        }
        
        console.log('=====================');
        
        // TODO: Implementar navegação para checkout
        alert('Função de checkout será implementada em breve!');
    }
    
    /**
     * Mostra notificação temporária
     */
    showNotification(message) {
        // Implementação simples com alert por enquanto
        // TODO: Criar notificação toast mais elegante
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

// Adicionar animações para notificações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Inicializar o gerenciador de carrinho globalmente
window.cartManager = new CartManager();

