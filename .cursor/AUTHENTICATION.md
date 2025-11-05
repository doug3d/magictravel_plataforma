# Sistema de Autenticação e Autorização

## 🔐 Visão Geral

O Magic Marketplace usa um sistema de autenticação **baseado em tokens** com **múltiplos tipos de usuários** e **isolamento por tenant (Store)**.

---

## 👥 Tipos de Usuários

### 1. Seller (Vendedor)
- Cria e gerencia lojas
- Adiciona produtos às lojas
- Acessa métricas e relatórios

### 2. Customer (Cliente)
- Compra produtos de uma loja
- Gerencia carrinho e pedidos
- Vinculado a uma loja específica

---

## 🔑 Estrutura de Autenticação

### Tokens

```python
# UUID v4 usado como token
import uuid
access_token = str(uuid.uuid4())  
# Exemplo: "550e8400-e29b-41d4-a716-446655440000"
```

### Tabelas de Autenticação

#### SellerAuth
```python
class SellerAuth(Model):
    id = fields.IntField(primary_key=True)
    seller = fields.ForeignKeyField("models.Seller")
    access_token = fields.CharField(max_length=255)
    status = fields.CharField(choices=AUTH_STATUS, default='valid')
    created_at = fields.DatetimeField(auto_now_add=True)
```

#### CustomerAuth
```python
class CustomerAuth(Model):
    id = fields.IntField(primary_key=True)
    customer = fields.ForeignKeyField("models.Customer")
    access_token = fields.CharField(max_length=255)
    status = fields.CharField(choices=AUTH_STATUS, default='valid')
    created_at = fields.DatetimeField(auto_now_add=True)
```

### Status de Token
- `valid`: Token ativo e utilizável
- `invalidated`: Token revogado (logout/novo login)

---

## 🔒 Headers de Autenticação

### 1. Seller-Authorization
```http
Seller-Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000
```

**Usado em:**
- POST `/stores/` - Criar loja
- POST `/stores/{id}/products` - Adicionar produto
- GET `/stores/{id}/get-credential` - Obter credential

### 2. Customer-Authorization
```http
Customer-Authorization: Bearer 660e8400-e29b-41d4-a716-446655440001
```

**Usado em:**
- POST `/carts/` - Adicionar ao carrinho
- PUT `/carts/update-amount` - Atualizar quantidade
- DELETE `/carts/{id}` - Remover do carrinho
- POST `/orders/` - Finalizar pedido

### 3. Store-Credential
```http
Store-Credential: a1b2c3d4e5f6
```

**Usado em:** Praticamente todas as requisições (exceto criar seller/loja)

**Propósito:**
- Identifica qual loja está sendo acessada
- Garante isolamento entre lojas (multi-tenancy)
- Previne acesso cruzado de dados

---

## 🛡️ Decoradores de Autenticação

### @seller_required

```python
@seller_required
async def create_store(request: Request, body: StoreSchema):
    # request.current_user contém o Seller autenticado
    seller_id = request.current_user.id
    ...
```

**Validação:**
1. Extrai `Seller-Authorization` do header
2. Remove prefixo `Bearer `
3. Busca `SellerAuth` com `status='valid'` e token correspondente
4. Carrega `Seller` relacionado
5. Injeta em `request.current_user`

**Erros:**
- 403 Forbidden: Token ausente/inválido/invalidado

---

### @customer_required

```python
@customer_required
async def add_to_cart(request: Request, body: CartItemSchema):
    # request.current_user contém o Customer autenticado
    customer_id = request.current_user.id
    ...
```

**Validação:**
1. Extrai `Customer-Authorization` do header
2. Remove prefixo `Bearer `
3. Busca `CustomerAuth` com `status='valid'` e token correspondente
4. Carrega `Customer` relacionado
5. Injeta em `request.current_user`

**Erros:**
- 403 Forbidden: Token ausente/inválido/invalidado

---

### @store_required

```python
@store_required
async def add_product(request: Request, body: ProductSchema):
    # request.current_store contém a Store identificada
    store_id = request.current_store.id
    ...
```

**Validação:**
1. Extrai `Store-Credential` do header
2. Busca `Store` com credential correspondente
3. Injeta em `request.current_store`

