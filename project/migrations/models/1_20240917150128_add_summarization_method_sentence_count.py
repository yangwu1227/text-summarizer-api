from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "textsummary" ADD "summarization_method" TEXT;
        ALTER TABLE "textsummary" ADD "sentence_count" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "textsummary" DROP COLUMN "summarization_method";
        ALTER TABLE "textsummary" DROP COLUMN "sentence_count";"""
