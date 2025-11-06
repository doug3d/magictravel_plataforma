# 🎨 Guia de Desenvolvimento Frontend

## 🎯 Objetivo

Este documento é um guia prático para desenvolver o frontend do Magic Marketplace, focado em React/Next.js ou Vue/Nuxt.

---

## 📋 Checklist de Implementação

### Fase 1: Setup Inicial ✅
- [ ] Configurar projeto (React/Vue)
- [ ] Instalar dependências (axios, react-router/vue-router)
- [ ] Configurar variáveis de ambiente
- [ ] Criar cliente HTTP com interceptors
- [ ] Implementar gerenciamento de estado (Context/Zustand/Pinia)

### Fase 2: Autenticação 🔐
- [ ] Página de login Seller
- [ ] Página de cadastro Seller
- [ ] Página de login Customer
- [ ] Página de cadastro Customer
- [ ] Gerenciar tokens no localStorage
- [ ] Implementar auto-refresh/logout

### Fase 3: Área do Seller 🏪
- [ ] Dashboard inicial
- [ ] Criar loja
- [ ] Visualizar credential da loja
- [ ] Adicionar produtos manualmente (opcional)
- [ ] Ver produtos em destaque

### Fase 4: Catálogo de Produtos (Maria API) 📦
- [ ] Listar parques disponíveis
- [ ] Filtros (localização, data)
- [ ] Visualizar produtos de um parque
- [ ] Detalhes do produto
- [ ] Adicionar ao carrinho (cria produto no backend)

### Fase 5: Carrinho e Checkout 🛒
- [ ] Visualizar carrinho
- [ ] Atualizar quantidade
- [ ] Remover itens
- [ ] Calcular total
- [ ] Finalizar pedido

### Fase 6: Pedidos 📦
- [ ] Listar pedidos do customer
- [ ] Detalhes do pedido
- [ ] Status do pedido

---

## 🏗️ Estrutura de Projeto Sugerida

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── products/
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductList.tsx
│   │   │   ├── ProductDetail.tsx
│   │   │   └── ProductFilters.tsx
│   │   ├── cart/
│   │   │   ├── CartIcon.tsx
│   │   │   ├── CartItem.tsx
│   │   │   └── CartSummary.tsx
│   │   └── orders/
│   │       ├── OrderCard.tsx
│   │       └── OrderDetail.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Parks.tsx
│   │   ├── Products.tsx
│   │   ├── ProductDetail.tsx
│   │   ├── Cart.tsx
│   │   ├── Checkout.tsx
│   │   └── Orders.tsx
│   ├── services/
│   │   ├── api.ts              # Cliente HTTP configurado
│   │   ├── authService.ts      # Login, register, logout
│   │   ├── mariaApiService.ts  # Integração Maria API
│   │   ├── cartService.ts      # Carrinho
│   │   └── orderService.ts     # Pedidos
│   ├── store/
│   │   ├── authStore.ts        # Estado de autenticação
│   │   ├── cartStore.ts        # Estado do carrinho
│   │   └── productsStore.ts    # Cache de produtos
│   ├── types/
│   │   ├── auth.ts
│   │   ├── product.ts
│   │   ├── cart.ts
│   │   └── order.ts
│   └── utils/
│       ├── formatters.ts       # Formatação de preços, datas
│       └── validators.ts       # Validações de formulário
└── .env
```

---

## ⚙️ Setup Inicial

### 1. Cliente HTTP (Axios)

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
});

// Interceptor para adicionar headers automaticamente
api.interceptors.request.use(config => {
  const userType = localStorage.getItem('user_type'); // 'seller' ou 'customer'
  const token = localStorage.getItem(`${userType}_token`);
  const storeCredential = localStorage.getItem('store_credential');
  
  if (token) {
    const headerName = userType === 'seller' 
      ? 'Seller-Authorization' 
      : 'Customer-Authorization';
    config.headers[headerName] = `Bearer ${token}`;
  }
  
  if (storeCredential) {
    config.headers['Store-Credential'] = storeCredential;
  }
  
  return config;
});

// Interceptor para tratar erros
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 403) {
      // Token inválido - redirecionar para login
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Variáveis de Ambiente

```env
# .env
VITE_BACKEND_URL=http://localhost:8000
VITE_MARIA_API_URL=http://localhost:8001
```

---

## 🔐 Autenticação

### Service de Autenticação

```typescript
// src/services/authService.ts
import api from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  name: string;
}

export interface AuthResponse {
  access_token: string;
  seller_id?: number;
  customer_id?: number;
  name: string;
}

class AuthService {
  // Seller
  async registerSeller(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post('/sellers/', data);
    this.saveSeller(response.data);
    return response.data;
  }

  async loginSeller(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/sellers/auth', data);
    this.saveSeller(response.data);
    return response.data;
  }

