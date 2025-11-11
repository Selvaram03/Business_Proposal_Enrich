from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "Techno-Commercial Proposal Auto Generator"
    secret_key: str = os.getenv("APP_SECRET_KEY", "change-me")
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")

    # Must be mysql+pymysql://
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://proposal_user:proposal_pass@localhost:3306/proposal_db",
    )

    # TLS flags
    mysql_ssl_enabled: bool = os.getenv("MYSQL_SSL_ENABLED", "false").lower() == "true"
    mysql_ssl_ca_pem: str | None = os.getenv("MYSQL_SSL_CA_PEM")

    local_backup_dir: str = os.getenv("LOCAL_BACKUP_DIR", "backups")

    roles: tuple[str, ...] = ("BESS", "EPC", "ADMIN")

    @property
    def is_cloud(self) -> bool:
        # Streamlit Cloud sets this env
        return os.getenv("STREAMLIT_RUNTIME", "") == "1"

settings = Settings()
