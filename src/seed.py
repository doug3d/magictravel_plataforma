"""
Script de inicialização do banco de dados.
Cria dados iniciais se não existirem.
"""
import uuid
from src.models import Seller, SellerAuth, Store
from tortoise.exceptions import DoesNotExist


async def seed_database():
    """
    Cria seller admin e loja padrão se não existirem.
    """
    
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
        print(f"  Email: {admin_email}")
        print(f"  Senha: {admin_password}")
        
        # Criar token de autenticação para o admin
        access_token = str(uuid.uuid4())
        await SellerAuth.create(
            seller=admin_seller,
            access_token=access_token,
            status='valid'
        )
        print(f"  Token: {access_token}")
    
    # Criar loja padrão se não existir
    store_name = "Magic Marketplace"
    
    try:
        store = await Store.get(seller=admin_seller, name=store_name)
        print(f"✓ Loja '{store_name}' já existe (ID: {store.id})")
        print(f"  Credential: {store.credential}")
    except DoesNotExist:
        store_credential = str(uuid.uuid4().hex)[:250]
        store = await Store.create(
            seller=admin_seller,
            name=store_name,
            credential=store_credential
        )
        print(f"✓ Loja '{store_name}' criada (ID: {store.id})")
        print(f"  Credential: {store_credential}")
    
    print("\n" + "="*50)
    print("🚀 Banco de dados inicializado com sucesso!")
    print("="*50)
    print("\n📝 Credenciais para desenvolvimento:\n")
    print(f"Seller Admin:")
    print(f"  Email: {admin_email}")
    print(f"  Senha: {admin_password}")
    print(f"\nStore:")
    print(f"  Nome: {store_name}")
    print(f"  Credential: {store.credential}")
    print("\n" + "="*50 + "\n")

