# 📚 Magic Marketplace - Documentação Completa

Bem-vindo à documentação do **Magic Marketplace**, um sistema de marketplace multi-tenant especializado em ingressos para parques temáticos.

---

## 🗂️ Índice de Documentação

### 1. [OVERVIEW.md](./OVERVIEW.md) - Visão Geral do Projeto
**Comece aqui se você é novo no projeto!**

- Descrição e objetivo do sistema
- Arquitetura geral da aplicação
- Conceitos fundamentais (multi-tenancy, autenticação, lazy loading)
- Principais entidades e fluxos
- Tecnologias utilizadas
- Como executar o projeto

### 2. [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md) - Estrutura do Banco de Dados
**Para entender o modelo de dados**

- Diagrama ER completo
- Detalhes de cada tabela
- Relacionamentos entre entidades
- Índices recomendados
- Consultas SQL comuns
- Métricas e análises

### 3. [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Documentação da API
**Para integrar com o backend**

- Headers de autenticação
- Todos os endpoints documentados
- Exemplos de request/response
- Códigos de erro
- Fluxos completos
- Dicas de implementação frontend

### 4. [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md) - Integração Maria API
**Para entender a integração externa**

- O que é Maria API
- Endpoints disponíveis
- Modelos Pydantic (DTOs)
- Diferenças entre lista e detalhe
- Fluxo de integração recomendado
- Estratégias de cache
- Troubleshooting

### 5. [PRODUCT_FLOW.md](./PRODUCT_FLOW.md) - Fluxo de Produtos (Lazy Loading)
**⭐ Conceito FUNDAMENTAL do sistema**

- Problema e solução (lazy loading)
- Fluxo completo detalhado
- Vantagens da abordagem
- Implementação recomendada
- Considerações UI/UX
- Monitoramento e métricas

### 6. [AUTHENTICATION.md](./AUTHENTICATION.md) - Sistema de Autenticação
**Para entender segurança e permissões**

- Tipos de usuários (Seller, Customer)
- Estrutura de tokens
- Headers de autenticação
- Decoradores (@seller_required, @customer_required)
- Fluxos de autenticação
- Isolamento multi-tenant
- Recomendações de segurança

### 7. [TESTING.md](./TESTING.md) - Estratégia de Testes
**Para escrever e executar testes**

- Estrutura de testes
- Fixtures compartilhadas
- Testes ordenados
- Exemplos práticos
- Coverage
- Debugging
- Dicas de performance

---

## 🎯 Guias por Persona

### 👨‍💻 Desenvolvedor Frontend

**Leia nesta ordem:**

