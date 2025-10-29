from tortoise.models import Model
from tortoise import fields


ORDER_STATUS = (
    ('created', 'Criado'),
    ('waiting_payment', 'Aguardando Pagamento'),
    ('paid', 'Pago'),
    ('delivered', 'Entregue'),
    ('cancelled', 'Cancelado'),
)

AUTH_STATUS = (
    ('valid', 'Válido'),
    ('invalidated', 'Inválido'),
)
class Store(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    seller = fields.ForeignKeyField("models.Seller", related_name='seller_owner')
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
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    price = fields.IntField()
    external_id = fields.TextField() # from maria api
    store = fields.ForeignKeyField("models.Store", related_name='store_product')
    created_at = fields.DatetimeField(auto_now_add=True)

class Order(Model):
    id = fields.IntField(primary_key=True)
    status = fields.CharField(max_length=255, choices=ORDER_STATUS, default='created')
    created_at = fields.DatetimeField(auto_now_add=True)

class OrderItem(Model):
    id = fields.IntField(primary_key=True)
    order = fields.ForeignKeyField("models.Order", related_name='orderitem_order')
    product = fields.ForeignKeyField("models.Order", related_name='product_order')
    price = fields.IntField()
    amount = fields.IntField(default=1)