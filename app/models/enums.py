from enum import Enum

class AuctionStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    SOLD = "SOLD"
    CANCELLED = "CANCELLED"

class ReservationStatus(str, Enum):
    PENDING_ON_SITE = "PENDING_ON_SITE"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Gender(str, Enum):
    ANY = "ANY"
    FEMALE = "FEMALE"
    MALE = "MALE"


# Additional shared enums used across models/services
class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# `AllowedGender` is conceptually the same as `Gender` (used for auction eligibility).
# Keeping a distinct name for domain clarity, but reusing the same values avoids duplication.
AllowedGender = Gender


class PaymentStatus(str, Enum):
    PENDING_ON_SITE = "PENDING_ON_SITE"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"
