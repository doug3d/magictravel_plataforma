# Maria API Integration - Documentação

## 🎯 O que é Maria API?

Maria API é uma API externa que fornece informações sobre **parques temáticos da Disney** e seus **produtos (ingressos)**. Os dados incluem:

- Lista de parques (Disney Orlando, Universal, etc.)
- Produtos/ingressos disponíveis para cada parque
- Preços em diferentes moedas (USD, BRL)
- Detalhes dos ingressos (dias, tipo, restrições)

## 📍 Localização no Código

```
magic-marketplace/
└── src/
    └── integrations/
        └── maria_api/
            ├── maria.py      # Cliente HTTP (MariaApi class)
            └── dto.py        # Modelos Pydantic
```

---

## 🔌 Cliente Maria API

### Configuração

A URL base é configurada via variável de ambiente:
```bash
MARIA_API_ENDPOINT=http://localhost:8001
```

### Classe MariaApi

```python
from src.integrations.maria_api.maria import MariaApi

# Inicializar
maria_client = MariaApi()

# Métodos disponíveis
parks = maria_client.get_parks(location="FL")
park = maria_client.get_park(park_code="uuid")
products = maria_client.get_park_products(park_code="uuid")
product = maria_client.get_park_product_detail(park_code="uuid", product_code="uuid")
```

---

## 📋 Endpoints Disponíveis

### 1. GET `/parks/` - Listar Parques

**Parâmetros:**
- `location` (opcional): Estado do parque (ex: "FL" para Florida)

**Response:**
```json
[
  {
    "code": "bdab5664-ab6c-4cbd-817e-59a8c76b4dac",
    "name": "Disney Orlando",
    "description": "Walt Disney World Resort...",
    "images": {
      "cover": "https://i.imgur.com/2Nn9jYe.jpg",
      "thumbnail": "https://i.imgur.com/2Nn9jYe.jpg"
    },
    "parklocation": {
      "city": "Orlando",
      "state": "FL"
    },
    "attraction": "Magic Kingdom, EPCOT...",
    "status": true,
    "translations": []
  }
]
```

**Modelo Pydantic:**
```python
class Park(BaseModel):
    code: str
    name: str
    description: str
    images: ParkImages
    location: ParkLocation  # alias: "parklocation"
    attraction: str
    status: Union[bool, str]
    translations: List[Translation]
```

---

### 2. GET `/parks/{park_code}` - Detalhes do Parque

**Response:** Mesmo formato do endpoint de lista (objeto único)

---

### 3. GET `/parks/{park_code}/products` - Listar Produtos do Parque

**Parâmetros Query (todos opcionais):**
- `forDate`: Data da visita (YYYY-MM-DD)
- `numberDays`: Número de dias do ingresso
- `numAdults`: Número de adultos
- `numChildren`: Número de crianças
- `isSpecial`: Se é evento especial

**Response:**
```json
[
  {
    "code": "987cedca-559e-4b71-a00b-932c5208b846",
    "ticketName": "Magic Kingdom - 1 Day Dated Theme Park Ticket",
    "parkIncluded": "Magic Kingdom® Park",
    "parkLocation": {
      "city": "Orlando",
      "state": "FL"
    },
    "isMultiDays": false,
    "isParkToPark": false,
    "isDated": true,
    "isTimed": false,
    "availableOptions": [],
    "extensions": {
      "numberDays": 1,
      "usageWindow": 7,
      "numberParks": 1,
      "productKind": "admission",
      "aboutTicket": "This ticket provides...",
      "ticketType": "eTicket",
      "ticketBanner": "https://i.imgur.com/SLZzytz.png",
      "observations": ""
    },
    "prices": {
      "adult": {
        "original": { "amount": "129.48", "currency": "USD", "symbol": "$" },
        "usdbrl": { "amount": "750.98", "currency": "BRL", "symbol": "R$" }
      },
      "child": { /* ... */ },
      "total": { /* ... */ },
      "type": "starting"
    },
    "isSpecial": false,
    "translations": [],
    "hasActivePromo": false
  }
]
```

