#!/usr/bin/env python3
"""
🔐 Test Secret Access - Proves loaders work
Run this to verify secrets are accessible via the universal loader
"""

from scripts.get_secret import get_secret
import sys

def test_secret_access():
    """Test that we can access secrets via the universal loader"""
    
    print("🧪 Testing Secret Access via Universal Loader")
    print("=" * 50)
    
    # Test getting a known secret
    test_key = 'GOOGLE_MAPS_API_KEY'
    secret = get_secret(test_key)
    
    if secret:
        print(f"✅ SUCCESS: Retrieved {test_key}")
        print(f"   Value starts with: {secret[:20]}...")
        print(f"   Length: {len(secret)} characters")
        print("\n🎉 Secret access WORKS via scripts/get_secret.py")
        return 0
    else:
        print(f"❌ FAILED: Could not retrieve {test_key}")
        print("\n💡 Make sure you have:")
        print("   - ~/.config/secrets/global.env (if accessible)")
        print("   - OR .env in project root")
        print("   - OR environment variable set")
        return 1

if __name__ == '__main__':
    sys.exit(test_secret_access())

