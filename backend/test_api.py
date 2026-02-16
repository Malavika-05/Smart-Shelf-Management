#!/usr/bin/env python3
"""
Simple test script to verify the backend API is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_detect():
    """Test detect endpoint"""
    print("\nTesting /api/detect...")
    try:
        response = requests.get(f"{BASE_URL}/api/detect")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_forecast():
    """Test forecast endpoint"""
    print("\nTesting /api/forecast...")
    try:
        response = requests.get(f"{BASE_URL}/api/forecast")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_alerts():
    """Test alerts endpoint"""
    print("\nTesting /api/alerts...")
    try:
        response = requests.get(f"{BASE_URL}/api/alerts")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_analytics():
    """Test analytics endpoint"""
    print("\nTesting /api/analytics...")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics?range=24h")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Smart Shelf Management Backend API Test")
    print("=" * 50)
    print(f"Testing API at {BASE_URL}")
    print("\nMake sure the backend server is running!")
    print("=" * 50)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Detect", test_detect()))
    results.append(("Forecast", test_forecast()))
    results.append(("Alerts", test_alerts()))
    results.append(("Analytics", test_analytics()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20} {status}")
    
    all_passed = all(result for _, result in results)
    print("=" * 50)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed. Check the output above.")
