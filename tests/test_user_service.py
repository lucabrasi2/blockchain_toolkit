#!/usr/bin/env python3
"""
Test the User Service.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService


def test_user_service():
    """Test User Service functionality."""
    service = UserService()

    # Test user creation
    print("Creating user...")
    user = service.create_user("testuser", "test@example.com", "password123")
    if user:
        print(f"✅ User created: {user.username} ({user.id})")
    else:
        print("❌ User creation failed")
        return False

    # Test authentication
    print("Testing authentication...")
    auth_user = service.authenticate("testuser", "password123")
    if auth_user:
        print(f"✅ User authenticated: {auth_user.username}")
    else:
        print("❌ Authentication failed")
        return False

    # Test wrong password
    print("Testing wrong password...")
    wrong_user = service.authenticate("testuser", "wrongpassword")
    if wrong_user is None:
        print("✅ Wrong password rejected correctly")
    else:
        print("❌ Wrong password accepted incorrectly")
        return False

    # Test API key
    print("Testing API key...")
    api_key_user = service.get_user_by_api_key(user.api_key)
    if api_key_user:
        print(f"✅ API key found for user: {api_key_user.username}")
    else:
        print("❌ API key not found")
        return False

    print("\n🎉 All user service tests passed!")
    return True


if __name__ == "__main__":
    test_user_service()