**Modelo Pydantic:**
```python
class ParkProduct(BaseModel):
    code: str
    ticket_name: str           # alias: "ticketName"
    park_included: str         # alias: "parkIncluded"
    park_location: ParkLocation # alias: "parkLocation"
    is_multi_days: bool        # alias: "isMultiDays"
    is_park_to_park: bool      # alias: "isParkToPark"
    is_dated: bool             # alias: "isDated"
    is_timed: bool             # alias: "isTimed"
    available_options: List[str]
    extensions: ParkProductExtension
    prices: Prices
    is_special: bool
    translations: List[Translation]
    has_active_promo: bool
```

---

### 4. GET `/parks/{park_code}/products/{product_code}` - Detalhe do Produto

**Parâmetros Query (mesmos do endpoint anterior)**

**Response:**
```json
{
  "code": "987cedca-559e-4b71-a00b-932c5208b846",
  "ticketName": "Magic Kingdom - 1 Day Dated Theme Park Ticket",
  "parkIncluded": "Magic Kingdom® Park",
  "parklocation": {  // Note: minúsculo
    "city": "Orlando",
    "state": "FL"
  },
  "extensions": {
    "days": 1,       // Note: não é "numberDays"
    "parks": 1,      // Note: não é "numberParks"
    "productKind": "admission",
    "aboutTicket": "...",
    "ticketType": "eTicket",
    "ticketBanner": "...",
    "observations": "",
    "notes": ""
  },
  "startingPrice": {  // Note: não é "prices"
    "original": { "amount": "129.48", "currency": "USD", "symbol": "$" },
    "usdbrl": { "amount": "750.98", "currency": "BRL", "symbol": "R$" }
  },
  "isSpecial": false,
  "status": true,
  "translations": []
}
```

**Modelo Pydantic:**
```python
class ParkProductDetail(BaseModel):
    code: str
    ticket_name: str
    park_included: str
    park_location: ParkLocation  # alias: "parklocation" (minúsculo!)
    is_multi_days: bool
    is_park_to_park: bool
    is_dated: bool
    is_timed: bool
    available_options: List[str]
    extensions: ParkProductDetailExtension  # Estrutura diferente
    starting_price: PricePair  # Não é "prices"!
    is_special: bool
    status: Union[bool, str]
    translations: List[Translation]
```

---

## ⚠️ Diferenças Importantes

### Lista vs Detalhe de Produto

| Campo           | Lista (`/products`)    | Detalhe (`/products/{id}`)  |
|-----------------|------------------------|----------------------------|
| parkLocation    | `parkLocation`         | `parklocation` (minúsculo) |
| Preço           | `prices` (objeto complexo) | `startingPrice` (simples) |
| Extensions.days | `numberDays` (alias)   | `days` (direto)            |
| Extensions.parks| `numberParks` (alias)  | `parks` (direto)           |
| has_active_promo| ✅ Sim                 | ❌ Não                     |
| status          | ❌ Não                 | ✅ Sim                     |

**Por isso temos 2 modelos diferentes:**
- `ParkProduct` → para lista
- `ParkProductDetail` → para detalhe

---

## 🔄 Fluxo de Integração Recomendado

### 1. Frontend: Exibir Vitrine

```javascript
// Buscar parques disponíveis
const parks = await mariaApi.get('/parks/', { params: { location: 'FL' } });

// Usuário seleciona um parque
const selectedPark = parks[0];

// Buscar produtos do parque
const products = await mariaApi.get(
  `/parks/${selectedPark.code}/products`,
  {
    params: {
      forDate: '2024-12-25',
      numberDays: 3,
      numAdults: 2,
      numChildren: 1
    }
  }
);

// Exibir produtos na vitrine
displayProducts(products);
```

### 2. Backend: Criar Produto no Banco

**❌ NÃO fazer:** Sincronizar todos os produtos da Maria API para o banco

**✅ FAZER:** Criar produto apenas quando adicionado ao carrinho