  // Customer
  async registerCustomer(data: RegisterRequest, storeCredential: string): Promise<AuthResponse> {
    const response = await api.post('/customers/', data, {
      headers: { 'Store-Credential': storeCredential }
    });
    this.saveCustomer(response.data);
    return response.data;
  }

  async loginCustomer(data: LoginRequest, storeCredential: string): Promise<AuthResponse> {
    const response = await api.post('/customers/auth', data, {
      headers: { 'Store-Credential': storeCredential }
    });
    this.saveCustomer(response.data);
    return response.data;
  }

  // Helpers
  private saveSeller(data: AuthResponse) {
    localStorage.setItem('user_type', 'seller');
    localStorage.setItem('seller_token', data.access_token);
    localStorage.setItem('user_name', data.name);
    localStorage.setItem('seller_id', String(data.seller_id));
  }

  private saveCustomer(data: AuthResponse) {
    localStorage.setItem('user_type', 'customer');
    localStorage.setItem('customer_token', data.access_token);
    localStorage.setItem('user_name', data.name);
    localStorage.setItem('customer_id', String(data.customer_id));
  }

  logout() {
    localStorage.clear();
    window.location.href = '/login';
  }

  isAuthenticated(): boolean {
    const userType = localStorage.getItem('user_type');
    return !!localStorage.getItem(`${userType}_token`);
  }

  getUserType(): 'seller' | 'customer' | null {
    return localStorage.getItem('user_type') as 'seller' | 'customer' | null;
  }
}

export default new AuthService();
```

### Componente de Login

```typescript
// src/pages/Login.tsx
import { useState } from 'react';
import authService from '../services/authService';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState<'seller' | 'customer'>('customer');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (userType === 'seller') {
        await authService.loginSeller({ email, password });
        window.location.href = '/dashboard';
      } else {
        const storeCredential = localStorage.getItem('store_credential') || '';
        await authService.loginCustomer({ email, password }, storeCredential);
        window.location.href = '/products';
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      
      <div className="user-type-selector">
        <button onClick={() => setUserType('customer')}>Cliente</button>
        <button onClick={() => setUserType('seller')}>Vendedor</button>
      </div>

      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Senha"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </div>
  );
}
```

---

## 📦 Catálogo de Produtos (Maria API)

### Service Maria API

```typescript
// src/services/mariaApiService.ts
import axios from 'axios';

const mariaApi = axios.create({
  baseURL: import.meta.env.VITE_MARIA_API_URL || 'http://localhost:8001',
});

export interface Park {
  code: string;
  name: string;
  description: string;
  images: {
    cover: string;
    thumbnail: string;
  };
  parklocation: {
    city: string;
    state: string;
  };
  attraction: string;
  status: boolean;
}

export interface Product {
  code: string;
  ticketName: string;
  parkIncluded: string;
  parkLocation: {
    city: string;
    state: string;
  };
  isMultiDays: boolean;
  isParkToPark: boolean;
  extensions: {
    numberDays: number;
    numberParks: number;
    productKind: string;
    ticketType: string;
  };
  prices: {
    adult: {
      usdbrl: {
        amount: string;
        currency: string;
        symbol: string;
      };
    };
    total: {
      usdbrl: {
        amount: string;
        currency: string;
        symbol: string;
      };
    };
  };
  isSpecial: boolean;
}

class MariaApiService {
  async getParks(location: string = 'FL'): Promise<Park[]> {
    const response = await mariaApi.get('/parks/', { params: { location } });
    return response.data;
  }

  async getProducts(parkCode: string, filters?: {
    forDate?: string;
    numberDays?: number;
    numAdults?: number;
    numChildren?: number;
  }): Promise<Product[]> {
    const response = await mariaApi.get(`/parks/${parkCode}/products`, {
      params: filters
    });
    return response.data;
  }

  async getProductDetail(parkCode: string, productCode: string): Promise<Product> {
    const response = await mariaApi.get(`/parks/${parkCode}/products/${productCode}`);
    return response.data;
  }
}

export default new MariaApiService();
```

### Componente de Produtos

```typescript
// src/pages/Products.tsx
import { useState, useEffect } from 'react';
import mariaApiService, { Park, Product } from '../services/mariaApiService';
import cartService from '../services/cartService';

