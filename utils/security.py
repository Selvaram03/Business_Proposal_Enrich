from passlib.context import CryptContext

# Password hashing (Argon2 -> no 72-byte limit, modern & safe)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Return a secure hash for the given plaintext password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ----- Simple RBAC guard for template access -----
def can_use_template(user_role: str, template_choice: str) -> bool:
    """
    Allow if:
      - user is ADMIN, or
      - the first word of the template name (e.g., 'EPC Template' -> 'EPC')
        matches the user's role.
    """
    if not user_role or not template_choice:
        return False

    user_role = user_role.strip().upper()
    template_role = template_choice.strip().upper().split()[0]  # "EPC Template" -> "EPC"

    if user_role == "ADMIN":
        return True
    return user_role == template_role

__all__ = ["hash_password", "verify_password", "can_use_template"]