**Erros:**
- 403 Forbidden: Credential ausente/inválida

---

## 🔄 Fluxos de Autenticação

### Fluxo 1: Seller

```
┌──────────────────────────────────────────────┐
│ 1. Cadastro                                  │
│    POST /sellers/                            │
│    Body: { name, email, password }           │
│                                              │
│    Response:                                 │
│    {                                         │
│      "seller_id": 1,                         │
│      "access_token": "550e8400-..."          │
│    }                                         │
└──────────────────┬───────────────────────────┘
                   │
                   │ Salvar access_token
                   │
┌──────────────────▼───────────────────────────┐
│ 2. Criar Loja                                │
│    POST /stores/                             │
│    Headers:                                  │
│      Seller-Authorization: Bearer {token}    │
│    Body: { name }                            │
│                                              │
│    Response:                                 │
│    { "id": 1, "name": "Magic Store" }        │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ 3. Obter Credential                          │
│    GET /stores/1/get-credential              │
│    Headers:                                  │
│      Seller-Authorization: Bearer {token}    │
│                                              │
│    Response:                                 │
│    { "credential": "a1b2c3..." }             │
└──────────────────┬───────────────────────────┘
                   │
                   │ Salvar credential
                   │
┌──────────────────▼───────────────────────────┐
│ 4. Adicionar Produtos                        │
│    POST /stores/1/products                   │
│    Headers:                                  │
│      Seller-Authorization: Bearer {token}    │
│      Store-Credential: {credential}          │
│    Body: { name, description, price, ... }   │
└──────────────────────────────────────────────┘
```

### Fluxo 2: Customer

```
┌──────────────────────────────────────────────┐
│ 1. Cadastro                                  │
│    POST /customers/                          │
│    Headers:                                  │
│      Store-Credential: {credential}          │
│    Body: { name, email, password }           │
│                                              │
│    Response:                                 │
│    {                                         │
│      "customer_id": 1,                       │
│      "access_token": "660e8400-..."          │
│    }                                         │
└──────────────────┬───────────────────────────┘
                   │
                   │ Salvar access_token
                   │
┌──────────────────▼───────────────────────────┐
│ 2. Adicionar ao Carrinho                     │
│    POST /carts/                              │
│    Headers:                                  │
│      Customer-Authorization: Bearer {token}  │
│      Store-Credential: {credential}          │
│    Body: { product_id, amount }              │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ 3. Finalizar Pedido                          │
│    POST /orders/                             │
│    Headers:                                  │
│      Customer-Authorization: Bearer {token}  │
│      Store-Credential: {credential}          │
└──────────────────────────────────────────────┘
```

---

## 🔄 Login e Invalidação

### Login (gera novo token e invalida anteriores)

```python
async def generate_credentials(user, model: str):
    access_token = uuid.uuid4()
    
    if model == 'seller':
        # Invalidar tokens anteriores
        await SellerAuth.filter(seller=user).update(status='invalidated')
        
        # Criar novo token
        auth = await SellerAuth.create(
            seller=user,
            access_token=access_token,
            status='valid'
        )
        
    return {
        'access_token': access_token,
        'seller_id': user.id,
        'name': user.name
    }
```

**Comportamento:**
- Cada login gera um novo token
- Tokens anteriores são invalidados
- Apenas 1 token válido por usuário por vez

---

## 🛡️ Isolamento Multi-Tenant

### Como Funciona

Cada requisição valida:
1. **Token de usuário** (Seller ou Customer)
2. **Store Credential** (qual loja está acessando)

### Exemplo de Proteção

```python
@customer_required
@store_required
async def add_to_cart(request: Request, body: CartItemSchema):
    # Buscar produto
    product = await Product.filter(id=body.product_id).first()
    
    # Validar que produto pertence à loja atual
    if product.store_id != request.current_store.id:
        raise HTTPException(403, "Product from different store")
    
    # Criar carrinho vinculado à loja e customer
    cart = await Cart.create(
        store_id=request.current_store.id,  # Loja identificada pelo credential
        customer_id=request.current_user.id, # Customer autenticado
        status='active'
    )
```

