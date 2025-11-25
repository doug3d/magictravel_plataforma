from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "seller" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "sellerauth" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(255) NOT NULL DEFAULT 'valid',
    "access_token" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "seller_id" INT NOT NULL REFERENCES "seller" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "store" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "credential" VARCHAR(255) NOT NULL,
    "commission_percentage" VARCHAR(40) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "seller_id" INT NOT NULL REFERENCES "seller" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "customer" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "store_id" INT NOT NULL REFERENCES "store" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cart" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(255) NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE,
    "store_id" INT NOT NULL REFERENCES "store" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "customerauth" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(255) NOT NULL DEFAULT 'valid',
    "access_token" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "order" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(255) NOT NULL DEFAULT 'created',
    "code" VARCHAR(255) NOT NULL,
    "customer_name" VARCHAR(255),
    "customer_email" VARCHAR(255),
    "customer_document" VARCHAR(255),
    "customer_phone" VARCHAR(255),
    "address_street" VARCHAR(255),
    "address_number" VARCHAR(255),
    "address_city" VARCHAR(255),
    "address_state" VARCHAR(255),
    "address_zip" VARCHAR(255),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE,
    "store_id" INT NOT NULL REFERENCES "store" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "product" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(255) NOT NULL DEFAULT 'active',
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "price" INT NOT NULL,
    "product_code" TEXT NOT NULL,
    "park_code" TEXT NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "store_id" INT NOT NULL REFERENCES "store" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cartitem" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "amount" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "cart_id" INT NOT NULL REFERENCES "cart" ("id") ON DELETE CASCADE,
    "product_id" INT NOT NULL REFERENCES "product" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "orderitem" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "price" INT NOT NULL,
    "amount" INT NOT NULL DEFAULT 1,
    "order_id" INT NOT NULL REFERENCES "order" ("id") ON DELETE CASCADE,
    "product_id" INT NOT NULL REFERENCES "product" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
