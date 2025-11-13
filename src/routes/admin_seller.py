"""
Seller Admin routes
Each seller manages their own store through this admin panel
Protected by @seller_required decorator
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from decimal import Decimal
from tortoise.functions import Sum, Count
from tortoise.expressions import Q

from src.authentication import seller_required, store_required
from src.models import Order, OrderItem, Customer, Store

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
    
    # Número de customers únicos que compraram (todos os tempos)
    unique_customers = await Order.filter(
        store=store,
        status='paid'
    ).distinct().values_list('customer_id', flat=True)
    
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

