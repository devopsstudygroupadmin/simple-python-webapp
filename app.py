#!/usr/bin/env python3
"""
Simple Flask Web Application
A basic web application with health checks, logging, and basic functionality
"""

from flask import Flask, jsonify, request, render_template_string
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Basic HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Python Web App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { background: #e8f5e8; padding: 20px; border-radius: 5px; }
        .info { background: #f0f8ff; padding: 15px; margin-top: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Simple Python Web Application</h1>
        <div class="status">
            <h2>Application Status: Running</h2>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Python Version:</strong> {{ python_version }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
        </div>
        <div class="info">
            <h3>Available Endpoints:</h3>
            <ul>
                <li><a href="/">/</a> - Home page</li>
                <li><a href="/health">/health</a> - Health check</li>
                <li><a href="/api/info">/api/info</a> - Application info (JSON)</li>
                <li><a href="/api/metrics">/api/metrics</a> - Basic metrics (JSON)</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Home page with application information"""
    logger.info("Home page accessed")
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        python_version=sys.version,
        environment=os.environ.get('ENVIRONMENT', 'development')
    )

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check accessed")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': get_app_version()
    }), 200

@app.route('/api/info')
def app_info():
    """Application information endpoint"""
    logger.info("App info accessed")
    return jsonify({
        'application': 'Simple Python Web App',
        'version': get_app_version(),
        'python_version': sys.version,
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('ENVIRONMENT', 'development'),
        'port': os.environ.get('PORT', '5000')
    })

@app.route('/api/metrics')
def metrics():
    """Basic metrics endpoint"""
    logger.info("Metrics accessed")
    return jsonify({
        'uptime': 'N/A',  # In a real app, you'd track this
        'requests_total': 'N/A',  # In a real app, you'd track this
        'memory_usage': 'N/A',  # In a real app, you'd track this
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing POST requests"""
    logger.info("Echo endpoint accessed")
    data = request.get_json() or {}
    return jsonify({
        'received': data,
        'timestamp': datetime.now().isoformat(),
        'method': request.method
    })

def get_app_version():
    """Get application version from environment or default"""
    return os.environ.get('APP_VERSION', '1.0.0')

def calculate_fibonacci(n):
    """Calculate fibonacci number - for testing purposes"""
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

def add_numbers(a, b):
    """Add two numbers - for testing purposes"""
    return a + b

def divide_numbers(a, b):
    """Divide two numbers - for testing purposes"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting application on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Python version: {sys.version}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)