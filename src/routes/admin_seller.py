"""
Seller Admin routes
Each seller manages their own store through this admin panel
Protected by @seller_required decorator
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from decimal import Decimal
from tortoise.functions import Sum, Count
from tortoise.expressions import Q

from src.authentication import seller_required, store_required
from src.models import Order, OrderItem, Customer, Store, Product

router = APIRouter(prefix="/seller/admin", tags=["seller_admin"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def seller_admin_login_page(request: Request):
    """Página de login do seller admin"""
    return templates.TemplateResponse("admin_seller/login.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def seller_admin_dashboard_page(request: Request):
    """Dashboard principal do seller admin"""
    return templates.TemplateResponse("admin_seller/dashboard.html", {
        "request": request
    })


@router.get("/api/dashboard-stats")
@seller_required
@store_required
async def get_seller_dashboard_stats(request: Request):
    """
    Retorna estatísticas do dashboard do seller:
    - Valor total do dia (vendas da loja)
    - Valor total do mês (vendas da loja)
    - Número de customers únicos que compraram na loja
    """
    store = request.current_store
    
    # Data de hoje (início do dia)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Primeiro dia do mês
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Valor total do dia (pedidos concluídos)
    orders_today = await Order.filter(
        store=store,
        created_at__gte=today_start,
        status='paid'  # Usando 'paid' ao invés de 'completed'
    ).prefetch_related('orderitem_order__product')
    
    total_today = 0
    for order in orders_today:
        items = await order.orderitem_order.all()
        order_total = sum(item.price * item.amount for item in items)
        total_today += order_total
    
    total_today = total_today / 100  # Converter de cents para reais
    
    # Valor total do mês
    orders_month = await Order.filter(
        store=store,
        created_at__gte=month_start,
        status='paid'
    ).prefetch_related('orderitem_order__product')
    
    total_month = 0
    for order in orders_month:
        items = await order.orderitem_order.all()
        order_total = sum(item.price * item.amount for item in items)
        total_month += order_total
    
    total_month = total_month / 100  # Converter de cents para reais
    
    # Número de customers únicos que compraram (todos os tempos, qualquer status exceto cancelado)
    unique_customers = await Order.filter(
        store=store
    ).exclude(status='cancelled').distinct().values_list('customer_id', flat=True)
    
    return {
        "total_today": float(total_today),
        "total_month": float(total_month),
        "unique_customers": len(set(unique_customers))
    }


@router.get("/api/orders")
@seller_required
@store_required
async def get_seller_orders(request: Request, limit: int = 50):
    """
    Retorna lista de pedidos da loja do seller
    """
    store = request.current_store
    
    # Buscar pedidos ordenados por data (mais recentes primeiro)
    orders = await Order.filter(store=store).order_by('-created_at').limit(limit).prefetch_related('orderitem_order__product', 'customer')
    
    orders_data = []
    
    for order in orders:
        # Montar string de produtos (1x PRODUTO 1, 3x Produto 2)
        items = await order.orderitem_order.all().prefetch_related('product')
        products_str = ", ".join([f"{item.amount}x {item.product.name}" for item in items])
        
        # Calcular total do pedido
        order_total = sum(item.price * item.amount for item in items) / 100
        
        # Dados do cliente
        customer = await order.customer
        customer_email = customer.email if customer else "N/A"
        
        orders_data.append({
            "id": order.id,
            "customer_email": customer_email,
            "status": order.status,
            "products": products_str,
            "total": float(order_total),
            "created_at": order.created_at.isoformat()
        })
    
    return {"orders": orders_data}


@router.get("/products", response_class=HTMLResponse)
async def seller_admin_products_page(request: Request):
    """Página de gerenciamento de produtos do seller"""
    return templates.TemplateResponse("admin_seller/products.html", {
        "request": request
    })


@router.get("/api/products")
@seller_required
@store_required
async def get_seller_products(request: Request, limit: int = 100, offset: int = 0, status: str = None):
    """
    Retorna lista de produtos da loja do seller
    """
    store = request.current_store
    
    # Filtros
    filters = {"store": store}
    if status:
        filters["status"] = status
    
    # Buscar produtos
    products = await Product.filter(**filters).order_by('-created_at').limit(limit).offset(offset)
    
    # Total de produtos
    total = await Product.filter(**filters).count()
    
    products_data = []
    for product in products:
        products_data.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price / 100),  # Converter de cents para reais
            "price_cents": product.price,
            "status": product.status,
            "product_code": product.product_code,
            "park_code": product.park_code,
            "created_at": product.created_at.isoformat()
        })
    
    return {
        "products": products_data,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.put("/api/products/{product_id}")
@seller_required
@store_required
async def update_seller_product(request: Request, product_id: int):
    """
    Atualiza um produto da loja
    """
    store = request.current_store
    
    # Buscar produto
    product = await Product.filter(id=product_id, store=store).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Pegar dados do body
    body = await request.json()
    
    # Atualizar campos permitidos
    if "name" in body:
        product.name = body["name"]
    if "description" in body:
        product.description = body["description"]
    if "price" in body:
        # Converter de reais para cents
        product.price = int(float(body["price"]) * 100)
    if "status" in body:
        product.status = body["status"]
    
    await product.save()
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price / 100),
        "status": product.status,
        "message": "Produto atualizado com sucesso"
    }


@router.get("/customers", response_class=HTMLResponse)
async def seller_admin_customers_page(request: Request):
    """Página de visualização de clientes do seller"""
    return templates.TemplateResponse("admin_seller/customers.html", {
        "request": request
    })


@router.get("/api/customers")
@seller_required
@store_required
async def get_seller_customers(request: Request, limit: int = 100, offset: int = 0):
    """
    Retorna lista de clientes da loja do seller
    """
    store = request.current_store
    
    # Buscar customers da loja
    customers = await Customer.filter(store=store).order_by('-created_at').limit(limit).offset(offset)
    
    # Total de customers
    total = await Customer.filter(store=store).count()
    
    customers_data = []
    for customer in customers:
        # Calcular total gasto pelo customer (pedidos pagos)
        orders = await Order.filter(customer=customer, store=store, status='paid').prefetch_related('orderitem_order')
        
        total_spent = 0
        total_orders = len(orders)
        
        for order in orders:
            items = await order.orderitem_order.all()
            order_total = sum(item.price * item.amount for item in items)
            total_spent += order_total
        
        customers_data.append({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "total_spent": float(total_spent / 100),  # Converter de cents para reais
            "total_orders": total_orders,
            "created_at": customer.created_at.isoformat()
        })
    
    return {
        "customers": customers_data,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/api/customers/{customer_id}/orders")
@seller_required
@store_required
async def get_customer_orders(request: Request, customer_id: int):
    """
    Retorna pedidos de um cliente específico
    """
    store = request.current_store
    
    # Verificar se customer pertence à loja
    customer = await Customer.filter(id=customer_id, store=store).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Buscar pedidos do customer
    orders = await Order.filter(customer=customer, store=store).order_by('-created_at').prefetch_related('orderitem_order__product')
    
    orders_data = []
    for order in orders:
        items = await order.orderitem_order.all().prefetch_related('product')
        products_str = ", ".join([f"{item.amount}x {item.product.name}" for item in items])
        order_total = sum(item.price * item.amount for item in items) / 100
        
        orders_data.append({
            "id": order.id,
            "code": order.code,
            "status": order.status,
            "products": products_str,
            "total": float(order_total),
            "created_at": order.created_at.isoformat()
        })
    
    return {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email
        },
        "orders": orders_data
    }


@router.get("/orders", response_class=HTMLResponse)
async def seller_admin_orders_page(request: Request):
    """Página de visualização de pedidos do seller"""
    return templates.TemplateResponse("admin_seller/orders.html", {
        "request": request
    })

