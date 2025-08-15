#!/usr/bin/env python3
"""
Test script to measure response times for all chat endpoints.
"""

import requests
import time
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_MESSAGE = "add iPhone 15 Pro, amazing camera and price is $999"

# Test endpoints
ENDPOINTS = [
    ("/chat/v1", "Configurable NLP (qwen2.5:3b-instruct-q4_K_M)"),
    ("/chat/v2", "Joint Intent-Slot Classification"),
    ("/chat/v3", "CSV-based ML Classifier")
]

def test_endpoint(endpoint, description):
    """Test a single endpoint and measure response time."""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🧪 Testing {description}")
    print(f"📍 Endpoint: {endpoint}")
    print(f"📝 Message: {TEST_MESSAGE}")
    print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            json={"message": TEST_MESSAGE},
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"📤 Response: {json.dumps(result, indent=2)}")
            
            # Extract additional info if available
            if "method" in result:
                print(f"🔍 Method: {result['method']}")
            if "confidence" in result:
                print(f"📊 Confidence: {result['confidence']}")
            if "extraction_time" in result:
                print(f"⚡ Extraction time: {result['extraction_time']:.2f}s")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"⏱️  Response time: {response_time:.2f} seconds (TIMEOUT)")
        print("❌ Request timed out")
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"❌ Error: {str(e)}")
    
    return response_time

def main():
    """Main test function."""
    print("🚀 Starting Chat API Performance Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Test Message: {TEST_MESSAGE}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    for endpoint, description in ENDPOINTS:
        response_time = test_endpoint(endpoint, description)
        results.append((description, response_time))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    for description, response_time in results:
        print(f"{description:<40} | {response_time:>8.2f}s")
    
    print("=" * 60)
    
    # Find fastest and slowest
    if results:
        fastest = min(results, key=lambda x: x[1])
        slowest = max(results, key=lambda x: x[1])
        
        print(f"🏆 Fastest: {fastest[0]} ({fastest[1]:.2f}s)")
        print(f"🐌 Slowest: {slowest[0]} ({slowest[1]:.2f}s)")
        
        if fastest[1] > 0:
            speedup = slowest[1] / fastest[1]
            print(f"⚡ Speedup: {speedup:.1f}x faster than slowest")

if __name__ == "__main__":
    main()