### Cenários Protegidos

❌ **Cenário 1: Customer tentando acessar produto de outra loja**
```http
POST /carts/
Headers:
  Customer-Authorization: Bearer {customer_token}
  Store-Credential: {store_A_credential}
Body:
  { "product_id": 999 }  # Produto pertence a Store B

Resultado: 403 Forbidden ou 404 Not Found
```

❌ **Cenário 2: Seller tentando adicionar produto em loja de outro seller**
```python
@router.post("/{store_id}/products")
@seller_required
@store_required
async def add_product(request: Request, store_id: int, body: ProductSchema):
    seller = await request.current_store.seller
    
    # Validar ownership
    if seller.id != request.current_user.id:
        raise HTTPException(403, "Forbidden")
    
    # Continuar...
```

---

## 🔧 Implementação dos Decoradores

### Código Completo

```python
# src/authentication.py

from functools import wraps
from fastapi import HTTPException, Request
from src.models import CustomerAuth, SellerAuth, Store

async def valid_access_token(access_token: str, model):
    if not access_token:
        raise HTTPException(403, "Unauthorized")
    
    # Remover prefixo "Bearer "
    access_token = access_token.split(' ')[1]
    
    # Buscar token válido
    user_auth = await model.filter(
        status='valid',
        access_token=access_token
    ).first()
    
    if not user_auth:
        raise HTTPException(403, "Unauthorized")
    
    # Retornar usuário
    if model == CustomerAuth:
        return await user_auth.customer
    else:
        return await user_auth.seller


def customer_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        access_token = request.headers.get("Customer-Authorization", False)
        user = await valid_access_token(access_token, CustomerAuth)
        request.current_user = user
        return await func(*args, **kwargs)
    return wrapper


def seller_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        access_token = request.headers.get("Seller-Authorization", False)
        user = await valid_access_token(access_token, SellerAuth)
        request.current_user = user
        return await func(*args, **kwargs)
    return wrapper


def store_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        credential = request.headers.get("Store-Credential", False)
        
        if not credential:
            raise HTTPException(403, "Store credential is invalid")
        
        store = await Store.get(credential=credential)
        if not store:
            raise HTTPException(403, "Store credential is invalid")
        
        request.current_store = store
        return await func(*args, **kwargs)
    return wrapper
```

---

## 🧪 Testando Autenticação

### Teste 1: Sem Token

```python
async def test_should_not_add_to_cart_without_auth(client):
    response = await client.post("/carts/", json={"product_id": 1, "amount": 1})
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized"
```

### Teste 2: Token Inválido

```python
async def test_should_not_add_to_cart_with_invalid_token(client):
    response = await client.post(
        "/carts/",
        headers={"Customer-Authorization": "Bearer invalid-token"},
        json={"product_id": 1, "amount": 1}
    )
    assert response.status_code == 403
```

### Teste 3: Sem Store Credential

```python
async def test_should_not_create_customer_without_store(client):
    response = await client.post(
        "/customers/",
        json={"name": "Test", "email": "test@test.com", "password": "123"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Store credential is invalid"
```

---

## 🔐 Segurança Adicional

### 1. Hashear Senhas (Recomendado)

```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Ao criar usuário
hashed = hash_password(body.password)
seller = await Seller.create(
    name=body.name,
    email=body.email,
    password=hashed
)

# Ao autenticar
hashed_input = hash_password(body.password)
seller = await Seller.filter(email=body.email, password=hashed_input).first()
```

**Melhor ainda: usar bcrypt**
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 2. Expiração de Tokens

```python
class SellerAuth(Model):
    # ...
    expires_at = fields.DatetimeField()

# Ao criar token
expires_at = datetime.now() + timedelta(days=30)

# Ao validar
if user_auth.expires_at < datetime.now():
    raise HTTPException(403, "Token expired")
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/sellers/auth")
@limiter.limit("5/minute")  # Máximo 5 tentativas por minuto
async def authenticate(request: Request, body: SellerAuthSchema):
    ...
```

### 4. HTTPS Only

```python
# Produção: forçar HTTPS
if not request.url.scheme == "https":
    raise HTTPException(403, "HTTPS required")
```

