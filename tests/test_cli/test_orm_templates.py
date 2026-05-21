from nest.cli.templates.postgres_template import AsyncPostgresqlTemplate
from nest.cli.templates.mysql_template import AsyncMySQLTemplate, MySQLTemplate
from nest.cli.templates.sqlite_template import SQLiteTemplate


def test_sync_orm_app_template_uses_database_module_for_root():
    template = SQLiteTemplate("book")

    app_file = template.app_file()
    config_file = template.config_file()
    service_file = template.service_file()
    entity_file = template.entity_file()

    assert "from nest.core.database import DatabaseModule" in app_file
    assert "from .config import DATABASE_CONFIG" in app_file
    assert "DatabaseModule.for_root(**DATABASE_CONFIG)" in app_file
    assert "create_all=True" in config_file
    assert "config.create_all" not in app_file
    assert "OrmProvider" not in config_file
    assert "DATABASE_CONFIG = dict(" in config_file
    assert "from nest.core.database import DatabaseService" in service_file
    assert "def __init__(self, db: DatabaseService):" in service_file
    assert "with self.db.session() as session:" in service_file
    assert "from src.config import config" not in service_file
    assert "from nest.core.database import Base" in entity_file


def test_async_orm_template_uses_injected_database_service():
    template = AsyncPostgresqlTemplate("book")

    app_file = template.app_file()
    config_file = template.config_file()
    service_file = template.service_file()
    controller_file = template.controller_file()

    assert "DatabaseModule.for_root(**DATABASE_CONFIG)" in app_file
    assert '"async_mode": True' in config_file
    assert '"create_all": True' in config_file
    assert "AsyncOrmProvider" not in config_file
    assert "from nest.core.database import DatabaseService" in service_file
    assert "def __init__(self, db: DatabaseService):" in service_file
    assert "async with self.db.session() as session:" in service_file
    assert "Depends(config.get_db)" not in controller_file
    assert "AsyncSession" not in controller_file


def test_orm_template_requirements_include_sqlalchemy_runtime():
    sync_requirements = SQLiteTemplate("book").requirements_file()
    async_requirements = AsyncPostgresqlTemplate("book").requirements_file()

    assert "sqlalchemy" in sync_requirements.lower()
    assert "sqlalchemy" in async_requirements.lower()


def test_mysql_orm_templates_default_missing_port_environment_variables():
    sync_config = MySQLTemplate("book").config_file()
    async_config = AsyncMySQLTemplate("book").config_file()

    assert 'os.getenv("MYSQL_PORT", 3306)' in sync_config
    assert 'os.getenv("MYSQL_PORT", 3306)' in async_config
