from datetime import datetime
from core.mongo import get_db
from utils.security import hash_password, verify_password

db = get_db()

# -----------------------------------------------------------
# Initialize MongoDB Users (Seed Only Once)
# -----------------------------------------------------------
def init_db():
    """
    Seed default users if users collection is empty.
    Safe to run multiple times.
    """
    if db.users.count_documents({}) == 0:
        db.users.insert_many([
            {
                "email": "selva.ram@enrichenergy.com",
                "name": "Admin",
                "role": "ADMIN",
                "password_hash": hash_password("Admin@123"),
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "email": "bess@enrichenergy.com",
                "name": "BESS User",
                "role": "BESS",
                "password_hash": hash_password("Bess@123"),
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "email": "epc@enrichenergy.com",
                "name": "EPC User",
                "role": "EPC",
                "password_hash": hash_password("Epc@123"),
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ])

# -----------------------------------------------------------
# Authenticate User
# -----------------------------------------------------------
def authenticate(email: str, password: str) -> dict | None:
    user = db.users.find_one(
        {"email": email, "is_active": True},
        {"_id": 1, "email": 1, "name": 1, "role": 1, "password_hash": 1}
    )

    if user and verify_password(password, user["password_hash"]):
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }

    return None

# -----------------------------------------------------------
# Get User by ID
# -----------------------------------------------------------
def get_user(user_id: str) -> dict | None:
    user = db.users.find_one(
        {"_id": user_id},
        {"_id": 1, "email": 1, "name": 1, "role": 1}
    )

    if user:
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }

    return None
