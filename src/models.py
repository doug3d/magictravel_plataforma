from tortoise.models import Model
from tortoise import fields


ORDER_STATUS = (
    ('created', 'Criado'),
    ('waiting_payment', 'Aguardando Pagamento'),
    ('paid', 'Pago'),
    ('delivered', 'Entregue'),
    ('cancelled', 'Cancelado'),
)

CART_STATUS = (
    ('active', 'Ativo'),
    ('abandoned', 'Abandonado'),
)

AUTH_STATUS = (
    ('valid', 'Válido'),
    ('invalidated', 'Inválido'),
)

PRODUCT_STATUS = (
    ('active', 'Ativo'),
    ('inactive', 'Inativo'),
)

class Store(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    seller = fields.ForeignKeyField("models.Seller", related_name='seller_owner')
    credential = fields.CharField(max_length=255)
    commission_percentage = fields.DecimalField(max_digits=5, decimal_places=2, default=0)  # Ex: 10.50 = 10.5%
    created_at = fields.DatetimeField(auto_now_add=True)

class Seller(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(unique=True, max_length=255)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

class SellerAuth(Model):
    id = fields.IntField(primary_key=True)
    status = fields.CharField(max_length=255, choices=AUTH_STATUS, default='valid')
    seller = fields.ForeignKeyField("models.Seller", related_name='seller_auth')
    access_token = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

class Customer(Model):
    id = fields.IntField(primary_key=True)
    store = fields.ForeignKeyField("models.Store", related_name='store_customer')
    name = fields.CharField(max_length=255)
    email = fields.CharField(unique=True, max_length=255)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

class CustomerAuth(Model):
    id = fields.IntField(primary_key=True)
    status = fields.CharField(max_length=255, choices=AUTH_STATUS, default='valid')
    customer = fields.ForeignKeyField("models.Customer", related_name='customer_auth')
    access_token = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

class Product(Model):
    id = fields.IntField(primary_key=True)
    status = fields.CharField(max_length=255, choices=PRODUCT_STATUS, default='active')
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    price = fields.IntField()
    product_code = fields.TextField() # from maria api
    park_code = fields.TextField() # from maria api
    store = fields.ForeignKeyField("models.Store", related_name='store_product')
    created_at = fields.DatetimeField(auto_now_add=True)


class Cart(Model):
    id = fields.IntField(primary_key=True)
    store = fields.ForeignKeyField("models.Store", related_name='store_cart')
    status = fields.CharField(max_length=255, choices=CART_STATUS, default='active')
    customer = fields.ForeignKeyField("models.Customer", related_name='cart_customer')
    created_at = fields.DatetimeField(auto_now_add=True)

class CartItem(Model):
    id = fields.IntField(primary_key=True)
    cart = fields.ForeignKeyField("models.Cart", related_name='cartitem_cart')
    product = fields.ForeignKeyField("models.Product", related_name='product_cartitem')
    amount = fields.IntField(default=1)
    price = fields.IntField(default=0)  # Price in cents at the time of addition
    attributes = fields.JSONField(default={})  # Stores date, adults, children, etc.
    created_at = fields.DatetimeField(auto_now_add=True)

class Order(Model):
    id = fields.IntField(primary_key=True)
    store = fields.ForeignKeyField("models.Store", related_name='store_order')
    status = fields.CharField(max_length=255, choices=ORDER_STATUS, default='created')
    customer = fields.ForeignKeyField("models.Customer", related_name='order_customer')
    code = fields.CharField(max_length=255)
    
    # Snapshot of customer details
    customer_name = fields.CharField(max_length=255, null=True)
    customer_email = fields.CharField(max_length=255, null=True)
    customer_document = fields.CharField(max_length=255, null=True)
    customer_phone = fields.CharField(max_length=255, null=True)
    
    # Address
    address_street = fields.CharField(max_length=255, null=True)
    address_number = fields.CharField(max_length=255, null=True)
    address_city = fields.CharField(max_length=255, null=True)
    address_state = fields.CharField(max_length=255, null=True)
    address_zip = fields.CharField(max_length=255, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

class OrderItem(Model):
    id = fields.IntField(primary_key=True)
    order = fields.ForeignKeyField("models.Order", related_name='orderitem_order')
    product = fields.ForeignKeyField("models.Product", related_name='product_orderitem')
    price = fields.IntField()
    amount = fields.IntField(default=1)
    attributes = fields.JSONField(default={})  # Snapshot of cart item attributes