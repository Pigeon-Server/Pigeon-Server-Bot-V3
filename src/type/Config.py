class Config:
    class DatabaseConfig:
        host: str
        password: str
        username: str
        database_name: str
        port: int
        auto_commit: bool

    database: DatabaseConfig