1. [OVERVIEW.md](./OVERVIEW.md) - Entender o sistema
2. [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Integrar com backend
3. [PRODUCT_FLOW.md](./PRODUCT_FLOW.md) - **CRÍTICO**: Entender fluxo de produtos
4. [AUTHENTICATION.md](./AUTHENTICATION.md) - Implementar login/auth
5. [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md) - Consumir catálogo

**Principais conceitos:**

```javascript
// 1. Buscar produtos da Maria API (vitrine)
const products = await mariaApi.get('/parks/{id}/products');

// 2. Cliente adiciona ao carrinho
// Backend cria o produto no banco neste momento
await backendApi.post('/carts/', {
  maria_product_code: product.code,
  amount: 1
});

// 3. Headers necessários
headers: {
  'Customer-Authorization': 'Bearer {token}',
  'Store-Credential': '{credential}'
}
```

---

### 👨‍💻 Desenvolvedor Backend

**Leia nesta ordem:**

1. [OVERVIEW.md](./OVERVIEW.md) - Visão geral
2. [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md) - Modelo de dados
3. [PRODUCT_FLOW.md](./PRODUCT_FLOW.md) - **CRÍTICO**: Lazy loading strategy
4. [AUTHENTICATION.md](./AUTHENTICATION.md) - Sistema de auth
5. [TESTING.md](./TESTING.md) - Escrever testes
6. [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md) - Integração externa

**Principais conceitos:**

```python
# Decoradores de autenticação
@seller_required      # request.current_user = Seller
@customer_required    # request.current_user = Customer
@store_required       # request.current_store = Store

# Lazy loading de produtos
# Produto é criado apenas quando adicionado ao carrinho
product = await Product.filter(external_id=maria_code).first()
if not product:
    # Buscar da Maria API e criar
    product = await Product.create(...)
```

---

### 🎨 Designer/Product Manager

**Leia nesta ordem:**

1. [OVERVIEW.md](./OVERVIEW.md) - Entender o negócio
2. [PRODUCT_FLOW.md](./PRODUCT_FLOW.md) - **CRÍTICO**: Fluxo de produtos
3. [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Ver fluxos completos

**Principais conceitos:**

- **Vitrine**: Produtos vêm da Maria API (sempre atualizados)
- **Carrinho**: Produtos são salvos no banco (preço garantido)
- **Multi-tenancy**: Cada loja é isolada das outras
- **Dois tipos de usuários**: Seller (vende) e Customer (compra)

---

### 🔧 DevOps/SRE

**Leia nesta ordem:**

1. [OVERVIEW.md](./OVERVIEW.md) - Arquitetura
2. [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md) - Índices e queries
3. [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md) - Dependência externa
4. [TESTING.md](./TESTING.md) - CI/CD

**Principais conceitos:**

```bash
# Variáveis de ambiente necessárias
DATABASE_URL=sqlite://db.sqlite3
MARIA_API_ENDPOINT=http://localhost:8001

# Comandos principais
poetry install          # Instalar dependências
aerich upgrade          # Rodar migrações
fastapi dev src/application.py  # Iniciar app
pytest                  # Executar testes
```

**Monitoramento:**
- Rate limiting da Maria API
- Performance de queries (índices)
- Taxa de conversão (carrinho → pedido)

---

## 🚀 Quick Start

### 1. Instalar Dependências

```bash
cd magic-marketplace
poetry install
```

### 2. Configurar Ambiente

```bash
# .env
DATABASE_URL=sqlite://db.sqlite3
MARIA_API_ENDPOINT=http://localhost:8001
```

### 3. Rodar Migrações

```bash
poetry run aerich upgrade
```

### 4. Executar Aplicação

```bash
poetry run fastapi dev src/application.py
```

### 5. Executar Testes

```bash
poetry run pytest -v
```

---

## 💡 Conceitos Chave

### 🔑 Multi-Tenancy

Cada **Store** é um tenant isolado:
- Sellers criam lojas
- Customers pertencem a uma loja
- Products pertencem a uma loja
- Isolamento garantido por `Store-Credential`

### 🔐 Dupla Autenticação

Duas camadas de segurança:
1. **Token de usuário**: Identifica Seller ou Customer
2. **Store Credential**: Identifica qual loja está acessando

### 📦 Lazy Loading de Produtos

**Conceito FUNDAMENTAL do sistema:**

```
Vitrine (Maria API) → Cliente adiciona ao carrinho → Produto criado no banco
```

**Não sincronizamos catálogo completo!**

Vantagens:
- ✅ Banco limpo (apenas produtos com interesse)
- ✅ Preços sempre atualizados
- ✅ Métricas significativas
- ✅ Sem sincronização complexa

### 🔄 Fluxo Completo

```
1. Seller cria conta e loja
2. Seller obtém Store Credential
3. Customer cria conta na loja (usando Credential)
4. Frontend busca produtos da Maria API (vitrine)
5. Customer adiciona produto ao carrinho
   → Backend cria produto no banco (lazy loading)
6. Customer finaliza pedido
   → Preços salvos como snapshot
```

---

## 📊 Arquitetura em Camadas

```
┌─────────────────────────────────────┐
│         Frontend (React/Vue)        │
│  - Consome Maria API (catálogo)     │
│  - Consome Backend API (transações) │
└──────────────┬──────────────────────┘
               │
        HTTP Requests
               │
┌──────────────▼──────────────────────┐
│      FastAPI Backend (Python)       │
│  - Routes (endpoints)               │
│  - Authentication (decorators)      │
│  - Business Logic (utils)           │
│  - Tortoise ORM (models)            │
└──────────────┬──────────────────────┘
               │
          ┌────┴────┐
          │         │
          ▼         ▼
┌─────────────┐  ┌──────────────┐
│  Database   │  │  Maria API   │
│  (SQLite)   │  │  (External)  │
│             │  │              │
│ - Sellers   │  │ - Parks      │
│ - Stores    │  │ - Products   │
│ - Customers │  │ - Prices     │
│ - Products* │  └──────────────┘
│ - Carts     │   * Lazy loaded
│ - Orders    │     from here
└─────────────┘
```

---

## 🔍 Como Navegar na Documentação

### Buscar por Tópico

**Autenticação:**
- Headers: [API_ENDPOINTS.md](./API_ENDPOINTS.md)
- Decoradores: [AUTHENTICATION.md](./AUTHENTICATION.md)
- Testes: [TESTING.md](./TESTING.md)

**Produtos:**
- Lazy Loading: [PRODUCT_FLOW.md](./PRODUCT_FLOW.md)
- API Endpoints: [API_ENDPOINTS.md](./API_ENDPOINTS.md)
- Modelo de dados: [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md)

**Maria API:**
- Integração: [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md)
- DTOs: [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md)
- Testes: [TESTING.md](./TESTING.md)

**Banco de Dados:**
- Estrutura: [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md)
- Queries: [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md)
- Índices: [DATABASE_STRUCTURE.md](./DATABASE_STRUCTURE.md)

---

## 📝 Convenções de Código

### Nomenclatura

```python
# Classes: PascalCase
class MariaApi:
    ...

# Funções/métodos: snake_case
def get_cart_items():
    ...

# Constantes: UPPER_SNAKE_CASE
ORDER_STATUS = (...)

# Variáveis: snake_case
access_token = "..."
```

### Estrutura de Arquivos

```python
# Routes sempre retornam dicts ou models
@router.post("/")
async def create_seller(body: SellerSchema):
    return {"seller_id": 1, "name": "..."}

# Utils para lógica reutilizável
async def get_cart_items(store_id, customer_id):
    ...

# Models usam Tortoise ORM
class Seller(Model):
    id = fields.IntField(primary_key=True)
    ...
```

---

## 🆘 Problemas Comuns

### Maria API não está acessível
```bash
# Verificar se está rodando
curl http://localhost:8001/parks/

# Iniciar Maria API
cd mariaAPI
poetry run uvicorn main:app --reload --port 8001
```

### Testes falhando
```bash
# Limpar banco de dados
rm db.sqlite3*

# Rodar migrações
poetry run aerich upgrade

# Executar testes
poetry run pytest -v
```

### Erro de validação Pydantic
- Verificar se DTOs correspondem à resposta da API
- Ver [MARIA_API_INTEGRATION.md](./MARIA_API_INTEGRATION.md)

---

## 🤝 Contribuindo

1. Leia [OVERVIEW.md](./OVERVIEW.md) e [PRODUCT_FLOW.md](./PRODUCT_FLOW.md)
2. Crie branch a partir de `main`
3. Escreva testes ([TESTING.md](./TESTING.md))
4. Garanta que todos os testes passam
5. Atualize documentação se necessário
6. Abra Pull Request

---

## 📞 Contato e Suporte

- **Documentação**: Esta pasta `.cursor/`
- **Código**: `magic-marketplace/src/`
- **Testes**: `magic-marketplace/tests/`

---

## 🎓 Recursos Adicionais

### Tecnologias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tortoise ORM Documentation](https://tortoise.github.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Conceitos

- Multi-tenancy Architecture
- Token-based Authentication
- Lazy Loading Pattern
- Repository Pattern

---

**Última atualização:** 2024-11-05

**Versão:** 1.0.0

---

> 💡 **Dica**: Sempre comece com [OVERVIEW.md](./OVERVIEW.md) e depois navegue para documentos específicos conforme sua necessidade!

