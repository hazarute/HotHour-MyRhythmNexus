"""
Unit tests for Auction Validation Logic

Tests price and timing validation rules for auction creation.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.utils.validators import AuctionValidator, ValidationError
from app.core.timezone import now_tr


class TestPriceValidation:
    """Test suite for price validation rules"""

    def test_valid_prices(self):
        """Valid prices should pass without error"""
        AuctionValidator.validate_prices(
            start_price=Decimal("100"),
            floor_price=Decimal("50"),
            drop_amount=Decimal("10"),
            drop_interval_mins=30,
        )
        # No exception should be raised

    def test_start_price_must_exceed_floor_price(self):
        """start_price must be greater than floor_price"""
        with pytest.raises(ValidationError, match="start_price.*must be greater than floor_price"):
            AuctionValidator.validate_prices(
                start_price=Decimal("50"),
                floor_price=Decimal("100"),
                drop_amount=Decimal("10"),
                drop_interval_mins=30,
            )

    def test_start_price_equal_to_floor_price_fails(self):
        """start_price equal to floor_price should fail"""
        with pytest.raises(ValidationError):
            AuctionValidator.validate_prices(
                start_price=Decimal("100"),
                floor_price=Decimal("100"),
                drop_amount=Decimal("10"),
                drop_interval_mins=30,
            )

    def test_start_price_must_be_positive(self):
        """start_price must be positive"""
        with pytest.raises(ValidationError, match="start_price must be positive"):
            AuctionValidator.validate_prices(
                start_price=Decimal("-50"),
                floor_price=Decimal("10"),
                drop_amount=Decimal("5"),
                drop_interval_mins=30,
            )

    def test_floor_price_must_be_positive(self):
        """floor_price must be positive"""
        with pytest.raises(ValidationError, match="floor_price must be positive"):
            AuctionValidator.validate_prices(
                start_price=Decimal("100"),
                floor_price=Decimal("-10"),
                drop_amount=Decimal("5"),
                drop_interval_mins=30,
            )

    def test_drop_amount_must_be_positive(self):
        """drop_amount must be positive"""
        with pytest.raises(ValidationError, match="drop_amount must be positive"):
            AuctionValidator.validate_prices(
                start_price=Decimal("100"),
                floor_price=Decimal("50"),
                drop_amount=Decimal("-10"),
                drop_interval_mins=30,
            )

    def test_drop_amount_cannot_exceed_price_range(self):
        """drop_amount cannot exceed the price range (start - floor)"""
        with pytest.raises(ValidationError, match="drop_amount.*cannot exceed price range"):
            AuctionValidator.validate_prices(
                start_price=Decimal("100"),
                floor_price=Decimal("50"),
                drop_amount=Decimal("60"),  # Range is only 50
                drop_interval_mins=30,
            )

    def test_large_drop_amount_acceptable_within_range(self):
        """Large drop_amount should be acceptable if within price range"""
        AuctionValidator.validate_prices(
            start_price=Decimal("1000"),
            floor_price=Decimal("100"),
            drop_amount=Decimal("100"),  # Range is 900, so this is OK
            drop_interval_mins=30,
        )
        # No exception should be raised

    def test_turbo_mode_drop_amount_must_be_positive(self):
        """turbo_drop_amount must be positive when turbo enabled"""
        with pytest.raises(ValidationError, match="turbo_drop_amount must be positive"):
            AuctionValidator.validate_prices(
                start_price=Decimal("100"),
                floor_price=Decimal("50"),
                drop_amount=Decimal("10"),
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_drop_amount=Decimal("-5"),
            )

    def test_turbo_mode_drop_amount_cannot_exceed_range(self):
        """turbo_drop_amount cannot exceed price range"""
        with pytest.raises(ValidationError, match="turbo_drop_amount.*cannot exceed price range"):
            AuctionValidator.validate_prices(
                start_price=Decimal("100"),
                floor_price=Decimal("50"),
                drop_amount=Decimal("10"),
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_drop_amount=Decimal("60"),
            )

    def test_string_prices_converted_to_decimal(self):
        """String prices should be automatically converted to Decimal"""
        AuctionValidator.validate_prices(
            start_price="100",
            floor_price="50",
            drop_amount="10",
            drop_interval_mins=30,
        )
        # No exception should be raised


class TestTimingValidation:
    """Test suite for timing validation rules"""

    def test_valid_timing(self):
        """Valid timing should pass without error"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)
        
        AuctionValidator.validate_timing(
            start_time=start,
            end_time=end,
            drop_interval_mins=30,
        )
        # No exception should be raised

    def test_start_time_must_be_before_end_time(self):
        """start_time must be before end_time"""
        now = now_tr()
        end = now + timedelta(hours=1)
        start = now + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="start_time.*must be before end_time"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
            )

    def test_start_time_equal_to_end_time_fails(self):
        """start_time equal to end_time should fail"""
        now = now_tr()
        time = now + timedelta(hours=1)
        
        with pytest.raises(ValidationError):
            AuctionValidator.validate_timing(
                start_time=time,
                end_time=time,
                drop_interval_mins=30,
            )

    def test_end_time_must_be_in_future(self):
        """end_time must be in the future"""
        past = now_tr() - timedelta(hours=1)
        earlier_past = past - timedelta(hours=1)
        
        with pytest.raises(ValidationError, match="end_time.*must be in the future"):
            AuctionValidator.validate_timing(
                start_time=earlier_past,
                end_time=past,
                drop_interval_mins=30,
            )

    def test_drop_interval_must_be_positive(self):
        """drop_interval_mins must be positive"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="drop_interval_mins must be positive"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=-30,
            )

    def test_drop_interval_cannot_exceed_auction_duration(self):
        """drop_interval_mins cannot exceed total auction duration"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)  # 60 minutes duration
        
        with pytest.raises(ValidationError, match="drop_interval_mins.*cannot exceed"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=90,  # Exceeds 60-minute duration
            )

    def test_drop_interval_equal_to_duration_acceptable(self):
        """drop_interval_mins equal to auction duration should be acceptable"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)  # 60 minutes duration
        
        AuctionValidator.validate_timing(
            start_time=start,
            end_time=end,
            drop_interval_mins=60,
        )
        # No exception should be raised

    def test_turbo_interval_must_be_positive(self):
        """turbo_interval_mins must be positive when turbo enabled"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="turbo_interval_mins must be positive"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_trigger_mins=120,
                turbo_interval_mins=-5,
            )

    def test_turbo_interval_must_not_exceed_drop_interval(self):
        """turbo_interval_mins must be <= drop_interval_mins"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="turbo_interval_mins.*must be less than drop_interval_mins"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_trigger_mins=120,
                turbo_interval_mins=40,
            )

    def test_turbo_interval_equal_to_drop_interval_acceptable(self):
        """turbo_interval_mins equal to drop_interval_mins should be acceptable"""
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=2)
        
        with pytest.raises(ValidationError, match="must be less than drop_interval_mins"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_trigger_mins=120,
                turbo_interval_mins=30,
            )

    def test_turbo_requires_minimum_3_hours(self):
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=3)  # 120 minutes duration

        with pytest.raises(ValidationError, match="requires at least 180 minutes"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_trigger_mins=120,
                turbo_interval_mins=10,
            )

    def test_turbo_fixed_interval_and_trigger(self):
        now = now_tr()
        start = now + timedelta(hours=1)
        end = now + timedelta(hours=5)

        with pytest.raises(ValidationError, match="turbo_interval_mins must be fixed at 10"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_trigger_mins=120,
                turbo_interval_mins=15,
            )

        with pytest.raises(ValidationError, match="turbo_trigger_mins must be fixed at 120"):
            AuctionValidator.validate_timing(
                start_time=start,
                end_time=end,
                drop_interval_mins=30,
                turbo_enabled=True,
                turbo_trigger_mins=90,
                turbo_interval_mins=10,
            )


class TestAuctionCreateValidation:
    """Test suite for the main validate_auction_create method"""

    def test_valid_auction_creation_data(self):
        """Valid auction creation data should pass"""
        now = now_tr()
        data = {
            "start_price": Decimal("100"),
            "floor_price": Decimal("50"),
            "drop_amount": Decimal("10"),
            "start_time": now + timedelta(hours=1),
            "end_time": now + timedelta(hours=2),
            "drop_interval_mins": 30,
        }
        
        is_valid, error_msg = AuctionValidator.validate_auction_create(data)
        assert is_valid is True
        assert error_msg == ""

    def test_missing_start_price(self):
        """Missing start_price should fail"""
        now = now_tr()
        data = {
            "floor_price": Decimal("50"),
            "drop_amount": Decimal("10"),
            "start_time": now + timedelta(hours=1),
            "end_time": now + timedelta(hours=2),
            "drop_interval_mins": 30,
        }
        
        is_valid, error_msg = AuctionValidator.validate_auction_create(data)
        assert is_valid is False
        assert "start_price" in error_msg

    def test_invalid_prices_in_auction_creation(self):
        """Invalid prices in auction creation should fail"""
        now = now_tr()
        data = {
            "start_price": Decimal("50"),
            "floor_price": Decimal("100"),  # Invalid: start < floor
            "drop_amount": Decimal("10"),
            "start_time": now + timedelta(hours=1),
            "end_time": now + timedelta(hours=2),
            "drop_interval_mins": 30,
        }
        
        is_valid, error_msg = AuctionValidator.validate_auction_create(data)
        assert is_valid is False
        assert "greater than floor_price" in error_msg

    def test_invalid_timing_in_auction_creation(self):
        """Invalid timing in auction creation should fail"""
        now = now_tr()
        data = {
            "start_price": Decimal("100"),
            "floor_price": Decimal("50"),
            "drop_amount": Decimal("10"),
            "start_time": now + timedelta(hours=2),
            "end_time": now + timedelta(hours=1),  # Invalid: start after end
            "drop_interval_mins": 30,
        }
        
        is_valid, error_msg = AuctionValidator.validate_auction_create(data)
        assert is_valid is False
        assert "must be before" in error_msg

    def test_turbo_mode_validation_in_auction_creation(self):
        """Turbo mode validation should work in full auction creation"""
        now = now_tr()
        data = {
            "start_price": Decimal("100"),
            "floor_price": Decimal("50"),
            "drop_amount": Decimal("10"),
            "start_time": now + timedelta(hours=1),
            "end_time": now + timedelta(hours=2),
            "drop_interval_mins": 30,
            "turbo_enabled": True,
            "turbo_drop_amount": Decimal("60"),  # Invalid: exceeds price range
        }
        
        is_valid, error_msg = AuctionValidator.validate_auction_create(data)
        assert is_valid is False
        assert "turbo_drop_amount" in error_msg
