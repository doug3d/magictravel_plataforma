# Estrutura do Banco de Dados

## 📊 Diagrama ER (Entity-Relationship)

```
┌─────────────┐
│   Seller    │
│─────────────│
│ id (PK)     │
│ name        │
│ email       │──────┐
│ password    │      │
│ created_at  │      │
└─────────────┘      │
       │             │
       │ 1:N         │ 1:N
       │             │
       ▼             ▼
┌─────────────┐   ┌──────────────┐
│ SellerAuth  │   │    Store     │
│─────────────│   │──────────────│
│ id (PK)     │   │ id (PK)      │
│ seller_id   │   │ seller_id    │───────┐
│ access_token│   │ name         │       │
│ status      │   │ credential   │       │
│ created_at  │   │ created_at   │       │
└─────────────┘   └──────────────┘       │
                         │                │
                         │ 1:N            │
                         ▼                │
                  ┌─────────────┐         │
                  │  Customer   │         │
                  │─────────────│         │
                  │ id (PK)     │         │
                  │ store_id    │         │
                  │ name        │         │
                  │ email       │         │
                  │ password    │         │
                  │ created_at  │         │
                  └─────────────┘         │
                         │                │
                         │ 1:N            │
                         ▼                │
                  ┌──────────────┐        │
                  │ CustomerAuth │        │
                  │──────────────│        │
                  │ id (PK)      │        │
                  │ customer_id  │        │
                  │ access_token │        │
                  │ status       │        │
                  │ created_at   │        │
                  └──────────────┘        │
                         │                │
                         │ 1:N            │
                         ▼                │
                  ┌─────────────┐         │
                  │    Cart     │         │
                  │─────────────│         │
                  │ id (PK)     │         │
                  │ store_id    │◄────────┘
                  │ customer_id │
                  │ status      │
                  │ created_at  │
                  └─────────────┘
                         │
                         │ 1:N
                         ▼
                  ┌─────────────┐         ┌─────────────┐
                  │  CartItem   │         │   Product   │
                  │─────────────│         │─────────────│
                  │ id (PK)     │    ┌───►│ id (PK)     │
                  │ cart_id     │    │    │ store_id    │
                  │ product_id  │────┘    │ name        │
                  │ amount      │         │ description │
                  │ created_at  │         │ price       │
                  └─────────────┘         │ external_id │◄── Maria API code
                                          │ status      │
                  ┌─────────────┐         │ created_at  │
                  │    Order    │         └─────────────┘
                  │─────────────│                │
                  │ id (PK)     │                │
                  │ store_id    │                │
                  │ customer_id │                │
                  │ code        │                │
                  │ status      │                │
                  │ created_at  │                │
                  └─────────────┘                │
                         │                       │
                         │ 1:N                   │
                         ▼                       │
                  ┌─────────────┐                │
                  │  OrderItem  │                │
                  │─────────────│                │
                  │ id (PK)     │                │
                  │ order_id    │                │
                  │ product_id  │────────────────┘
                  │ price       │ (snapshot)
                  │ amount      │
                  └─────────────┘
```

## 📋 Tabelas Detalhadas

### Seller
**Vendedor que gerencia lojas**

| Campo      | Tipo     | Descrição                    |
|------------|----------|------------------------------|
| id         | Integer  | PK, auto-increment           |
| name       | String   | Nome do vendedor             |
| email      | String   | Email único do vendedor      |
| password   | String   | Senha (deve ser hasheada)    |
| created_at | DateTime | Data de criação              |

**Relacionamentos:**
- 1:N com `Store` (um seller pode ter várias lojas)
- 1:N com `SellerAuth` (histórico de tokens)

---

### SellerAuth
**Tokens de autenticação do vendedor**

| Campo        | Tipo     | Descrição                        |
|--------------|----------|----------------------------------|
| id           | Integer  | PK, auto-increment               |
| seller_id    | Integer  | FK → Seller                      |
| access_token | String   | Token UUID                       |
| status       | String   | 'valid' ou 'invalidated'         |
| created_at   | DateTime | Data de criação                  |

**Notas:**
- Quando um novo token é criado, os anteriores são invalidados
- Permite logout de sessões anteriores

---

### Store
**Loja (tenant principal do sistema)**

| Campo      | Tipo     | Descrição                         |
|------------|----------|-----------------------------------|
| id         | Integer  | PK, auto-increment                |
| seller_id  | Integer  | FK → Seller (dono da loja)        |
| name       | String   | Nome da loja                      |
| credential | String   | UUID único (identifica a loja)    |
| created_at | DateTime | Data de criação                   |

**Relacionamentos:**
- N:1 com `Seller`
- 1:N com `Customer`
- 1:N com `Product`
- 1:N com `Cart`
- 1:N com `Order`

**Notas:**
- A `credential` é usada no header `Store-Credential` de todas as requisições
- Garante isolamento entre lojas (multi-tenancy)

---

### Customer
**Cliente que compra produtos**

| Campo      | Tipo     | Descrição                     |
|------------|----------|-------------------------------|
| id         | Integer  | PK, auto-increment            |
| store_id   | Integer  | FK → Store                    |
| name       | String   | Nome do cliente               |
| email      | String   | Email único (por loja)        |
| password   | String   | Senha (deve ser hasheada)     |
| created_at | DateTime | Data de criação               |

**Relacionamentos:**
- N:1 com `Store`
- 1:N com `CustomerAuth`
- 1:N com `Cart`
- 1:N com `Order`

**Notas:**
- Email é único dentro da mesma loja
- Customer pertence a uma única loja

---

### CustomerAuth
**Tokens de autenticação do cliente**

