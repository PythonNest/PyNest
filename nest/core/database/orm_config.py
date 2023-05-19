from abc import abstractmethod


class BaseOrmConfig:

    @abstractmethod
    def get_engine_url(self) -> str:
        pass


class BaseOrmProvider(BaseOrmConfig):

    def __init__(
            self,
            host: str,
            db_name: str,
            user: str,
            password: str,
            port: int
    ):
        self.host = host
        self.db_name = db_name
        self.user = user
        self.password = password
        self.port = port

    def get_engine_url(self) -> str:
        pass


class PostgresConfig(BaseOrmProvider):

    def __init__(
            self,
            host: str,
            db_name: str,
            user: str,
            password: str,
            port: int
    ):
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self):
        return f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'


class MySQLConfig(BaseOrmProvider):

    def __init__(
            self,
            host: str,
            db_name: str,
            user: str,
            password: str,
            port: int
    ):
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self):
        return f'mysql+mysqlconnector://{self.user}:{self.password}@{self.host}'


class SQLiteConfig(BaseOrmConfig):

    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_engine_url(self):
        return f'sqlite:///{self.db_name}.db'


class ConfigFactory:

    def __init__(self, db_type: str):
        self.db_type = db_type

    def get_config(self):
        if self.db_type == "postgresql":
            return PostgresConfig
        elif self.db_type == "mysql":
            return MySQLConfig
        elif self.db_type == "sqlite":
            return SQLiteConfig
        else:
            raise Exception(f"Database type {self.db_type} is not supported")
