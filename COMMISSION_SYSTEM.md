# Sistema de Comissões

Este documento explica como funciona o sistema de comissões da plataforma Magic Marketplace.

## 📊 Visão Geral

O sistema aplica **DUAS** comissões em cascata sobre os preços dos produtos da Maria API:

1. **Comissão da Plataforma**: 5% (fixa)
2. **Comissão do Seller**: Configurável (0% a 100%)

---

## 🧮 Fórmula de Cálculo

```
Preço Base (Maria API)
    ↓
+ 5% (Comissão da Plataforma)
    ↓
= Subtotal
    ↓
+ X% (Comissão do Seller)
    ↓
= Preço Final (exibido para o cliente)
```

### Exemplo Prático:

```
Preço Base:           R$ 100,00
+ Plataforma (5%):    R$   5,00
──────────────────────────────
Subtotal:             R$ 105,00
+ Seller (10%):       R$  10,50
──────────────────────────────
Preço Final:          R$ 115,50
```

---

## 🔧 Implementação

### 1. Constante Global (`src/constants.py`)

```python
PLATFORM_COMMISSION_PERCENTAGE = Decimal('5.0')  # 5%
```

### 2. Aplicação nas Rotas Maria API (`src/routes/maria.py`)

As comissões são aplicadas **ANTES** de exibir os produtos:

- `GET /maria/parks/{park_code}/products` - Lista de produtos
- `GET /maria/parks/{park_code}/products/{product_code}` - Detalhe do produto

**Campos adicionados na resposta:**
- `original_price`: Preço base da Maria API
- `platform_commission`: 5.0
- `seller_commission`: Configurado pelo seller
- `prices.usdbrl.amount`: Preço final (com comissões)

### 3. Aplicação na Criação de Produtos (`src/routes/product.py`)

Quando o produto é **criado no banco** (lazy loading ao adicionar no carrinho):

```python
base_price = Decimal(str(price_str))
price_with_platform = base_price * (1 + PLATFORM_COMMISSION_PERCENTAGE / 100)
seller_commission = Decimal(str(request.current_store.commission_percentage))
final_price = price_with_platform * (1 + seller_commission / 100)
price_cents = int(final_price * 100)  # Salvo no banco em centavos
```

---

## 💰 Distribuição de Lucro

### Exemplo com Produto de R$ 100,00:

| Parte | Valor | % do Total |
|-------|-------|------------|
| Fornecedor (Maria API) | R$ 100,00 | 86.5% |
| Plataforma (5%) | R$ 5,00 | 4.3% |
| Seller (10% sobre R$ 105) | R$ 10,50 | 9.1% |
| **Cliente Paga** | **R$ 115,50** | **100%** |

---

## ⚙️ Configuração do Seller

O seller pode configurar sua comissão em:

**`/seller/admin/settings`**

- **Campo**: Comissão do Seller (%)
- **Validação**: 0% a 100%
- **Padrão**: 0%
- **Persistência**: Campo `commission_percentage` no model `Store`

---

## 🔄 Fluxo Completo

```
1. Cliente acessa loja
   ↓
2. Frontend busca produtos: GET /maria/parks/{code}/products
   ↓
3. Backend aplica comissões (5% + seller%)
   ↓
4. Frontend exibe preço final
   ↓
5. Cliente adiciona ao carrinho
   ↓
6. Backend cria produto no banco com preço final
   ↓
7. Produto salvo com comissões já aplicadas
```

---

## 📝 Considerações Importantes

1. **Transparência**: O preço exibido é o preço final (já inclui todas as comissões)
2. **Lazy Loading**: Produtos só são salvos no banco quando adicionados ao carrinho
3. **Preço Fixo**: Uma vez salvo no banco, o preço não muda (mesmo que a comissão seja alterada)
4. **Comissão da Plataforma**: Fixa em 5%, definida em `src/constants.py`
5. **Comissão do Seller**: Configurável, definida em `Store.commission_percentage`

---

## 🛡️ Segurança

- ✅ Comissões aplicadas no backend (cliente não pode manipular)
- ✅ Validação de valores (0% a 100%)
- ✅ Uso de `Decimal` para precisão financeira
- ✅ Isolamento por store (multi-tenant)

---

## 🔮 Futuras Melhorias

- [ ] Dashboard com breakdown de comissões
- [ ] Relatório de lucro por período
- [ ] Histórico de alterações de comissão
- [ ] Comissão diferenciada por categoria de produto
- [ ] Comissão da plataforma configurável (admin do sistema)

---

_Última atualização: Implementação do sistema de comissões duplas._

