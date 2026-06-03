from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Algoritmo de firma para tokens JWT
ALGORITHM = "HS256"
# Tiempo de expiración del token en minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto de criptografía para bcrypt (hash de contraseñas)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera un hash bcrypt de la contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica que la contraseña en texto plano coincida con el hash almacenado."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """
    Crea un token JWT con los datos proporcionados y fecha de expiración.
    
    Args:
        data: Diccionario con la información a codificar (ej: {"sub": username})
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a decodificar
    
    Returns:
        Payload del token como dict, o None si es inválido/expirado
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None