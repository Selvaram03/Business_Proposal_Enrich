from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "Techno-Commercial Proposal Auto Generator"
    secret_key: str = os.getenv("APP_SECRET_KEY", "change-me")
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")

    # Database: MySQL DSN -> mysql+pymysql://USER:PASS@HOST:PORT/DBNAME
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:Karthi123@localhost:3306/proposal_db",
    )

    # Storage (local backups only)
    local_backup_dir: str = os.getenv("LOCAL_BACKUP_DIR", "backups")

    # RBAC roles
    roles: tuple[str, ...] = ("BESS", "EPC", "ADMIN")

settings = Settings()