| Campo        | Tipo     | Descrição                        |
|--------------|----------|----------------------------------|
| id           | Integer  | PK, auto-increment               |
| customer_id  | Integer  | FK → Customer                    |
| access_token | String   | Token UUID                       |
| status       | String   | 'valid' ou 'invalidated'         |
| created_at   | DateTime | Data de criação                  |

---

### Product
**Produto vendido na loja**

| Campo       | Tipo     | Descrição                              |
|-------------|----------|----------------------------------------|
| id          | Integer  | PK, auto-increment                     |
| store_id    | Integer  | FK → Store                             |
| name        | String   | Nome do produto                        |
| description | Text     | Descrição detalhada                    |
| price       | Integer  | Preço em centavos                      |
| external_id | Text     | Código do produto na Maria API         |
| status      | String   | 'active' ou 'inactive'                 |
| created_at  | DateTime | Data de criação                        |

**Relacionamentos:**
- N:1 com `Store`
- 1:N com `CartItem`
- 1:N com `OrderItem`

**Notas Importantes:**
- ⚠️ **Lazy Loading**: Produto só é criado quando adicionado ao carrinho
- `external_id`: Referência para Maria API (permite buscar detalhes atualizados)
- `price`: Snapshot do preço no momento da criação
- `status`: Permite desativar produtos

---

### Cart
**Carrinho de compras ativo**

| Campo       | Tipo     | Descrição                    |
|-------------|----------|------------------------------|
| id          | Integer  | PK, auto-increment           |
| store_id    | Integer  | FK → Store                   |
| customer_id | Integer  | FK → Customer                |
| status      | String   | 'active' ou 'abandoned'      |
| created_at  | DateTime | Data de criação              |

**Relacionamentos:**
- N:1 com `Store`
- N:1 com `Customer`
- 1:N com `CartItem`

**Notas:**
- Um customer pode ter apenas 1 carrinho ativo por loja
- Carrinhos vazios são deletados automaticamente

---

### CartItem
**Item dentro do carrinho**

| Campo      | Tipo     | Descrição                    |
|------------|----------|------------------------------|
| id         | Integer  | PK, auto-increment           |
| cart_id    | Integer  | FK → Cart                    |
| product_id | Integer  | FK → Product                 |
| amount     | Integer  | Quantidade (default: 1)      |
| created_at | DateTime | Data de criação              |

**Relacionamentos:**
- N:1 com `Cart`
- N:1 com `Product`

---

### Order
**Pedido finalizado**

| Campo       | Tipo     | Descrição                        |
|-------------|----------|----------------------------------|
| id          | Integer  | PK, auto-increment               |
| store_id    | Integer  | FK → Store                       |
| customer_id | Integer  | FK → Customer                    |
| code        | String   | UUID (código do pedido)          |
| status      | String   | Status do pedido (ver abaixo)    |
| created_at  | DateTime | Data de criação                  |

**Status possíveis:**
- `created`: Criado
- `waiting_payment`: Aguardando Pagamento
- `paid`: Pago
- `delivered`: Entregue
- `cancelled`: Cancelado

**Relacionamentos:**
- N:1 com `Store`
- N:1 com `Customer`
- 1:N com `OrderItem`

---

### OrderItem
**Item dentro do pedido (snapshot)**

| Campo      | Tipo     | Descrição                       |
|------------|----------|---------------------------------|
| id         | Integer  | PK, auto-increment              |
| order_id   | Integer  | FK → Order                      |
| product_id | Integer  | FK → Product                    |
| price      | Integer  | Preço no momento da compra      |
| amount     | Integer  | Quantidade                      |

**Relacionamentos:**
- N:1 com `Order`
- N:1 com `Product`

**Notas:**
- `price`: Snapshot do preço no momento da compra
- Importante para histórico (produto pode mudar de preço depois)

## 🔍 Índices Importantes

Recomendações de índices para performance:

```sql
-- Store
CREATE INDEX idx_store_credential ON store(credential);
CREATE INDEX idx_store_seller ON store(seller_id);

-- Customer
CREATE INDEX idx_customer_email_store ON customer(email, store_id);
CREATE INDEX idx_customer_store ON customer(store_id);

-- CustomerAuth / SellerAuth
CREATE INDEX idx_customer_auth_token ON customerauth(access_token, status);
CREATE INDEX idx_seller_auth_token ON sellerauth(access_token, status);

-- Product
CREATE INDEX idx_product_store_status ON product(store_id, status);
CREATE INDEX idx_product_external_id ON product(external_id);

-- Cart
CREATE INDEX idx_cart_customer_store ON cart(customer_id, store_id, status);

-- Order
CREATE INDEX idx_order_customer_store ON order(customer_id, store_id);
CREATE INDEX idx_order_code ON order(code);
```

## 📈 Consultas Comuns

### Buscar carrinho ativo do cliente
```sql
SELECT * FROM cart 
WHERE customer_id = ? 
  AND store_id = ? 
  AND status = 'active'
LIMIT 1;
```

### Produtos mais vendidos de uma loja
```sql
SELECT 
    p.id,
    p.name,
    SUM(oi.amount) as total_sold
FROM product p
JOIN orderitem oi ON oi.product_id = p.id
JOIN order o ON o.id = oi.order_id
WHERE o.store_id = ?
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 10;
```

### Taxa de conversão (carrinho → pedido)
```sql
-- Produtos que foram ao carrinho
SELECT COUNT(DISTINCT product_id) as in_cart
FROM cartitem ci
JOIN cart c ON c.id = ci.cart_id
WHERE c.store_id = ?;

-- Produtos que foram vendidos
SELECT COUNT(DISTINCT product_id) as sold
FROM orderitem oi
JOIN order o ON o.id = oi.order_id
WHERE o.store_id = ?;
```

