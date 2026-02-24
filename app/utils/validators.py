"""
Auction Validation Utilities

Provides validation rules for auction creation and updates.
Validates pricing, timing, and auction-specific business logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Tuple


class ValidationError(Exception):
    """Custom exception for auction validation errors"""
    pass


class AuctionValidator:
    """Centralized auction validation logic"""

    @staticmethod
    def validate_prices(
        start_price: Decimal,
        floor_price: Decimal,
        drop_amount: Decimal,
        turbo_enabled: bool = False,
        turbo_drop_amount: Decimal = None,
    ) -> None:
        """
        Validate price-related constraints.
        
        Args:
            start_price: Initial auction price
            floor_price: Minimum auction price (floor)
            drop_amount: Amount to drop per interval
            turbo_enabled: Whether turbo mode is active
            turbo_drop_amount: Drop amount during turbo mode
            
        Raises:
            ValidationError: If any price constraint is violated
        """
        # Convert to Decimal if needed
        if not isinstance(start_price, Decimal):
            start_price = Decimal(str(start_price))
        if not isinstance(floor_price, Decimal):
            floor_price = Decimal(str(floor_price))
        if not isinstance(drop_amount, Decimal):
            drop_amount = Decimal(str(drop_amount))

        # Rule 1: All prices must be positive (check first)
        if start_price <= 0:
            raise ValidationError("start_price must be positive")
        if floor_price <= 0:
            raise ValidationError("floor_price must be positive")
        if drop_amount <= 0:
            raise ValidationError("drop_amount must be positive")

        # Rule 2: Start price must be greater than floor price
        if start_price <= floor_price:
            raise ValidationError(
                f"start_price ({start_price}) must be greater than floor_price ({floor_price})"
            )

        # Rule 3: Drop amount should not exceed price range
        # (Price range = start_price - floor_price)
        price_range = start_price - floor_price
        if drop_amount > price_range:
            raise ValidationError(
                f"drop_amount ({drop_amount}) cannot exceed price range ({price_range})"
            )

        # Rule 4: Turbo mode validations
        if turbo_enabled and turbo_drop_amount is not None:
            if not isinstance(turbo_drop_amount, Decimal):
                turbo_drop_amount = Decimal(str(turbo_drop_amount))
            
            if turbo_drop_amount <= 0:
                raise ValidationError("turbo_drop_amount must be positive")
            if turbo_drop_amount > price_range:
                raise ValidationError(
                    f"turbo_drop_amount ({turbo_drop_amount}) cannot exceed price range ({price_range})"
                )

    @staticmethod
    def validate_timing(
        start_time: datetime,
        end_time: datetime,
        drop_interval_mins: int,
        turbo_enabled: bool = False,
        turbo_interval_mins: int = None,
    ) -> None:
        """
        Validate timing-related constraints.
        
        Args:
            start_time: When auction becomes active
            end_time: When auction expires
            drop_interval_mins: Minutes between price drops
            turbo_enabled: Whether turbo mode is active
            turbo_interval_mins: Turbo mode interval in minutes
            
        Raises:
            ValidationError: If any timing constraint is violated
        """
        now = datetime.utcnow()

        # Rule 1: Start time must be before end time
        if start_time >= end_time:
            raise ValidationError(
                f"start_time ({start_time}) must be before end_time ({end_time})"
            )

        # Rule 2: End time must be in the future
        # Allow some tolerance (5 minutes) for immediate auctions
        if end_time < now:
            raise ValidationError(
                f"end_time ({end_time}) must be in the future (now: {now})"
            )

        # Rule 3: Drop interval must be positive
        if drop_interval_mins <= 0:
            raise ValidationError("drop_interval_mins must be positive")

        # Rule 4: Drop interval must not exceed total auction duration
        auction_duration_mins = int((end_time - start_time).total_seconds() / 60)
        if drop_interval_mins > auction_duration_mins:
            raise ValidationError(
                f"drop_interval_mins ({drop_interval_mins}) cannot exceed "
                f"auction duration ({auction_duration_mins} minutes)"
            )

        # Rule 5: Turbo mode validations
        if turbo_enabled and turbo_interval_mins is not None:
            if turbo_interval_mins <= 0:
                raise ValidationError("turbo_interval_mins must be positive")
            if turbo_interval_mins > drop_interval_mins:
                raise ValidationError(
                    f"turbo_interval_mins ({turbo_interval_mins}) must be less than or equal to "
                    f"drop_interval_mins ({drop_interval_mins})"
                )

    @staticmethod
    def validate_auction_create(data: dict) -> Tuple[bool, str]:
        """
        Main validation entry point for auction creation.
        
        Args:
            data: Dictionary containing auction creation data
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Extract required fields
            start_price = data.get("start_price")
            floor_price = data.get("floor_price")
            drop_amount = data.get("drop_amount", Decimal("0"))
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            drop_interval_mins = data.get("drop_interval_mins", 60)
            turbo_enabled = data.get("turbo_enabled", False)
            turbo_drop_amount = data.get("turbo_drop_amount")
            turbo_interval_mins = data.get("turbo_interval_mins")

            # Check required fields
            if start_price is None or floor_price is None:
                return False, "start_price and floor_price are required"
            if start_time is None or end_time is None:
                return False, "start_time and end_time are required"

            # Validate prices
            AuctionValidator.validate_prices(
                start_price, floor_price, drop_amount,
                turbo_enabled, turbo_drop_amount
            )

            # Validate timing
            AuctionValidator.validate_timing(
                start_time, end_time, drop_interval_mins,
                turbo_enabled, turbo_interval_mins
            )

            return True, ""

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}"


# Singleton instance
auction_validator = AuctionValidator()