```python
# Frontend envia para backend:
POST /carts/
{
  "maria_product_code": "987cedca-559e-4b71-a00b-932c5208b846",
  "amount": 2
}

# Backend (implementação futura):
async def add_to_cart(maria_product_code: str, amount: int):
    # 1. Buscar detalhes atualizados da Maria API
    maria_client = MariaApi()
    product_detail = maria_client.get_park_product_detail(
        park_code="bdab5664-ab6c-4cbd-817e-59a8c76b4dac",
        product_code=maria_product_code
    )
    
    # 2. Verificar se produto já existe no banco
    product = await Product.filter(external_id=maria_product_code).first()
    
    if not product:
        # 3. Criar produto no banco com dados da Maria API
        product = await Product.create(
            store_id=request.current_store.id,
            name=product_detail.ticket_name,
            description=product_detail.park_included,
            price=int(float(product_detail.starting_price.usdbrl.amount) * 100),
            external_id=maria_product_code,
            status='active'
        )
    
    # 4. Adicionar ao carrinho
    await CartItem.create(
        cart_id=cart.id,
        product_id=product.id,
        amount=amount
    )
```

---

## 💾 Estratégia de Cache (Recomendado)

### Problema
Maria API pode ser lenta ou ter rate limits.

### Solução
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedMariaApi:
    def __init__(self):
        self.maria_client = MariaApi()
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)
    
    def get_parks(self, location="FL"):
        cache_key = f"parks_{location}"
        
        # Verificar cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                return cached_data
        
        # Buscar da API
        data = self.maria_client.get_parks(location)
        self._cache[cache_key] = (data, datetime.now())
        return data
```

---

## 🧪 Testes

### Testes de Integração

```python
# tests/integration/test_maria_api.py

@pytest.mark.anyio
async def test_should_get_parks():
    maria_client = MariaApi()
    parks = maria_client.get_parks()
    assert len(parks) > 0
    assert parks[0].code is not None
    assert parks[0].name is not None

@pytest.mark.anyio
async def test_should_get_park_products():
    maria_client = MariaApi()
    products = maria_client.get_park_products(
        "bdab5664-ab6c-4cbd-817e-59a8c76b4dac"
    )
    assert len(products) > 0
    assert products[0].ticket_name is not None
```

### Executar Testes
```bash
# Configurar variável de ambiente
export MARIA_API_ENDPOINT=http://localhost:8001

# Rodar testes
poetry run pytest tests/integration/test_maria_api.py -v
```

---

## 🔧 Troubleshooting

### Erro: ValidationError
```
pydantic_core._pydantic_core.ValidationError: Field required
```

**Causa:** Modelo Pydantic não corresponde à resposta da API

**Solução:**
1. Verificar a resposta real da API (adicionar print)
2. Ajustar aliases no modelo (`Field(..., alias="...")`)
3. Verificar se está usando o modelo correto (Product vs ProductDetail)

### Erro: Connection Refused
```
httpx.ConnectError: [Errno 61] Connection refused
```

**Causa:** Maria API não está rodando

**Solução:**
```bash
# Verificar se Maria API está rodando
curl http://localhost:8001/parks/

# Iniciar Maria API
cd mariaAPI
poetry run uvicorn main:app --reload --port 8001
```

### Erro: 404 Not Found
```
httpx.HTTPStatusError: 404 Not Found
```

**Causa:** Endpoint ou código de parque/produto incorreto

**Solução:**
- Verificar URL exata no código da Maria API
- Usar códigos UUID válidos retornados pela API

---

## 📚 Referências Úteis

### Códigos de Parques Conhecidos
```python
DISNEY_ORLANDO = "bdab5664-ab6c-4cbd-817e-59a8c76b4dac"
UNIVERSAL_ORLANDO = "0db4e7c0-975c-4f90-b4d8-50992947cd65"
```

### Estrutura de Preços
```python
# prices.adult.usdbrl.amount → String "750.98"
# Converter para centavos:
price_cents = int(float(amount) * 100)  # 75098
```

### Conversão de Campos
```python
# Maria API → Banco de Dados
{
    "ticketName": "Magic Kingdom...",      # → name
    "parkIncluded": "Magic Kingdom® Park", # → description
    "startingPrice.usdbrl.amount": "750.98", # → price (75098)
    "code": "987cedca-..."                 # → external_id
}
```

