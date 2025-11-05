# API Endpoints - Documentação Completa

## 🔐 Headers de Autenticação

### Store-Credential
**Obrigatório em quase todas as requisições**
```
Store-Credential: {uuid}
```
- Identifica qual loja está sendo acessada
- Obtido após criar uma store
- Garante isolamento multi-tenant

### Seller-Authorization
**Para operações de vendedor**
```
Seller-Authorization: Bearer {token}
```
- Token obtido no cadastro ou login
- Necessário para criar lojas e gerenciar produtos

### Customer-Authorization
**Para operações de cliente**
```
Customer-Authorization: Bearer {token}
```
- Token obtido no cadastro ou login
- Necessário para carrinho e pedidos

---

## 👤 Sellers

### POST `/sellers/` - Criar Vendedor
Cria um novo vendedor no sistema.

**Headers:** Nenhum

**Body:**
```json
{
  "name": "João Silva",
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Response:** 200 OK
```json
{
  "seller_id": 1,
  "name": "João Silva",
  "access_token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errors:**
- 400: Email já cadastrado

---

### POST `/sellers/auth` - Login Vendedor
Autentica um vendedor existente.

**Headers:** Nenhum

**Body:**
```json
{
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Response:** 200 OK
```json
{
  "seller_id": 1,
  "name": "João Silva",
  "access_token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errors:**
- 401: Credenciais inválidas

---

## 🏪 Stores

### POST `/stores/` - Criar Loja
Cria uma nova loja para o vendedor autenticado.

**Headers:**
```
Seller-Authorization: Bearer {token}
```

**Body:**
```json
{
  "name": "Magic Store Orlando"
}
```

**Response:** 200 OK
```json
{
  "id": 1,
  "name": "Magic Store Orlando"
}
```

**Errors:**
- 403: Não autenticado como seller

**Nota:** Após criar a loja, use `GET /stores/{store_id}/get-credential` para obter a credential.

---

### GET `/stores/{store_id}/get-credential` - Obter Credential
Retorna a credential da loja (necessária para todas as operações).

**Headers:**
```
Seller-Authorization: Bearer {token}
```

**Response:** 200 OK
```json
{
  "credential": "a1b2c3d4e5f6"
}
```

**Errors:**
- 403: Não autenticado como seller
- 404: Loja não encontrada

---

### POST `/stores/{store_id}/products` - Adicionar Produto
Adiciona um produto à loja.

**Headers:**
```
Seller-Authorization: Bearer {token}
Store-Credential: {credential}
```

**Body:**
```json
{
  "name": "Magic Kingdom - 1 Day Ticket",
  "description": "Ingresso de 1 dia para Magic Kingdom",
  "price": 12948,
  "external_id": "987cedca-559e-4b71-a00b-932c5208b846"
}
```

**Response:** 200 OK
```json
{
  "id": 1,
  "name": "Magic Kingdom - 1 Day Ticket",
  "description": "Ingresso de 1 dia para Magic Kingdom",
  "price": 12948,
  "external_id": "987cedca-559e-4b71-a00b-932c5208b846",
  "status": "active",
  "created_at": "2024-11-05T10:30:00Z"
}
```

**Errors:**
- 403: Não autenticado como seller ou loja inválida
- 403: Seller não é dono da loja

**Notas:**
- `price`: Valor em centavos (12948 = R$ 129,48)
- `external_id`: Código do produto na Maria API

---

## 👥 Customers

### POST `/customers/` - Criar Cliente
Cria um novo cliente em uma loja.

**Headers:**
```
Store-Credential: {credential}
```

**Body:**
```json
{
  "name": "Maria Santos",
  "email": "maria@email.com",
  "password": "senha456"
}
```

**Response:** 200 OK
```json
{
  "customer_id": 1,
  "name": "Maria Santos",
  "access_token": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Errors:**
- 403: Store credential inválida
- 400: Email já cadastrado na loja

**Nota:** Email deve ser único por loja (mesmo email pode existir em lojas diferentes).

---

### POST `/customers/auth` - Login Cliente
Autentica um cliente em uma loja.

**Headers:**
```
Store-Credential: {credential}
```

**Body:**
```json
{
  "email": "maria@email.com",
  "password": "senha456"
}
```

**Response:** 200 OK
```json
{
  "customer_id": 1,
  "name": "Maria Santos",
  "access_token": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Errors:**
- 403: Store credential inválida
- 401: Credenciais inválidas

---

## 🛒 Carts

### POST `/carts/` - Adicionar Item ao Carrinho
Adiciona um produto ao carrinho do cliente. Se não existir carrinho ativo, cria um novo.

**Headers:**
```
Customer-Authorization: Bearer {token}
Store-Credential: {credential}
```

**Body:**
```json
{
  "product_id": 1,
  "amount": 2
}
```

**Response:** 200 OK
```json
{
  "cart_empty": false,
  "items": [
    {
      "product_id": 1,
      "product_name": "Magic Kingdom - 1 Day Ticket",
      "price": 12948,
      "amount": 2
    }
  ]
}
```

**Errors:**
- 403: Não autenticado como customer ou store inválida
- 404: Produto não encontrado
- 404: Produto inativo

---

### PUT `/carts/update-amount` - Atualizar Quantidade
Atualiza a quantidade de um item no carrinho.

**Headers:**
```
Customer-Authorization: Bearer {token}
Store-Credential: {credential}
```

**Body:**
```json
{
  "product_id": 1,
  "amount": 3
}
```

**Response:** 200 OK
```json
{
  "cart_empty": false,
  "items": [
    {
      "product_id": 1,
      "product_name": "Magic Kingdom - 1 Day Ticket",
      "price": 12948,
      "amount": 3
    }
  ]
}
```

**Errors:**
- 403: Não autenticado
- 404: Carrinho ou item não encontrado

**Notas:**
- Se `amount` for 0 ou negativo, será definido como 1

---

### DELETE `/carts/{product_id}` - Remover Item
Remove um item do carrinho. Se o carrinho ficar vazio, é deletado automaticamente.

**Headers:**
```
Customer-Authorization: Bearer {token}
Store-Credential: {credential}
```

**Response:** 200 OK
```json
{
  "cart_empty": true,
  "items": []
}
```

**Errors:**
- 403: Não autenticado
- 404: Carrinho ou item não encontrado

---

## 📦 Orders

### POST `/orders/` - Criar Pedido
Finaliza o carrinho criando um pedido. O carrinho é convertido em pedido.

**Headers:**
```
Customer-Authorization: Bearer {token}
Store-Credential: {credential}
```

**Body:** Nenhum (usa o carrinho ativo)

**Response:** 200 OK
```json
{
  "status": "created",
  "code": "a1b2c3d4e5f67890",
  "items": [
    {
      "product_id": 1,
      "product_name": "Magic Kingdom - 1 Day Ticket",
      "price": 12948,
      "amount": 2
    }
  ],
  "total_price": 25896,
  "created_at": "2024-11-05T10:30:00.000Z"
}
```

**Errors:**
- 403: Não autenticado
- 404: Carrinho vazio
- 404: Produto não encontrado ou inativo

**Notas:**
- Preços são salvos como snapshot no momento da compra
- Status inicial: `created`
- Carrinho é esvaziado após criar o pedido

---

## 📊 Fluxos Completos

### Fluxo 1: Seller Criando Loja
```
1. POST /sellers/           → Criar conta
2. POST /stores/            → Criar loja
3. GET /stores/1/get-credential → Obter credential
4. POST /stores/1/products  → Adicionar produtos
```

### Fluxo 2: Customer Comprando
```
1. POST /customers/         → Criar conta (com Store-Credential)
2. POST /carts/             → Adicionar produto ao carrinho
3. PUT /carts/update-amount → Ajustar quantidade (opcional)
4. POST /orders/            → Finalizar compra
```

### Fluxo 3: Integração com Maria API
```
Frontend:
1. GET Maria API /parks                    → Listar parques
2. GET Maria API /parks/{id}/products      → Listar produtos
3. Cliente escolhe produto

Backend:
4. POST /stores/1/products                 → Seller cria produto com external_id
   
Frontend (Cliente):
5. POST /carts/                            → Cliente adiciona ao carrinho
6. POST /orders/                           → Cliente finaliza compra
```

---

## 🔍 Códigos de Status HTTP

| Código | Significado                  | Quando ocorre                          |
|--------|------------------------------|----------------------------------------|
| 200    | OK                           | Requisição bem-sucedida                |
| 400    | Bad Request                  | Dados inválidos, email duplicado       |
| 401    | Unauthorized                 | Credenciais de login inválidas         |
| 403    | Forbidden                    | Token inválido, sem permissão          |
| 404    | Not Found                    | Recurso não encontrado                 |
| 500    | Internal Server Error        | Erro no servidor                       |

---

## 💡 Dicas de Implementação Frontend

### 1. Gerenciamento de Estado
```javascript
// Guardar tokens e credentials
localStorage.setItem('seller_token', response.access_token);
localStorage.setItem('customer_token', response.access_token);
localStorage.setItem('store_credential', response.credential);
```

### 2. Interceptor HTTP (Axios/Fetch)
```javascript
// Adicionar headers automaticamente
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

api.interceptors.request.use(config => {
  const customerToken = localStorage.getItem('customer_token');
  const storeCredential = localStorage.getItem('store_credential');
  
  if (customerToken) {
    config.headers['Customer-Authorization'] = `Bearer ${customerToken}`;
  }
  if (storeCredential) {
    config.headers['Store-Credential'] = storeCredential;
  }
  
  return config;
});
```

### 3. Formatação de Preços
```javascript
// Converter centavos para real
function formatPrice(cents) {
  return (cents / 100).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  });
}

// formatPrice(12948) → "R$ 129,48"
```

### 4. Tratamento de Erros
```javascript
try {
  const response = await api.post('/carts/', {
    product_id: 1,
    amount: 2
  });
} catch (error) {
  if (error.response?.status === 403) {
    // Redirecionar para login
    router.push('/login');
  } else if (error.response?.status === 404) {
    // Produto não encontrado
    showError('Produto não disponível');
  }
}
```

