# Estratégia de Testes

## 🎯 Visão Geral

O projeto utiliza **pytest** com testes ordenados para simular fluxos completos de usuário. Os testes são divididos em:

1. **Testes de API** (`tests/api/`) - Endpoints da aplicação
2. **Testes de Integração** (`tests/integration/`) - Integração com Maria API

---

## 🏗️ Estrutura de Testes

```
tests/
├── conftest.py                  # Fixtures compartilhadas
├── api/
│   ├── test_seller.py          # [Order 1-2]  Seller endpoints
│   ├── test_store.py           # [Order 3-4]  Store endpoints
│   ├── test_customer.py        # [Order 5-7]  Customer endpoints
│   ├── test_product.py         # [Order 8-10] Product endpoints
│   ├── test_cart.py            # [Order 11-15] Cart endpoints
│   └── test_order.py           # [Order 16-19] Order endpoints
└── integration/
    └── test_maria_api.py       # [Order 20-23] Maria API integration
```

---

## 📦 Configuração

### pyproject.toml

```toml
[project]
dependencies = [
    "pytest (>=8.4.2,<9.0.0)",
    "pytest-order (>=1.3.0,<2.0.0)",
    "httpx (>=0.28.1,<0.29.0)",
    "asgi-lifespan (>=2.1.0,<3.0.0)",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

### conftest.py - Fixtures

```python
import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from src.application import create_application

