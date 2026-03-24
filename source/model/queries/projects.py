from uuid import UUID

from loguru import logger
from asyncpg import PostgresError
from databases.core import Connection

from ...exceptions.database import DatabaseError


async def exists(database: Connection, project_id: UUID) -> bool:
    try:
        row = await database.fetch_one(
            "SELECT id FROM projects.projects WHERE id = :project_id",
            {"project_id": str(project_id)}
        )
        return row is not None
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e


async def get_user_project_names(database: Connection, user_id: int) -> list[str]:
    try:
        rows = await database.fetch_all("""
            SELECT p.name
            FROM relations.user_projects up
            JOIN projects.projects p ON p.id = up.project_id
            WHERE up.user_id = :user_id
        """, {"user_id": user_id})
        return [row["name"] for row in rows]
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e


async def link_user(database: Connection, user_id: int, project_id: UUID) -> None:
    try:
        await database.execute("""
            INSERT INTO relations.user_projects (user_id, project_id)
            VALUES (:user_id, :project_id)
            ON CONFLICT DO NOTHING
        """, {"user_id": user_id, "project_id": str(project_id)})
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e
