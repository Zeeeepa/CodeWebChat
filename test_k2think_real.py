#!/usr/bin/env python3
"""
Real-world test for K2Think provider
Tests actual login and message sending
"""

import sys
sys.path.insert(0, '/tmp/Zeeeepa/CodeWebChat')

from src.providers.k2think import K2ThinkProvider

def test_k2think_login_and_chat():
    """Test K2Think provider with real credentials"""
    
    print("="*60)
    print("K2Think Provider - Real World Test")
    print("="*60)
    
    # Initialize provider
    provider = K2ThinkProvider()
    
    # Test credentials (from user)
    email = "developer@pixelium.uk"
    password = "developer123?"
    
    print(f"\n1. Testing login to {K2ThinkProvider.AUTH_URL}")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)}")
    
    # Attempt login
    try:
        success = provider.login(email, password)
        
        if not success:
            print("\n❌ LOGIN FAILED")
            print("Possible reasons:")
            print("  - Credentials incorrect")
            print("  - Page structure changed")
            print("  - CAPTCHA present")
            print("  - Network issues")
            provider.close()
            return False
        
        print("\n✅ LOGIN SUCCESSFUL!")
        
        # Test sending a message
        print(f"\n2. Testing message sending to {K2ThinkProvider.CHAT_URL}")
        test_message = "Hello! Please respond with 'test successful' if you receive this."
        
        print(f"   Sending: {test_message}")
        
        response = provider.send_message(test_message)
        
        if response:
            print("\n✅ MESSAGE SENT & RESPONSE RECEIVED!")
            print(f"\n📝 Response:")
            print("-" * 60)
            print(response)
            print("-" * 60)
            
            # Close
            provider.close()
            return True
        else:
            print("\n❌ NO RESPONSE RECEIVED")
            print("Possible reasons:")
            print("  - Chat input not found")
            print("  - Response element not found")
            print("  - Page structure changed")
            provider.close()
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        provider.close()
        return False

if __name__ == "__main__":
    success = test_k2think_login_and_chat()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nNext steps:")
        print("1. Wrap this in FastAPI endpoint")
        print("2. Add OpenAI-compatible response format")
        print("3. Add streaming support")
        print("4. Add error recovery")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check if credentials are correct")
        print("2. Check if k2think.ai is accessible")
        print("3. Run with --headful to see browser")
        print("4. Check page HTML structure")
        sys.exit(1)

