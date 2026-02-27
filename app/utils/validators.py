"""
Auction Validation Utilities

Provides validation rules for auction creation and updates.
Validates pricing, timing, and auction-specific business logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, Union
from app.core.timezone import now_tr, to_tr_aware


class ValidationError(Exception):
    """Custom exception for auction validation errors"""
    pass


class AuctionValidator:
    """Centralized auction validation logic"""

    TURBO_MIN_DURATION_MINS = 180
    TURBO_TRIGGER_MINS_FIXED = 120
    TURBO_INTERVAL_MINS_FIXED = 10

    @staticmethod
    def validate_prices(
        start_price: Union[Decimal, str, int, float],
        floor_price: Union[Decimal, str, int, float],
        drop_amount: Union[Decimal, str, int, float],
        drop_interval_mins: int,
        turbo_enabled: bool = False,
        turbo_drop_amount: Optional[Decimal] = None,
        turbo_interval_mins: Optional[int] = None,
    ) -> None:
        """
        Validate price-related constraints.
        
        Args:
            start_price: Initial auction price
            floor_price: Minimum auction price (floor)
            drop_amount: Amount to drop per interval
            drop_interval_mins: Minutes between normal drops
            turbo_enabled: Whether turbo mode is active
            turbo_drop_amount: Drop amount during turbo mode
            turbo_interval_mins: Turbo interval in minutes
            
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
        if turbo_enabled and turbo_drop_amount is None:
            raise ValidationError("turbo_drop_amount is required when turbo_enabled is true")

        if turbo_enabled and turbo_drop_amount is not None:
            if not isinstance(turbo_drop_amount, Decimal):
                turbo_drop_amount = Decimal(str(turbo_drop_amount))
            
            if turbo_drop_amount <= 0:
                raise ValidationError("turbo_drop_amount must be positive")
            if turbo_drop_amount > price_range:
                raise ValidationError(
                    f"turbo_drop_amount ({turbo_drop_amount}) cannot exceed price range ({price_range})"
                )

            # Turbo should be more frequent (shorter interval) and smaller drop amount than normal mode
            if turbo_interval_mins is None:
                raise ValidationError("turbo_interval_mins is required when turbo_enabled is true")
            if turbo_interval_mins >= drop_interval_mins:
                raise ValidationError(
                    f"turbo_interval_mins ({turbo_interval_mins}) must be less than drop_interval_mins ({drop_interval_mins})"
                )
            if turbo_drop_amount >= drop_amount:
                raise ValidationError(
                    f"turbo_drop_amount ({turbo_drop_amount}) must be less than drop_amount ({drop_amount})"
                )

    @staticmethod
    def validate_timing(
        start_time: datetime,
        end_time: datetime,
        drop_interval_mins: int,
        turbo_enabled: bool = False,
        turbo_trigger_mins: Optional[int] = None,
        turbo_interval_mins: Optional[int] = None,
    ) -> None:
        """
        Validate timing-related constraints.
        
        Args:
            start_time: When auction becomes active
            end_time: When auction expires
            drop_interval_mins: Minutes between price drops
            turbo_enabled: Whether turbo mode is active
            turbo_trigger_mins: Turbo trigger threshold in minutes
            turbo_interval_mins: Turbo mode interval in minutes
            
        Raises:
            ValidationError: If any timing constraint is violated
        """
        # Ensure datetime comparisons are timezone-aware (Turkey)
        now = now_tr()

        # Normalize start/end into Turkey timezone aware datetimes
        start_time_aware = to_tr_aware(start_time)
        end_time_aware = to_tr_aware(end_time)
        if start_time_aware is None or end_time_aware is None:
            raise ValidationError("start_time and end_time are required")
        start_time = start_time_aware
        end_time = end_time_aware

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
        if turbo_enabled:
            if turbo_interval_mins is None:
                raise ValidationError("turbo_interval_mins is required when turbo_enabled is true")
            if turbo_trigger_mins is None:
                raise ValidationError("turbo_trigger_mins is required when turbo_enabled is true")

            if turbo_interval_mins <= 0:
                raise ValidationError("turbo_interval_mins must be positive")
            if turbo_interval_mins >= drop_interval_mins:
                raise ValidationError(
                    f"turbo_interval_mins ({turbo_interval_mins}) must be less than drop_interval_mins ({drop_interval_mins})"
                )

            # Enforce minimum 3-hour auction window for turbo mode
            if auction_duration_mins < AuctionValidator.TURBO_MIN_DURATION_MINS:
                raise ValidationError(
                    f"turbo mode requires at least {AuctionValidator.TURBO_MIN_DURATION_MINS} minutes auction duration"
                )

            # Fixed turbo rule checks
            if turbo_trigger_mins is not None and int(turbo_trigger_mins) != AuctionValidator.TURBO_TRIGGER_MINS_FIXED:
                raise ValidationError(
                    f"turbo_trigger_mins must be fixed at {AuctionValidator.TURBO_TRIGGER_MINS_FIXED}"
                )
            if int(turbo_interval_mins) != AuctionValidator.TURBO_INTERVAL_MINS_FIXED:
                raise ValidationError(
                    f"turbo_interval_mins must be fixed at {AuctionValidator.TURBO_INTERVAL_MINS_FIXED}"
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
            turbo_trigger_mins = data.get("turbo_trigger_mins")
            turbo_drop_amount = data.get("turbo_drop_amount")
            turbo_interval_mins = data.get("turbo_interval_mins")

            # Check required fields
            if start_price is None or floor_price is None:
                return False, "start_price and floor_price are required"
            if start_time is None or end_time is None:
                return False, "start_time and end_time are required"

            # Validate prices
            AuctionValidator.validate_prices(
                start_price, floor_price, drop_amount, drop_interval_mins,
                turbo_enabled, turbo_drop_amount, turbo_interval_mins
            )

            # Validate timing
            AuctionValidator.validate_timing(
                start_time, end_time, drop_interval_mins,
                turbo_enabled, turbo_trigger_mins, turbo_interval_mins
            )

            return True, ""

        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}"


# Singleton instance
auction_validator = AuctionValidator()
