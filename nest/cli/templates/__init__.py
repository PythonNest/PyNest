from enum import Enum


class Database(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    CLI = "cli"

    def __str__(self):
        return self.value
