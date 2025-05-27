#!/usr/bin/env python3
"""
Unit tests for the Flask web application
"""

import pytest
import json
import sys
import os

# Add the parent directory to the path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, add_numbers, divide_numbers, calculate_fibonacci, get_app_version

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestFlaskApp:
    """Test cases for Flask application endpoints"""
    
    def test_home_page(self, client):
        """Test the home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Simple Python Web Application' in response.data
        assert b'Application Status: Running' in response.data
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_app_info(self, client):
        """Test the application info endpoint"""
        response = client.get('/api/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['application'] == 'Simple Python Web App'
        assert 'version' in data
        assert 'python_version' in data
        assert 'timestamp' in data
    
    def test_metrics(self, client):
        """Test the metrics endpoint"""
        response = client.get('/api/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'timestamp' in data
        assert 'uptime' in data
    
    def test_echo_endpoint(self, client):
        """Test the echo endpoint with POST data"""
        test_data = {'test': 'value', 'number': 42}
        response = client.post('/api/echo', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['received'] == test_data
        assert data['method'] == 'POST'
    
    def test_echo_endpoint_empty(self, client):
        """Test the echo endpoint with empty data"""
        response = client.post('/api/echo', 
                             data='',
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['received'] == {}

class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_add_numbers(self):
        """Test the add_numbers function"""
        assert add_numbers(2, 3) == 5
        assert add_numbers(-1, 1) == 0
        assert add_numbers(0, 0) == 0
        assert add_numbers(10, -5) == 5
    
    def test_divide_numbers(self):
        """Test the divide_numbers function"""
        assert divide_numbers(10, 2) == 5
        assert divide_numbers(9, 3) == 3
        assert divide_numbers(-10, 2) == -5
        assert divide_numbers(1, 4) == 0.25
    
    def test_divide_by_zero(self):
        """Test that divide_numbers raises error for division by zero"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide_numbers(10, 0)
    
    def test_calculate_fibonacci(self):
        """Test the fibonacci calculation function"""
        assert calculate_fibonacci(0) == 0
        assert calculate_fibonacci(1) == 1
        assert calculate_fibonacci(2) == 1
        assert calculate_fibonacci(3) == 2
        assert calculate_fibonacci(4) == 3
        assert calculate_fibonacci(5) == 5
        assert calculate_fibonacci(6) == 8
    
    def test_get_app_version(self):
        """Test the get_app_version function"""
        # Test default version
        version = get_app_version()
        assert isinstance(version, str)
        assert len(version) > 0
        
        # Test with environment variable
        os.environ['APP_VERSION'] = '2.0.0'
        assert get_app_version() == '2.0.0'
        
        # Clean up
        if 'APP_VERSION' in os.environ:
            del os.environ['APP_VERSION']

class TestErrorHandling:
    """Test cases for error handling"""
    
    def test_404_error(self, client):
        """Test 404 error for non-existent endpoint"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed error"""
        response = client.post('/health')
        assert response.status_code == 405

if __name__ == '__main__':
    pytest.main([__file__, '-v'])