from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "product" RENAME COLUMN "external_id" TO "product_code";
        ALTER TABLE "product" ADD "park_code" TEXT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "product" RENAME COLUMN "product_code" TO "external_id";
        ALTER TABLE "product" DROP COLUMN "park_code";"""


MODELS_STATE = (
    "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"
    "7VHRVOIVHOkk/Dadeo8/AWlh7w4="
)
