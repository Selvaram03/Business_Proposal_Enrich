from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import settings
import tempfile, os
from urllib.parse import urlparse

def _connect_args():
    args = {}
    if settings.mysql_ssl_enabled:
        ssl_dict = {}
        if settings.mysql_ssl_ca_pem:
            ca_path = os.path.join(tempfile.gettempdir(), "mysql_ca.pem")
            if not os.path.exists(ca_path):
                with open(ca_path, "w", encoding="utf-8") as f:
                    f.write(settings.mysql_ssl_ca_pem)
            ssl_dict = {"ca": ca_path}
        args["ssl"] = ssl_dict if ssl_dict else {"_enable_tls": True}
    return args

# Guard: block localhost in Cloud to avoid confusing failures
parsed = urlparse(settings.database_url.replace("+pymysql", ""))  # crude parse
host = (parsed.hostname or "").lower()
if settings.is_cloud and host in {"localhost", "127.0.0.1"}:
    raise RuntimeError(
        "DATABASE_URL points to localhost on Streamlit Cloud. "
        "Use a public MySQL host (RDS/PlanetScale/etc.)."
    )

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=_connect_args(),
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

from contextlib import contextmanager
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
