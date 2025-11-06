# 🌱 Seed do Banco de Dados

## 📋 O que é?

O sistema de seed cria automaticamente dados iniciais no banco de dados para facilitar o desenvolvimento:

1. **Seller Admin**: Usuário admin padrão
2. **Store Padrão**: Loja "Magic Marketplace" vinculada ao admin

---

## 🚀 Execução Automática

O seed é executado **automaticamente** toda vez que a aplicação FastAPI inicia (desenvolvimento ou produção).

### Comportamento

- ✅ **Verifica se já existe**: Não cria duplicados
- ✅ **Idempotente**: Pode ser executado múltiplas vezes
- ✅ **Não afeta testes**: Testes usam banco em memória sem seed

### Logs no Startup

```bash
poetry run fastapi dev src/application.py
```

Output esperado:
```
✓ Seller admin criado (ID: 1)
  Email: admin@magic.com
  Senha: admin
  Token: 96a3fb6e-b30a-452b-9f8c-a54d16312d7b

✓ Loja 'Magic Marketplace' criada (ID: 1)
  Credential: 89c6579682c5435ba08d2905817d1bce

==================================================
🚀 Banco de dados inicializado com sucesso!
==================================================

📝 Credenciais para desenvolvimento:

Seller Admin:
  Email: admin@magic.com
  Senha: admin

Store:
  Nome: Magic Marketplace
  Credential: 89c6579682c5435ba08d2905817d1bce

==================================================
```

---

## 🔧 Execução Manual

Você pode executar o seed manualmente com o script:

```bash
poetry run python scripts/seed_db.py
```

**Quando usar:**
- Resetar dados iniciais
- Recriar seller/loja após limpar banco
- Testar o seed isoladamente

---

## 👤 Credenciais Padrão

### Seller Admin

```
Email: admin@magic.com
Senha: admin
```

**Endpoints:**
```bash
# Login
POST /sellers/auth
{
  "email": "admin@magic.com",
  "password": "admin"
}

# Retorna access_token para usar como Seller-Authorization
```

### Store Padrão

```
Nome: Magic Marketplace
Credential: {gerado automaticamente}
```

**Como obter o credential:**
```bash
# Após fazer login como seller admin
GET /stores/1/get-credential
Headers:
  Seller-Authorization: Bearer {access_token}

# Retorna
{
  "credential": "89c6579682c5435ba08d2905817d1bce"
}
```

---

## 🧪 Uso no Desenvolvimento Frontend

### 1. Focar no Fluxo do Customer

Com o seller admin e loja já criados, você pode pular diretamente para o fluxo do customer:

```javascript
// 1. Obter Store Credential do backend ou usar o exibido no console
const STORE_CREDENTIAL = "89c6579682c5435ba08d2905817d1bce";

// 2. Cadastrar customer
POST /customers/
Headers:
  Store-Credential: {STORE_CREDENTIAL}
Body:
  {
    "name": "João Silva",
    "email": "joao@email.com",
    "password": "123456"
  }

// 3. Customer já pode navegar, adicionar ao carrinho, comprar
```

### 2. Não Precisa Criar Seller/Store

Antes do seed:
```
❌ 1. Criar seller
❌ 2. Fazer login seller
❌ 3. Criar loja
❌ 4. Obter credential
❌ 5. Criar customer
✅ 6. Testar fluxo de compra
```

Depois do seed:
```
✅ 1. Criar customer (já tem store)
✅ 2. Testar fluxo de compra
```

---

## 📝 Código do Seed

### Localização

```
src/seed.py         # Lógica do seed
src/application.py  # Integração com FastAPI lifespan
scripts/seed_db.py  # Script manual
```

### seed.py - Função Principal

