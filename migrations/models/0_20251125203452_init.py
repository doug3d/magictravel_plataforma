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
    "price" INT NOT NULL DEFAULT 0,
    "attributes" JSON NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "cart_id" INT NOT NULL REFERENCES "cart" ("id") ON DELETE CASCADE,
    "product_id" INT NOT NULL REFERENCES "product" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "orderitem" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "price" INT NOT NULL,
    "amount" INT NOT NULL DEFAULT 1,
    "attributes" JSON NOT NULL,
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
