from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings  # centralized environment configuration

# Alembic Config object - provides access to values in alembic.ini
config = context.config

# Inject DATABASE_URL from centralized settings into Alembic config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _load_app_models():
    """
    Import Base and all models inside a function to ensure load_dotenv()
    and DATABASE_URL injection run first.

    Importing app.database triggers the SQLAlchemy engine creation, which
    reads DATABASE_URL. If this import happens at module level, it runs
    before load_dotenv() and the URL is not yet available.

    The noqa: F401 comment suppresses the 'imported but unused' warning
    for app.models - this import is intentional, it registers all model
    classes into Base.metadata so Alembic can detect them for autogenerate.
    """
    from app.database import Base
    import app.models  # noqa: F401
    return Base.metadata


target_metadata = _load_app_models()


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    Configures the context with just a URL, without creating an Engine.
    Useful for generating SQL scripts without a live database connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    Creates an Engine and associates a connection with the Alembic context.
    This is the standard mode used during development.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
