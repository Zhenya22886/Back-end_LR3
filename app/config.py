import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

DB_USER = os.environ.get("POSTGRES_USER", "expenses_user")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "expenses_password")
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "expenses_db")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
