from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "admin123"

hash_password = pwd_context.hash(password)

print(hash_password)