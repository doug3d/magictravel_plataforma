# Fluxo de Produtos - Lazy Loading Strategy

## 🎯 Problema

A Maria API fornece um catálogo de produtos (ingressos) que:
- **Muda constantemente**: Preços flutuam, novos produtos surgem, outros saem do ar
- **Tem milhares de variações**: Diferentes datas, número de dias, tipos de ingresso
- **É custoso sincronizar**: Atualizar todo o catálogo seria ineficiente

## ✅ Solução: Lazy Loading

**Produtos são criados no banco de dados apenas quando um cliente demonstra interesse real** (adiciona ao carrinho).

---

## 📊 Fluxo Completo

```
┌────────────┐
│  Frontend  │
└──────┬─────┘
       │
       │ 1. GET /parks
       ├─────────────────────────────┐
       │                             ▼
       │                    ┌────────────────┐
       │                    │   Maria API    │
       │                    │                │
       │ 2. Lista de parques│  - Parks       │
       │◄───────────────────┤  - Products    │
       │                    │  - Prices      │
       │                    └────────────────┘
       │ 3. GET /parks/{id}/products
       ├─────────────────────────────┤
       │                             │
       │ 4. Catálogo de produtos     │
       │◄────────────────────────────┤
       │                             │
       │                             │
┌──────▼─────────────────────────────┴─────┐
│  VITRINE (Frontend)                      │
│  Produtos exibidos DIRETO da Maria API   │
│  Sem passar pelo banco de dados          │
└──────┬───────────────────────────────────┘
       │
       │ Cliente escolhe produto
       │
       │ 5. POST /carts/
       │    { "maria_product_code": "uuid", "amount": 2 }
       │
       ▼
┌─────────────────┐
│  Backend API    │
└────────┬────────┘
         │
         │ 6. Verifica se produto existe
         ├──────────────────────────────┐
         │                              ▼
         │                       ┌──────────────┐
         │                       │   Database   │
         │                       │              │
         │ 7. SELECT * FROM      │  Products    │
         │    product WHERE      │  (apenas os  │
         │    external_id = ?    │   que foram  │
         │                       │   adicionados│
         │◄──────────────────────│   ao carrinho)│
         │ Produto não existe    └──────────────┘
         │                              ▲
         │ 8. Buscar detalhes           │
         │    da Maria API              │
         ├──────────────────────────────┤
         │                              │
         ▼                              │
┌────────────────┐                      │
│   Maria API    │                      │
│                │                      │
│ GET /parks/    │                      │
│  {park}/       │                      │
│  products/     │                      │
│  {product}     │                      │
└────────┬───────┘                      │
         │                              │
         │ 9. Detalhes do produto       │
         │    (nome, descrição, preço)  │
         │                              │
         │ 10. CREATE Product           │
         │     (com external_id)        │
         └──────────────────────────────┤
                                        │
         ┌──────────────────────────────┘
         │
         │ 11. CREATE CartItem
         │     (vincula ao produto)
         │
         ▼
┌─────────────────┐
│  Cart criado    │
│  com produto    │
│  salvo no banco │
└─────────────────┘
```

---

## 💡 Vantagens da Abordagem

### 1. Banco Limpo
```
❌ Sem Lazy Loading:
- 10.000 produtos da Maria API
- 9.500 nunca são visualizados
- 9.000 nunca são adicionados ao carrinho
- 8.500 nunca são comprados
→ Banco poluído com dados irrelevantes

✅ Com Lazy Loading:
- 0 produtos inicialmente
- 500 produtos adicionados ao carrinho
- 400 produtos efetivamente comprados
→ Apenas dados relevantes
```

### 2. Sempre Atualizado
```
Maria API: Preço muda de R$ 750 → R$ 800

❌ Sem Lazy Loading:
- Precisa sincronizar periodicamente
- Pode mostrar preço desatualizado
- Complexidade de manter sincronizado

✅ Com Lazy Loading:
- Busca preço atual no momento de adicionar ao carrinho
- Cliente sempre vê preço mais recente
- Não precisa sincronização
```

### 3. Métricas Significativas
```sql
-- Produtos que geraram interesse (foram ao carrinho)
SELECT COUNT(*) FROM product;

-- Taxa de conversão (carrinho → pedido)
SELECT 
  (SELECT COUNT(DISTINCT product_id) FROM orderitem) * 100.0 /
  (SELECT COUNT(*) FROM product) as conversion_rate;

-- Produtos mais populares
SELECT 
  p.name,
  COUNT(DISTINCT ci.cart_id) as times_in_cart,
  COUNT(DISTINCT oi.order_id) as times_purchased
FROM product p
LEFT JOIN cartitem ci ON ci.product_id = p.id
LEFT JOIN orderitem oi ON oi.product_id = p.id
GROUP BY p.id
ORDER BY times_purchased DESC;
```