export function Products() {
  const [parks, setParks] = useState<Park[]>([]);
  const [selectedPark, setSelectedPark] = useState<Park | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadParks();
  }, []);

  const loadParks = async () => {
    setLoading(true);
    try {
      const data = await mariaApiService.getParks();
      setParks(data);
      if (data.length > 0) {
        selectPark(data[0]);
      }
    } catch (error) {
      console.error('Erro ao carregar parques', error);
    } finally {
      setLoading(false);
    }
  };

  const selectPark = async (park: Park) => {
    setSelectedPark(park);
    setLoading(true);
    try {
      const data = await mariaApiService.getProducts(park.code);
      setProducts(data);
    } catch (error) {
      console.error('Erro ao carregar produtos', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (product: Product) => {
    if (!selectedPark) return;
    
    setLoading(true);
    try {
      await cartService.addToCart({
        maria_product_code: product.code,
        park_code: selectedPark.code,
        amount: 1
      });
      alert('Produto adicionado ao carrinho!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao adicionar produto');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="products-page">
      <h1>Catálogo de Produtos</h1>

      {/* Seletor de Parques */}
      <div className="parks-selector">
        {parks.map(park => (
          <button
            key={park.code}
            onClick={() => selectPark(park)}
            className={selectedPark?.code === park.code ? 'active' : ''}
          >
            {park.name}
          </button>
        ))}
      </div>

      {/* Lista de Produtos */}
      {loading ? (
        <div>Carregando...</div>
      ) : (
        <div className="products-grid">
          {products.map(product => (
            <div key={product.code} className="product-card">
              <h3>{product.ticketName}</h3>
              <p>{product.parkIncluded}</p>
              <p className="price">
                {product.prices.total.usdbrl.symbol} {product.prices.total.usdbrl.amount}
              </p>
              <p className="details">
                {product.extensions.numberDays} dia(s) • 
                {product.extensions.numberParks} parque(s)
              </p>
              <button onClick={() => addToCart(product)}>
                Adicionar ao Carrinho
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🛒 Carrinho

### Service de Carrinho

```typescript
// src/services/cartService.ts
import api from './api';

export interface AddToCartRequest {
  maria_product_code: string;
  park_code: string;
  amount: number;
}

export interface CartItem {
  product_id: number;
  product_name: string;
  price: number;
  amount: number;
}

export interface Cart {
  cart_empty: boolean;
  items: CartItem[];
}

class CartService {
  async addToCart(data: AddToCartRequest): Promise<Cart> {
    const response = await api.post('/carts/', data);
    return response.data;
  }

  async getCart(): Promise<Cart> {
    const response = await api.get('/carts/me');
    return response.data;
  }

  async updateAmount(productId: number, amount: number): Promise<Cart> {
    const response = await api.put('/carts/update-amount', {
      product_id: productId,
      amount
    });
    return response.data;
  }

  async removeItem(productId: number): Promise<Cart> {
    const response = await api.delete(`/carts/${productId}`);
    return response.data;
  }
}

export default new CartService();
```

---

## 💡 Dicas Importantes

### 1. Formatação de Preços

```typescript
// src/utils/formatters.ts
export function formatPrice(cents: number): string {
  return (cents / 100).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  });
}

// Uso
formatPrice(12948) // → "R$ 129,48"
```

### 2. Estados de Loading

```typescript
const [loading, setLoading] = useState({
  parks: false,
  products: false,
  cart: false
});

// Uso
setLoading(prev => ({ ...prev, products: true }));
```

### 3. Error Handling

```typescript
try {
  await cartService.addToCart(data);
} catch (error: any) {
  const message = error.response?.data?.detail || 'Erro desconhecido';
  
  if (error.response?.status === 404) {
    toast.error('Produto não disponível');
  } else if (error.response?.status === 403) {
    toast.error('Você precisa fazer login');
    router.push('/login');
  } else {
    toast.error(message);
  }
}
```

### 4. Protected Routes

```typescript
// src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  return <>{children}</>;
}

// Uso no router
<Route path="/cart" element={
  <ProtectedRoute>
    <Cart />
  </ProtectedRoute>
} />
```

---

## 🎨 Sugestões de UI/UX

### Badge de Carrinho

```typescript
// src/components/common/Header.tsx
<Link to="/cart">
  <ShoppingCart />
  {cartCount > 0 && <Badge>{cartCount}</Badge>}
</Link>
```

### Indicador de Preço Atualizado

```typescript
<ProductCard>
  <Price>{formatPrice(product.price)}</Price>
  <Badge color="blue">Preço em tempo real</Badge>
</ProductCard>
```

### Feedback Visual ao Adicionar ao Carrinho

```typescript
const [addedToCart, setAddedToCart] = useState(false);

const handleAddToCart = async () => {
  await cartService.addToCart(...);
  setAddedToCart(true);
  setTimeout(() => setAddedToCart(false), 2000);
};

<button disabled={addedToCart}>
  {addedToCart ? '✓ Adicionado!' : 'Adicionar ao Carrinho'}
</button>
```

---

## 📚 Próximos Passos

1. ✅ Implementar autenticação
2. ✅ Integrar com Maria API (catálogo)
3. ✅ Implementar carrinho
4. ⏭️ Implementar checkout e pedidos
5. ⏭️ Dashboard do seller
6. ⏭️ Histórico de pedidos
7. ⏭️ Perfil do usuário

---

## 🔗 Links Úteis

- [API Endpoints](./API_ENDPOINTS.md)
- [Product Flow](./PRODUCT_FLOW.md)
- [Authentication](./AUTHENTICATION.md)
- [Maria API Integration](./MARIA_API_INTEGRATION.md)

