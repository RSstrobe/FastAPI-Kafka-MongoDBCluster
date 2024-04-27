from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from tests.functional.core.settings import test_settings

pg_url = str(test_settings.database_url_psycopg)
engine = create_engine(pg_url)
async_factory = sessionmaker(engine)


def drop_all_tables():
    with async_factory() as sqlalchemy_sync_session:
        sqlalchemy_sync_session.execute(
            text(
                """
                        drop table if exists alembic_version, auth_history,
                         mix_actions, actions, users, roles, user_data cascade;
                """
            )
        )
        sqlalchemy_sync_session.commit()
