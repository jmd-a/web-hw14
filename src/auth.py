from src.database.models import User
from src.security import verify_password
from passlib.context import CryptContext


async def authenticate_user(email: str, password: str):
    user = await User.get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)