```python
async def seed_database():
    """
    Cria seller admin e loja padrão se não existirem.
    """
    
    # Criar seller admin se não existir
    admin_email = "admin@magic.com"
    admin_password = "admin"
    
    try:
        admin_seller = await Seller.get(email=admin_email)
        print(f"✓ Seller admin já existe (ID: {admin_seller.id})")
    except DoesNotExist:
        admin_seller = await Seller.create(
            name="Admin",
            email=admin_email,
            password=admin_password,
        )
        print(f"✓ Seller admin criado (ID: {admin_seller.id})")
        
        # Criar token
        access_token = str(uuid.uuid4())
        await SellerAuth.create(
            seller=admin_seller,
            access_token=access_token,
            status='valid'
        )
    
    # Criar loja padrão se não existir
    store_name = "Magic Marketplace"
    
    try:
        store = await Store.get(seller=admin_seller, name=store_name)
        print(f"✓ Loja já existe")
    except DoesNotExist:
        store_credential = str(uuid.uuid4().hex)[:250]
        store = await Store.create(
            seller=admin_seller,
            name=store_name,
            credential=store_credential
        )
        print(f"✓ Loja criada")
```

### application.py - Integração

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    
    # Startup: executar seed
    if run_seed:
        try:
            await seed_database()
        except Exception as e:
            print(f"⚠️  Erro ao executar seed: {e}")
    
    yield
    
    # Shutdown
    pass
```

---

## 🔄 Resetar Banco de Dados

### Opção 1: Deletar e Recriar

```bash
# Deletar banco
rm -f db.sqlite3*

# Rodar seed (criará novo banco com schemas)
poetry run python scripts/seed_db.py

# Ou apenas iniciar a aplicação
poetry run fastapi dev src/application.py
```

### Opção 2: Manter e Executar Seed

```bash
# Se seller/store já existem, apenas exibe mensagem
poetry run python scripts/seed_db.py
```

Output:
```
✓ Seller admin já existe (ID: 1)
✓ Loja 'Magic Marketplace' já existe (ID: 1)
```

---

## ⚙️ Configuração

### Desabilitar Seed no Startup

Se você quiser desabilitar o seed automático:

```python
# src/application.py

# Opção 1: Passar fake_db=True (usado em testes)
app = create_application(fake_db=True)

# Opção 2: Modificar create_lifespan
lifespan = create_lifespan(run_seed=False)
```

### Variável de Ambiente

Você pode adicionar uma variável de ambiente:

```python
# src/application.py
import os

run_seed = os.getenv('RUN_SEED', 'true').lower() == 'true'
lifespan = create_lifespan(run_seed=run_seed)
```

```bash
# .env
RUN_SEED=false  # Desabilita seed
```

---

## 🧪 Testes

O seed **não é executado durante os testes** porque:

```python
# tests/conftest.py
@pytest.fixture
async def client():
    app = create_application(fake_db=True)  # fake_db=True desabilita seed
    ...
```

Isso garante que:
- ✅ Testes começam com banco limpo
- ✅ Testes são isolados
- ✅ Testes não dependem de dados pre-existentes

---

## 💡 Customização

### Adicionar Mais Dados Iniciais

Você pode estender o seed para criar:

```python
# src/seed.py

async def seed_database():
    # ... código existente ...
    
    # Criar customer de exemplo
    try:
        customer = await Customer.get(email="cliente@example.com")
    except DoesNotExist:
        customer = await Customer.create(
            store=store,
            name="Cliente Exemplo",
            email="cliente@example.com",
            password="123456"
        )
        print(f"✓ Customer exemplo criado")
    
    # Criar produto de exemplo
    try:
        product = await Product.get(external_id="exemplo")
    except DoesNotExist:
        product = await Product.create(
            store=store,
            name="Produto Exemplo",
            description="Descrição do produto",
            price=10000,  # R$ 100,00
            external_id="exemplo"
        )
        print(f"✓ Produto exemplo criado")
```

### Diferentes Ambientes

```python
# src/seed.py
import os

async def seed_database():
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        # Não criar dados de exemplo em produção
        admin_password = os.getenv('ADMIN_PASSWORD', 'change-me')
    else:
        # Senha simples para desenvolvimento
        admin_password = 'admin'
    
    # ... resto do código ...
```

---

## 📚 Ver Também

- [OVERVIEW.md](./OVERVIEW.md) - Visão geral do sistema
- [AUTHENTICATION.md](./AUTHENTICATION.md) - Sistema de autenticação
- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Documentação da API
- [TESTING.md](./TESTING.md) - Estratégia de testes