### 4. Histórico de Preços
```python
# Preço salvo no momento que entrou no carrinho
product.price = 75098  # R$ 750,98

# Preço pode ter mudado na Maria API
current_price = maria_api.get_product_detail(product.external_id).starting_price

# Mas no pedido, salvamos o preço do momento da compra
order_item.price = product.price  # Snapshot
```

---

## 🔧 Implementação Recomendada

### Backend: Endpoint de Carrinho (Proposta)

```python
# src/routes/cart.py

@router.post("/")
@customer_required
@store_required
async def add_to_cart(request: Request, body: CartItemSchemaV2):
    """
    Body:
    {
      "maria_product_code": "987cedca-559e-4b71-a00b-932c5208b846",
      "park_code": "bdab5664-ab6c-4cbd-817e-59a8c76b4dac",
      "amount": 2
    }
    """
    
    # 1. Verificar se produto já existe no banco
    product = await Product.filter(
        store_id=request.current_store.id,
        external_id=body.maria_product_code
    ).first()
    
    if not product:
        # 2. Buscar detalhes da Maria API
        maria_client = MariaApi()
        try:
            product_detail = maria_client.get_park_product_detail(
                park_code=body.park_code,
                product_code=body.maria_product_code
            )
        except Exception as e:
            raise HTTPException(
                status_code=404, 
                detail="Product not available in Maria API"
            )
        
        # 3. Criar produto no banco
        product = await Product.create(
            store_id=request.current_store.id,
            name=product_detail.ticket_name,
            description=f"{product_detail.park_included}",
            price=_convert_price_to_cents(product_detail.starting_price.usdbrl.amount),
            external_id=body.maria_product_code,
            status='active'
        )
    
    # 4. Validar se produto está ativo
    if product.status != 'active':
        raise HTTPException(status_code=404, detail="Product inactive")
    
    # 5. Obter ou criar carrinho
    cart = await Cart.filter(
        store_id=request.current_store.id,
        customer_id=request.current_user.id,
        status='active'
    ).first()
    
    if not cart:
        cart = await Cart.create(
            store_id=request.current_store.id,
            customer_id=request.current_user.id,
            status='active'
        )
    
    # 6. Adicionar item ao carrinho
    cart_item = await CartItem.filter(
        cart_id=cart.id,
        product_id=product.id
    ).first()
    
    if cart_item:
        # Atualizar quantidade se já existe
        cart_item.amount += body.amount
        await cart_item.save()
    else:
        # Criar novo item
        await CartItem.create(
            cart_id=cart.id,
            product_id=product.id,
            amount=body.amount
        )
    
    return await get_cart_items(request.current_store.id, request.current_user.id)


def _convert_price_to_cents(price_string: str) -> int:
    """Converte string 'R$ 750.98' → 75098 (centavos)"""
    return int(float(price_string) * 100)
```

### Frontend: Fluxo de UI

```javascript
// 1. Página de Catálogo
async function loadProducts() {
  // Buscar direto da Maria API
  const parks = await mariaApi.get('/parks/');
  const selectedPark = parks[0];
  
  const products = await mariaApi.get(
    `/parks/${selectedPark.code}/products`,
    {
      params: {
        forDate: '2024-12-25',
        numberDays: 3
      }
    }
  );
  
  // Exibir produtos (NÃO estão no banco ainda)
  displayProducts(products);
}

// 2. Adicionar ao Carrinho
async function addToCart(mariaProduct) {
  try {
    // Backend vai criar o produto se não existir
    const response = await backendApi.post('/carts/', {
      maria_product_code: mariaProduct.code,
      park_code: currentPark.code,
      amount: 1
    });
    
    showSuccess('Produto adicionado ao carrinho!');
    updateCartBadge(response.items.length);
    
  } catch (error) {
    if (error.response?.status === 404) {
      showError('Produto não está mais disponível');
    } else {
      showError('Erro ao adicionar produto');
    }
  }
}

// 3. Página do Carrinho
async function loadCart() {
  // Agora os produtos ESTÃO no banco
  const cart = await backendApi.get('/carts/me');
  
  // Exibir com dados do banco (snapshot do momento que foi adicionado)
  displayCart(cart.items);
}
```

---

## 🎨 UI/UX Considerations

### Indicador Visual

