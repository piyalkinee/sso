from alembic import context
from sqlalchemy import engine_from_config, pool

from source.core.database.postgres import Base
from source.settings import settings

config = context.config

db = settings.postgres
connection_string = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"
config.set_main_option("sqlalchemy.url", connection_string)


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in ["public", "access", "relations", "rights", "users"]
    else:
        return True


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            include_schemas=True,
            include_name=include_name,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
