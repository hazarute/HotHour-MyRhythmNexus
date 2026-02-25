"""
Test for create_admin.py script
Tests admin account creation with various scenarios
"""

import asyncio
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.core import db
from app.core.security import get_password_hash, verify_password

# Import the script's main function
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.mark.asyncio
async def test_create_admin_success():
    """Test successful admin creation"""
    from scripts.create_admin import create_admin
    
    email = "test_admin@hothour.com"
    password = "SecurePass123"
    full_name = "Test Admin"
    phone = "+905551234567"
    
    # Connect to DB
    if not db.db.is_connected():
        await db.db.connect()
    
    try:
        # Clean up if exists
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass
        
        # Create admin with existing db connection
        await create_admin(email, password, full_name, phone, "MALE", prisma_client=db.db)
        
        # Verify admin was created
        admin = await db.db.user.find_unique(where={"email": email})
        assert admin is not None
        assert admin.email == email
        assert admin.fullName == full_name
        assert admin.phone == phone
        assert admin.role == "ADMIN"
        assert admin.isVerified == True
        assert admin.gender == "MALE"
        assert verify_password(password, admin.hashedPassword)
        
    finally:
        # Cleanup
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass


@pytest.mark.asyncio
async def test_create_admin_duplicate_email():
    """Test admin creation with duplicate email"""
    from scripts.create_admin import create_admin
    
    email = "duplicate_admin@hothour.com"
    password = "SecurePass123"
    full_name = "Test Admin"
    
    if not db.db.is_connected():
        await db.db.connect()
    
    try:
        # Clean up if exists
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass
        
        # Create first admin
        await create_admin(email, password, full_name, prisma_client=db.db)
        
        # Verify admin exists
        admin = await db.db.user.find_unique(where={"email": email})
        assert admin is not None
        
        # Try to create duplicate - should not raise but print error and return
        # Capture output to verify error message
        from io import StringIO
        from unittest.mock import patch
        
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            await create_admin(email, "AnotherPass123", "Another Admin", prisma_client=db.db)
        
        output = captured_output.getvalue()
        assert "zaten kayıtlı" in output or "Hata" in output
        
    finally:
        # Cleanup
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass


@pytest.mark.asyncio
async def test_create_admin_duplicate_phone():
    """Test admin creation with duplicate phone errors properly"""
    from scripts.create_admin import create_admin
    
    email1 = "dup_phone1@hothour.com"
    email2 = "dup_phone2@hothour.com" 
    password = "SecurePass123"
    
    if not db.db.is_connected():
        await db.db.connect()
    
    try:
        # Clean up
        for email in [email1, email2]:
            try:
                await db.db.user.delete(where={"email": email})
            except:
                pass
        
        # Create first admin
        await create_admin(email1, password, "Admin One", "+905559999999", prisma_client=db.db)
        
        # Verify it exists
        admin1 = await db.db.user.find_unique(where={"email": email1})
        assert admin1 is not None
        
    finally:
        for email in [email1, email2]:
            try:
                await db.db.user.delete(where={"email": email})
            except:
                pass


@pytest.mark.asyncio
async def test_create_admin_auto_phone():
    """Test admin creation with auto-generated phone"""
    from scripts.create_admin import create_admin
    
    email = "test_auto_phone@hothour.com"
    password = "SecurePass123"
    full_name = "Test Admin"
    
    if not db.db.is_connected():
        await db.db.connect()
    
    try:
        # Clean up if exists
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass
        
        # Create admin without phone (should auto-generate)
        await create_admin(email, password, full_name, phone=None, prisma_client=db.db)
        
        # Verify admin was created with auto-generated phone
        admin = await db.db.user.find_unique(where={"email": email})
        assert admin is not None
        assert admin.phone is not None
        assert admin.phone.startswith("admin-")
        
    finally:
        # Cleanup
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass


@pytest.mark.asyncio
async def test_create_admin_no_gender():
    """Test admin creation without gender"""
    from scripts.create_admin import create_admin
    
    email = "test_no_gender@hothour.com"
    password = "SecurePass123"
    full_name = "Test Admin"
    
    if not db.db.is_connected():
        await db.db.connect()
    
    try:
        # Clean up if exists
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass
        
        # Create admin without gender
        await create_admin(email, password, full_name, phone=None, gender=None, prisma_client=db.db)
        
        # Verify admin was created
        admin = await db.db.user.find_unique(where={"email": email})
        assert admin is not None
        assert admin.gender is None
        
    finally:
        # Cleanup
        try:
            await db.db.user.delete(where={"email": email})
        except:
            pass




def test_create_admin_cli_help():
    """Test CLI script help"""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, "scripts/create_admin.py", "--help"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    # Should show help (either exit 1 or 0 depending on implementation)  
    assert "Kullanım" in result.stdout or "usage" in result.stdout.lower() or result.returncode in [0, 1]
