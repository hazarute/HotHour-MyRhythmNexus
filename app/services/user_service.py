from app.core.db import db
from app.models.user import UserCreate
from app.core import security


def _turkish_lower(text: str) -> str:
    mapping = {
        "I": "ı",
        "İ": "i",
    }
    return "".join(mapping.get(char, char.lower()) for char in text)


def _capitalize_turkish_word(word: str) -> str:
    clean_word = (word or "").strip()
    if not clean_word:
        return clean_word

    lowered = _turkish_lower(clean_word)
    first_char = lowered[0]
    rest = lowered[1:]

    first_upper_map = {
        "i": "İ",
        "ı": "I",
    }
    first_upper = first_upper_map.get(first_char, first_char.upper())
    return first_upper + rest


def _normalize_full_name(full_name: str) -> str:
    parts = (full_name or "").strip().split()
    normalized_parts = []

    for part in parts:
        hyphenated = part.split("-")
        normalized_hyphenated = [_capitalize_turkish_word(piece) for piece in hyphenated if piece]
        normalized_parts.append("-".join(normalized_hyphenated))

    return " ".join(normalized_parts)

class UserService:
    async def create_user(self, user_in: UserCreate):
        hashed_password = security.get_password_hash(user_in.password)
        normalized_full_name = _normalize_full_name(user_in.full_name)
        user = await db.user.create(
            data={
                "email": user_in.email,
                "hashedPassword": hashed_password,
                "fullName": normalized_full_name,
                "phone": user_in.phone,
                "gender": user_in.gender,
            }
        )
        return user

    async def get_user_by_email(self, email: str):
        return await db.user.find_unique(where={"email": email})
    
    async def get_user_by_phone(self, phone: str):
        return await db.user.find_unique(where={"phone": phone})

    async def verify_user(self, email: str):
        return await db.user.update(
            where={"email": email},
            data={"isVerified": True}
        )

    async def update_password(self, user_id: int, new_password: str):
        hashed_password = security.get_password_hash(new_password)
        return await db.user.update(
            where={"id": user_id},
            data={"hashedPassword": hashed_password}
        )
            
user_service = UserService()
