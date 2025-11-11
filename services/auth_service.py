from core.db import get_session
from core.models import User, RoleEnum, Base
from utils.security import hash_password, verify_password
from sqlalchemy import select
from core.db import engine

# Initialize tables and a demo admin if empty
def init_db():
    Base.metadata.create_all(bind=engine)
    from contextlib import ExitStack
    with ExitStack() as stack:
        session = stack.enter_context(get_session())
        # Seed an admin and two demo users if none exist
        if not session.execute(select(User)).first():
            session.add_all([
                User(email="selva.ram@enrichenergy.com", name="Admin", role=RoleEnum.ADMIN, password_hash=hash_password("Admin@123")),
                User(email="bess@enrichenergy.com", name="BESS User", role=RoleEnum.BESS, password_hash=hash_password("Bess@123")),
                User(email="epc@enrichenergy.com", name="EPC User", role=RoleEnum.EPC, password_hash=hash_password("Epc@123")),
            ])

def authenticate(email: str, password: str) -> dict | None:
    with get_session() as session:
        stmt = select(User).where(User.email == email)
        user = session.execute(stmt).scalar_one_or_none()
        if user and verify_password(password, user.password_hash):
            return {"id": user.id, "email": user.email, "name": user.name, "role": user.role.value}
    return None

def get_user(user_id: int) -> dict | None:
    with get_session() as session:
        user = session.get(User, user_id)
        if user:
            return {"id": user.id, "email": user.email, "name": user.name, "role": user.role.value}
    return None