```jsx
// Produto na vitrine (Maria API)
<ProductCard>
  <ProductImage />
  <ProductName>{product.ticketName}</ProductName>
  <Price>{product.startingPrice.usdbrl.amount}</Price>
  <Badge color="blue">Preço em tempo real</Badge>
  <AddToCartButton />
</ProductCard>

// Produto no carrinho (Banco de dados)
<CartItem>
  <ProductName>{product.name}</ProductName>
  <Price>{product.price}</Price>
  <Badge color="green">Preço garantido</Badge>
  <RemoveButton />
</CartItem>
```

### Feedback de Loading

```jsx
async function addToCart(product) {
  setLoading(true);
  
  try {
    // Esta chamada pode demorar (busca Maria API + cria no banco)
    await backendApi.post('/carts/', { ... });
    
    toast.success('Produto adicionado!');
  } catch (error) {
    toast.error('Erro ao adicionar produto');
  } finally {
    setLoading(false);
  }
}
```

### Tratamento de Indisponibilidade

```jsx
// Se produto foi removido da Maria API
if (error.response?.status === 404) {
  showModal({
    title: 'Produto Indisponível',
    message: 'Este produto não está mais disponível para compra.',
    actions: [
      { label: 'Ver produtos similares', onClick: () => suggestAlternatives() },
      { label: 'Fechar', onClick: () => closeModal() }
    ]
  });
}
```

---

## 📈 Monitoramento

### Métricas Importantes

```sql
-- 1. Produtos únicos no carrinho vs vendidos
SELECT 
  COUNT(DISTINCT p.id) as total_products,
  COUNT(DISTINCT CASE WHEN ci.id IS NOT NULL THEN p.id END) as in_cart,
  COUNT(DISTINCT CASE WHEN oi.id IS NOT NULL THEN p.id END) as sold
FROM product p
LEFT JOIN cartitem ci ON ci.product_id = p.id
LEFT JOIN orderitem oi ON oi.product_id = p.id;

-- 2. Tempo médio entre adicionar ao carrinho e comprar
SELECT 
  AVG(TIMESTAMPDIFF(MINUTE, p.created_at, o.created_at)) as avg_minutes
FROM product p
JOIN orderitem oi ON oi.product_id = p.id
JOIN order o ON o.id = oi.order_id;

-- 3. Produtos abandonados no carrinho
SELECT 
  p.name,
  COUNT(DISTINCT ci.cart_id) as times_in_cart,
  COUNT(DISTINCT oi.order_id) as times_purchased,
  COUNT(DISTINCT ci.cart_id) - COUNT(DISTINCT oi.order_id) as abandoned
FROM product p
JOIN cartitem ci ON ci.product_id = p.id
LEFT JOIN orderitem oi ON oi.product_id = p.id
GROUP BY p.id
HAVING abandoned > 0
ORDER BY abandoned DESC;
```

---

## ⚠️ Considerações

### 1. Preços Podem Divergir

```
Cliente vê na vitrine: R$ 750,98 (Maria API agora)
Cliente adiciona ao carrinho: R$ 755,00 (Maria API no momento de adicionar)
```

**Solução**: Mostrar aviso no checkout se houver divergência grande.

### 2. Produto Pode Não Estar Mais Disponível

```python
try:
    product_detail = maria_client.get_park_product_detail(...)
except HTTPStatusError as e:
    if e.response.status_code == 404:
        # Produto não existe mais na Maria API
        raise HTTPException(404, "Product no longer available")
```

### 3. Performance

- Cache de produtos da Maria API (5-10 minutos)
- Background job para verificar produtos inativos
- Índice em `external_id` para busca rápida

---

## 🔄 Sincronização Opcional

Para produtos já no banco, você pode sincronizar preços:

```python
# scripts/sync_product_prices.py

async def sync_product_prices(store_id: int):
    """Atualiza preços dos produtos existentes"""
    maria_client = MariaApi()
    products = await Product.filter(store_id=store_id, status='active').all()
    
    for product in products:
        try:
            detail = maria_client.get_park_product_detail(
                park_code=product.park_code,  # Precisa adicionar este campo
                product_code=product.external_id
            )
            
            new_price = int(float(detail.starting_price.usdbrl.amount) * 100)
            
            if product.price != new_price:
                product.price = new_price
                await product.save()
                print(f"Updated {product.name}: {product.price} → {new_price}")
                
        except Exception as e:
            print(f"Error syncing {product.name}: {e}")

# Executar diariamente
# cron: 0 3 * * * poetry run python scripts/sync_product_prices.py
```

Mas isso é **opcional** - o lazy loading funciona perfeitamente sem sincronização!