@pytest.fixture
async def client():
    """Cliente HTTP assíncrono para testes"""
    app = create_application(fake_db=True)  # Banco em memória
    
    async with LifespanManager(app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

@pytest.fixture
async def get_authenticated_seller_access_token(client: AsyncClient):
    """Token de seller autenticado"""
    request = await client.post(
        "/sellers/",
        json={
            "name": "Vendedor",
            "email": "vendedor@magic.com",
            "password": "123456",
        },
    )
    return request.json()["access_token"]

@pytest.fixture
async def get_authenticated_store_credential(client: AsyncClient, 
                                             get_authenticated_seller_access_token: str):
    """Credential de store criada"""
    await client.post(
        "/stores/",
        headers={"Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}"},
        json={"name": "Magic Store"},
    )
    
    request = await client.get(
        "/stores/1/get-credential",
        headers={"Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}"},
    )
    return request.json()["credential"]

@pytest.fixture
async def get_authenticated_customer_access_token(client: AsyncClient, 
                                                  get_authenticated_store_credential: str):
    """Token de customer autenticado"""
    request = await client.post(
        "/customers/",
        headers={"Store-Credential": get_authenticated_store_credential},
        json={
            "name": "Guilherme",
            "email": "guilherme@gmail.com",
            "password": "123456",
        },
    )
    return request.json()["access_token"]
```

---

## 🔢 Testes Ordenados

### Por que Ordem?

Os testes simulam um **fluxo real de usuário**:
1. Seller cria conta
2. Seller cria loja
3. Customer cria conta na loja
4. Seller adiciona produto
5. Customer adiciona ao carrinho
6. Customer finaliza pedido

### Marcadores de Ordem

```python
@pytest.mark.anyio
@pytest.mark.order(1)  # Executado primeiro
async def test_should_create_seller(client: AsyncClient):
    ...

@pytest.mark.anyio
@pytest.mark.order(2)  # Executado depois
async def test_shouldnt_create_seller_with_same_email(client: AsyncClient):
    ...
```

---

## 📝 Exemplos de Testes

### Teste de Sucesso

```python
@pytest.mark.anyio
@pytest.mark.order(1)
async def test_should_create_seller(client: AsyncClient):
    request = await client.post(
        "/sellers/",
        json={
            "name": "Vendedor",
            "email": "vendedor@magic.com",
            "password": "123456",
        },
    )
    response = request.json()
    
    # Assertions
    assert request.status_code == 200
    assert response["seller_id"] == 1
    assert response["name"] == "Vendedor"
    assert response["access_token"] is not None
```

### Teste de Falha (Validação)

```python
@pytest.mark.anyio
@pytest.mark.order(2)
async def test_shouldnt_create_seller_with_same_email(client: AsyncClient):
    request = await client.post(
        "/sellers/",
        json={
            "name": "Vendedor",
            "email": "vendedor@magic.com",  # Email já existe
            "password": "123456",
        },
    )
    response = request.json()
    
    # Assertions
    assert request.status_code == 400
    assert response["detail"] == "Email already registered"
```

### Teste com Autenticação

```python
@pytest.mark.anyio
@pytest.mark.order(4)
async def test_should_create_store_with_seller(
    client: AsyncClient,
    get_authenticated_seller_access_token: str
):
    request = await client.post(
        "/stores/",
        headers={
            "Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}",
        },
        json={"name": "Magic Store"},
    )
    response = request.json()
    
    assert request.status_code == 200
    assert response["id"] == 1
    assert response["name"] == "Magic Store"
```

### Teste com Múltiplos Headers

```python
@pytest.mark.anyio
@pytest.mark.order(10)
async def test_should_create_product_with_seller_authorization(
    client: AsyncClient,
    get_authenticated_seller_access_token: str,
    get_authenticated_store_credential: str
):
    request = await client.post(
        "/stores/1/products",
        headers={
            "Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}",
            "Store-Credential": get_authenticated_store_credential,
        },
        json={
            "name": "Produto de Teste",
            "description": "Descrição do produto de teste",
            "price": 100,
            "external_id": "1234567890",
        },
    )
    response = request.json()
    
    assert request.status_code == 200
    assert response["id"] == 1
    assert response["name"] == "Produto de Teste"
    assert response["price"] == 100
```

---

## 🌐 Testes de Integração com Maria API

### Setup

```python
# tests/integration/test_maria_api.py
import pytest
from src.integrations.maria_api.maria import MariaApi

@pytest.mark.anyio
@pytest.mark.order(20)
async def test_should_get_parks():
    maria_client = MariaApi()
    parks = maria_client.get_parks()
    
    assert len(parks) > 0
    assert parks[0].code is not None
    assert parks[0].name is not None
    assert parks[0].location is not None
```

### Variável de Ambiente

```bash
# .env ou export
MARIA_API_ENDPOINT=http://localhost:8001

# Executar testes
poetry run pytest tests/integration/
```

---

## 🚀 Executando Testes

### Todos os Testes

```bash
poetry run pytest
```

### Testes Específicos

```bash
# Por arquivo
poetry run pytest tests/api/test_seller.py

# Por função
poetry run pytest tests/api/test_seller.py::test_should_create_seller

# Por marcador
poetry run pytest -m order
```

### Com Verbose

```bash
poetry run pytest -v
poetry run pytest -vv  # Ainda mais detalhado
```

### Com Output (print statements)

```bash
poetry run pytest -s
```

### Stop on First Failure

```bash
poetry run pytest -x
```

### Executar a Partir de um Teste

```bash
# Executar apenas testes após order 10
poetry run pytest --order-markers="order>=10"
```

---

## 📊 Coverage

### Instalar Coverage

```bash
poetry add --group dev pytest-cov
```

### Executar com Coverage

```bash
# Gerar relatório
poetry run pytest --cov=src --cov-report=html

# Ver relatório
open htmlcov/index.html
```

### Coverage Config

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

---

## 🧪 Padrões de Teste

### 1. AAA Pattern (Arrange, Act, Assert)

```python
async def test_should_add_to_cart():
    # Arrange - Preparar dados
    product_id = 1
    amount = 2
    
    # Act - Executar ação
    request = await client.post(
        "/carts/",
        headers={"Customer-Authorization": f"Bearer {token}"},
        json={"product_id": product_id, "amount": amount}
    )
    response = request.json()
    
    # Assert - Verificar resultado
    assert request.status_code == 200
    assert response["cart_empty"] == False
    assert response["items"][0]["amount"] == amount
```

### 2. Naming Convention

```python
# Formato: test_should_{action}_{condition}
test_should_create_seller()
test_shouldnt_create_seller_without_email()
test_should_add_product_with_valid_token()
test_shouldnt_add_product_without_authorization()
```

### 3. One Assertion per Concept

```python
# ❌ Ruim: Muitas assertions não relacionadas
def test_cart():
    assert cart.id == 1
    assert cart.customer_id == 1
    assert cart.items[0].amount == 2
    assert order.status == "created"  # Não relacionado ao cart

# ✅ Bom: Assertions relacionadas
def test_cart_should_have_correct_items():
    assert len(cart.items) == 1
    assert cart.items[0].product_id == 1
    assert cart.items[0].amount == 2

def test_order_should_be_created():
    assert order.status == "created"
    assert order.code is not None
```

---

## 🐛 Debugging Testes

### Print Request/Response

```python
async def test_debug():
    request = await client.post("/sellers/", json={"name": "Test"})
    
    # Debug
    print("Status:", request.status_code)
    print("Response:", request.json())
    print("Headers:", request.headers)
    
    assert request.status_code == 200
```

### Pytest -s (show prints)

```bash
poetry run pytest -s tests/api/test_seller.py
```

### pdb (Python Debugger)

```python
async def test_debug():
    import pdb; pdb.set_trace()  # Breakpoint
    
    request = await client.post(...)
    # Execução pausa aqui para inspeção
```

### pytest --pdb (auto breakpoint on error)

```bash
poetry run pytest --pdb
```

---

## ⚡ Dicas de Performance

### 1. Paralelizar Testes (pytest-xdist)

```bash
poetry add --group dev pytest-xdist

# Executar em paralelo
poetry run pytest -n auto
```

**Atenção**: Não funciona com testes ordenados que dependem de estado compartilhado!

### 2. Cache de Fixtures

```python
@pytest.fixture(scope="session")  # Uma vez por sessão
async def database():
    ...

@pytest.fixture(scope="module")  # Uma vez por módulo
async def app():
    ...

@pytest.fixture(scope="function")  # Padrão: uma vez por teste
async def client():
    ...
```

### 3. Marcar Testes Lentos

```python
@pytest.mark.slow
@pytest.mark.integration
async def test_maria_api_integration():
    ...

# Executar apenas testes rápidos
pytest -m "not slow"

# Executar apenas integração
pytest -m integration
```

---

## 📈 Estratégias Avançadas

### Mocking Maria API

```python
from unittest.mock import patch, MagicMock

@pytest.mark.anyio
async def test_add_to_cart_with_maria_api_down():
    with patch('src.integrations.maria_api.maria.MariaApi.get_park_product_detail') as mock:
        # Simular erro da Maria API
        mock.side_effect = Exception("Maria API down")
        
        request = await client.post("/carts/", json={...})
        
        assert request.status_code == 503  # Service unavailable
```

### Factories (Factory Boy)

```python
# tests/factories.py
import factory
from src.models import Product

class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f"Product {n}")
    price = factory.Faker('random_int', min=1000, max=50000)
    external_id = factory.Faker('uuid4')
    status = 'active'

# Usar em testes
async def test_with_factory():
    product = await ProductFactory.create()
    assert product.name.startswith("Product")
```

### Parametrização

```python
@pytest.mark.parametrize("price,expected", [
    (100, 100),
    (0, 0),
    (-1, 0),  # Preço negativo deve ser 0
])
async def test_product_price_validation(price, expected):
    product = await Product.create(name="Test", price=price)
    assert product.price == expected
```

---

## ✅ Checklist de Testes

Antes de commitar:

- [ ] Todos os testes passam (`pytest`)
- [ ] Testes cobrem casos de sucesso
- [ ] Testes cobrem casos de erro (validações)
- [ ] Testes cobrem autenticação/autorização
- [ ] Testes seguem naming convention
- [ ] Testes são independentes (podem rodar isolados)
- [ ] Coverage acima de 80% (`pytest --cov`)
- [ ] Sem prints de debug deixados no código

---

## 🎯 Executar Suite Completa

```bash
#!/bin/bash
# tests.sh

echo "🧪 Executando testes..."
poetry run pytest -v

echo "\n📊 Coverage Report..."
poetry run pytest --cov=src --cov-report=term-missing

echo "\n✅ Testes concluídos!"
```

```bash
chmod +x tests.sh
./tests.sh
```

