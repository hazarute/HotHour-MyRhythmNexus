"""Booking utility functions for code generation and booking operations."""

import random
import string
from typing import Tuple


def generate_booking_code(prefix: str = "HOT") -> str:
    """
    Generate a unique booking code in format: HOT-XXXX
    
    Example: HOT-8X2A
    
    Args:
        prefix: Prefix for the code (default: "HOT")
    
    Returns:
        Unique booking code string
    """
    # Generate 4 random characters (uppercase letters and digits)
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(4))
    return f"{prefix}-{code}"


def parse_booking_code(code: str) -> Tuple[str, str]:
    """
    Parse a booking code into prefix and suffix.
    
    Args:
        code: Booking code in format "PREFIX-SUFFIX"
    
    Returns:
        Tuple of (prefix, suffix) or (code, "") if format is invalid
    """
    if "-" in code:
        parts = code.split("-", 1)
        return (parts[0], parts[1])
    return (code, "")
