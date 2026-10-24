from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from alembic import context
import sys
from pathlib import Path

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

sys.path.append(str(Path(__file__).parent.parent))


from database import Base
from models import *

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/snaptapbot"

target_metadata = Base.metadata

config = context.config
fileConfig(config.config_file_name)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    url = config.get_main_option("sqlalchemy.url")


    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()