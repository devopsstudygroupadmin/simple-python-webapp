# Simple Python Web Application

A simple Flask web application designed for deployment in enterprise environments with comprehensive CI/CD pipeline integration.

## Features

- **Flask Web Framework**: Lightweight and scalable web application
- **Health Checks**: Built-in health monitoring endpoints
- **RESTful API**: JSON API endpoints for integration
- **Production Ready**: Configured with Gunicorn WSGI server
- **Security**: Non-root container execution and security scanning
- **Monitoring**: Application metrics and logging
- **Docker Support**: Multi-stage Docker builds for optimization

## API Endpoints

| Endpoint      | Method    | Description                       |
|---------------|-----------|-----------------------------------|
| /             | GET       | Home page with application status |
| /health       | GET       | Health check endpoint             |
| /api/info     | GET       | Application information (JSON)    |
| /api/metrics  | GET       | Basic application metrics (JSON)  |
| /api/echo     | POST      | Echo endpoint for testing         |

## Local Development

### Prerequisites

- Python 3.12+
- pip
- Docker (optional)
- Access to Nexus registry for UBI9 base images

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd simple-python-webapp
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open browser to: http://localhost:5000
   - Health check: http://localhost:5000/health

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
python -m pytest test_app.py -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Install development tools
pip install flake8 pylint black isort bandit safety

# Style checking
flake8 app.py test_app.py
pylint app.py

# Security scanning
bandit -r app.py
safety check

# Code formatting
black app.py test_app.py
isort app.py test_app.py
```

## Docker Usage

### Build Image

```bash
# Login to your Nexus registry first
docker login your-nexus-registry.com:8082

# Build the image
docker build -t simple-python-webapp:latest .
```

### Run Container

```bash
docker run -d -p 5000:5000 --name webapp simple-python-webapp:latest
```

### Test Container

```bash
curl http://localhost:5000/health
```

## CI/CD Pipeline

The application includes a comprehensive Jenkins pipeline (`Jenkinsfile`) that performs:

### Pipeline Stages

1. **Checkout**: Source code retrieval from GitHub Enterprise
2. **Python Environment Setup**: Virtual environment and dependency installation
3. **Code Quality Checks**: 
   - Linting (flake8, pylint)
   - Style checking (black, isort)
   - Security scanning (bandit, safety)
4. **Unit Tests & Coverage**: Pytest execution with coverage reporting
5. **SonarQube Analysis**: Static code analysis and quality gate
6. **AppScan Security Testing**: Dynamic application security testing
7. **Container Build**: Docker image creation with metadata
8. **Container Security Scan**: Image vulnerability scanning
9. **Registry Push**: Image deployment to Nexus Docker registry
10. **OpenShift Preparation**: Deployment manifest generation

### Required Jenkins Plugins

- Pipeline
- Docker Pipeline
- SonarQube Scanner
- Nexus Artifact Uploader
- HTML Publisher
- Credentials Binding

### Jenkins Configuration

#### Credentials Required

1. **nexus-credentials**: Username/password for Nexus registry
2. **appscan-credentials**: Username/password for HCL AppScan
3. **github-credentials**: Token for GitHub Enterprise access

#### Tools Configuration

1. **SonarQube Server**: Configure in Jenkins Global Tool Configuration
2. **Docker**: Ensure Docker is available on Jenkins agents
3. **Python**: Python 3.6.8 installation on build agents

### Environment Variables

Configure these in Jenkins or as pipeline parameters:

```groovy
NEXUS_REGISTRY = 'your-nexus-registry.com:8082'
SONARQUBE_SERVER = 'SonarQube'
SONARQUBE_PROJECT_KEY = 'simple-python-webapp'
```

## OpenShift Deployment

The pipeline generates OpenShift deployment manifests in the `openshift/` directory:

- `deployment.yaml`: Application deployment configuration
- `service.yaml`: Service exposure configuration  
- `route.yaml`: External routing configuration

### Manual Deployment

```bash
# Login to OpenShift
oc login <your-openshift-cluster>

# Create or switch to project
oc new-project simple-python-webapp || oc project simple-python-webapp

# Deploy application
oc apply -f openshift/

# Check deployment status
oc get pods
oc get routes
```

### Accessing the Application

```bash
# Get route URL
oc get route simple-python-webapp-route -o jsonpath='{.spec.host}'

# Test application
curl https://<route-url>/health
```

## Monitoring and Observability

### Health Checks

- **Liveness Probe**: `/health` endpoint
- **Readiness Probe**: `/health` endpoint
- **Docker Health Check**: Built into container

### Logging

- Application logs to stdout/stderr
- Structured logging with timestamps
- Request/response logging via Gunicorn

### Metrics

Basic metrics available at `/api/metrics` endpoint (extend as needed):
- Application uptime
- Request counters
- Memory usage
- Custom business metrics

## Security Features

- **Non-root container execution**: Runs as dedicated `appuser`
- **Minimal base image**: Python slim image reduces attack surface
- **Security scanning**: Integrated bandit and safety checks
- **Dependency scanning**: Regular security updates
- **Secret management**: No hardcoded credentials

## Production Considerations

### Resource Requirements

- **Minimum**: 128Mi memory, 100m CPU
- **Recommended**: 256Mi memory, 200m CPU
- **Scaling**: Horizontal pod autoscaling recommended

### Performance Optimization

- **Gunicorn workers**: Configured for production workloads
- **Multi-stage builds**: Optimized container image size
- **Connection pooling**: Implement for database connections
- **Caching**: Add Redis/Memcached for session storage

### High Availability

- **Multiple replicas**: Minimum 2 pods for availability
- **Pod disruption budgets**: Prevent simultaneous pod termination
- **Health checks**: Automatic pod restart on failure
- **Load balancing**: OpenShift service provides load distribution

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check Python version
   python3 --version
   
   # Verify dependencies
   pip check
   ```

2. **Container Issues**
   ```bash
   # Check container logs
   docker logs <container-name>
   
   # Debug container
   docker exec -it <container-name> /bin/bash
   ```

3. **OpenShift Deployment**
   ```bash
   # Check pod status
   oc describe pod <pod-name>
   
   # View logs
   oc logs <pod-name>
   ```

### Performance Issues

- Monitor CPU and memory usage
- Check application response times
- Review database connection pools
- Analyze network latency

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Ensure all tests pass (`pytest`)
5. Run quality checks (`flake8`, `pylint`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Create Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Maintain 80%+ test coverage
- Include docstrings for all functions
- Use type hints where appropriate
- Security scan must pass

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create GitHub issues for bugs
- Contact DevOps team for infrastructure
- Check Jenkins build logs for CI/CD issues

---

**Version**: 1.0.0  
**Python Version**: 3.6.8  
**Last Updated**: 2025