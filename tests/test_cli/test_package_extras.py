from pathlib import Path


def test_pyproject_defines_granular_generation_extras():
    pyproject = Path("pyproject.toml").read_text()

    for extra in (
        "http",
        "cli",
        "sqlite",
        "sqlite-async",
        "postgresql",
        "postgresql-async",
        "mysql",
        "mysql-async",
        "mongodb",
    ):
        assert f"{extra} = [" in pyproject

    for dependency in (
        '"sqlalchemy>=2.0.36,<3.0.0"',
        '"aiosqlite>=0.19.0,<1.0.0"',
        '"asyncpg>=0.30.0,<0.31.0"',
        '"mysql-connector-python==8.2.0"',
        '"aiomysql==0.2.0"',
        '"beanie>=1.27.0,<2.0.0"',
        '"python-dotenv>=1.0.1,<2.0.0"',
    ):
        assert dependency in pyproject
