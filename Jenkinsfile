#!/usr/bin/env groovy

pipeline {
    /*
    agent {
        label 'linux'  // Use Linux worker nodes
    }
    */
    agent any
    environment {
        // Application settings
        APP_NAME = 'simple-python-webapp'
        APP_VERSION = "${BUILD_NUMBER}"
        PYTHON_VERSION = '3.12'
        
        // Registry settings
        NEXUS_REGISTRY = 'your-nexus-registry.com:8082'
        NEXUS_REPO = 'docker-hosted'
        NEXUS_CREDENTIALS_ID = 'nexus-credentials'
        
        // SonarQube settings
        SONARQUBE_SERVER = 'SonarQube'
        SONARQUBE_PROJECT_KEY = 'simple-python-webapp'
        
        // AppScan settings
        APPSCAN_CREDENTIALS_ID = 'appscan-credentials'
        
        // Build settings
        BUILD_DATE = sh(script: "date -u +'%Y-%m-%dT%H:%M:%SZ'", returnStdout: true).trim()
        // GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
        
        // Image naming
        IMAGE_NAME = "${NEXUS_REGISTRY}/${NEXUS_REPO}/${APP_NAME}"
        IMAGE_TAG = "${APP_VERSION}-${GIT_COMMIT_SHORT}"
        FULL_IMAGE_NAME = "${IMAGE_NAME}:${IMAGE_TAG}"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        skipDefaultCheckout()
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out source code..."
                    // checkout scm
                    checkout scmGit(branches: [[name: 'main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GIT_CICD_SVC', url: 'git@github.com:devopsstudygroupadmin/simple-python-webapp.git']])
                    
                    // Get additional git information
                    env.GIT_COMMIT_FULL = sh(script: "git rev-parse HEAD", returnStdout: true).trim()
                    env.GIT_BRANCH = sh(script: "git rev-parse --abbrev-ref HEAD", returnStdout: true).trim()
                    env.GIT_AUTHOR = sh(script: "git log -1 --pretty=format:'%an'", returnStdout: true).trim()
                    
                    echo "📋 Build Information:"
                    echo "   - Application: ${APP_NAME}"
                    echo "   - Version: ${APP_VERSION}"
                    echo "   - Git Branch: ${env.GIT_BRANCH}"
                    echo "   - Git Commit: ${env.GIT_COMMIT_FULL}"
                    echo "   - Git Author: ${env.GIT_AUTHOR}"
                    echo "   - Build Date: ${BUILD_DATE}"
                }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    echo "🐍 Setting up Python environment..."
                    sh '''
                        # Verify Python version
                        python3 --version
                        
                        # Create virtual environment
                        python3 -m venv venv
                        source venv/bin/activate
                        
                        # Upgrade pip
                        pip install --upgrade pip
                        
                        # Install dependencies
                        pip install -r requirements.txt
                        
                        # List installed packages for verification
                        pip list
                    '''
                }
            }
        }
        
        stage('Code Quality & Security Checks') {
            parallel {
                stage('Lint & Style Check') {
                    steps {
                        script {
                            echo "🔍 Running code quality checks..."
                            sh '''
                                source venv/bin/activate
                                
                                # Install linting tools
                                pip install flake8 pylint black isort
                                
                                # Run flake8 for style guide enforcement
                                echo "Running flake8..."
                                flake8 app.py test_app.py --max-line-length=88 --exclude=venv || true
                                
                                # Run pylint for code quality
                                echo "Running pylint..."
                                pylint app.py --disable=C0103,C0114,C0115,C0116 --exit-zero
                                
                                # Check import sorting
                                echo "Checking import sorting..."
                                isort --check-only --diff app.py test_app.py || true
                                
                                # Check code formatting
                                echo "Checking code formatting..."
                                black --check --diff app.py test_app.py || true
                            '''
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        script {
                            echo "🔒 Running security scans..."
                            sh '''
                                source venv/bin/activate
                                
                                # Install security scanning tools
                                pip install bandit safety
                                
                                # Run bandit for security issues
                                echo "Running Bandit security scan..."
                                bandit -r app.py -f json -o bandit-report.json || true
                                bandit -r app.py || true
                                
                                # Check for known security vulnerabilities in dependencies
                                echo "Running Safety check..."
                                safety check --json --output safety-report.json || true
                                safety check || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Unit Tests & Coverage') {
            steps {
                script {
                    echo "🧪 Running unit tests and code coverage..."
                    sh '''
                        source venv/bin/activate
                        
                        # Run tests with coverage
                        python -m pytest test_app.py -v --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing
                        
                        # Generate coverage badge data
                        coverage-badge -o coverage.svg
                        
                        # Display coverage summary
                        coverage report
                    '''
                }
            }
            post {
                always {
                    // Archive test results
                    archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'coverage.svg', allowEmptyArchive: true
                    
                    // Publish test results if using JUnit format
                    // publishTestResults testResultsPattern: 'test-results.xml'
                    
                    // Publish coverage results
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Code Coverage Report'
                    ])
                }
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "📊 Running SonarQube analysis..."
                    withSonarQubeEnv("${SONARQUBE_SERVER}") {
                        sh '''
                            source venv/bin/activate
                            
                            # Create sonar-project.properties if it doesn't exist
                            cat > sonar-project.properties << EOF
sonar.projectKey=${SONARQUBE_PROJECT_KEY}
sonar.projectName=${APP_NAME}
sonar.projectVersion=${APP_VERSION}
sonar.sources=app.py
sonar.tests=test_app.py
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml
sonar.exclusions=venv/**,htmlcov/**
EOF
                            
                            # Run SonarQube scanner
                            sonar-scanner
                        '''
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    echo "🚪 Waiting for SonarQube Quality Gate..."
                    timeout(time: 10, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to quality gate failure: ${qg.status}"
                        }
                    }
                }
            }
        }
        
        stage('AppScan Security Testing') {
            steps {
                script {
                    echo "🛡️ Running HCL AppScan security testing..."
                    withCredentials([usernamePassword(credentialsId: "${APPSCAN_CREDENTIALS_ID}", 
                                                    usernameVariable: 'APPSCAN_USER', 
                                                    passwordVariable: 'APPSCAN_PASS')]) {
                        sh '''
                            # Start the application in background for security testing
                            source venv/bin/activate
                            nohup python app.py &
                            APP_PID=$!
                            
                            # Wait for application to start
                            sleep 10
                            
                            # Check if application is running
                            curl -f http://localhost:5000/health || exit 1
                            
                            # Run AppScan (example command - adjust based on your AppScan setup)
                            # appscan.sh prepare -n "${APP_NAME}-security-scan"
                            # appscan.sh queue_analysis -a "${APP_NAME}-security-scan" -u "http://localhost:5000"
                            
                            # For demonstration, we'll use a mock security scan
                            echo "Mock AppScan security testing completed"
                            echo "In production, configure actual AppScan commands here"
                            
                            # Stop the application
                            kill $APP_PID || true
                        '''
                    }
                }
            }
        }
        
        stage('Build Container Image') {
            steps {
                script {
                    echo "🐳 Building Docker container image..."
                    
                    // Login to Nexus registry to pull base image
                    withCredentials([usernamePassword(credentialsId: "${NEXUS_CREDENTIALS_ID}", 
                                                    usernameVariable: 'NEXUS_USER', 
                                                    passwordVariable: 'NEXUS_PASS')]) {
                        sh '''
                            # Login to Nexus registry for base image access
                            echo "${NEXUS_PASS}" | docker login "${NEXUS_REGISTRY}" -u "${NEXUS_USER}" --password-stdin
                            
                            # Pull the base image to ensure we have the latest
                            docker pull "${NEXUS_REGISTRY}/ubi9/python-312:latest"
                            
                            # Build Docker image with build args
                            docker build \
                                --build-arg APP_VERSION="${APP_VERSION}" \
                                --build-arg BUILD_DATE="${BUILD_DATE}" \
                                --build-arg VCS_REF="${GIT_COMMIT_FULL}" \
                                --build-arg NEXUS_REGISTRY="${NEXUS_REGISTRY}" \
                                -t "${FULL_IMAGE_NAME}" \
                                -t "${IMAGE_NAME}:latest" \
                                .
                            
                            # List the built image
                            docker images | grep "${APP_NAME}"
                            
                            # Test the container image
                            echo "Testing container image..."
                            docker run --rm -d --name test-container -p 8080:5000 "${FULL_IMAGE_NAME}"
                            
                            # Wait for container to start
                            sleep 15
                            
                            # Test health endpoint with retries
                            for i in {1..5}; do
                                if curl -f http://localhost:8080/health; then
                                    echo "Health check passed"
                                    break
                                else
                                    echo "Health check attempt $i failed, retrying..."
                                    sleep 5
                                fi
                            done
                            
                            # Stop test container
                            docker stop test-container
                            
                            # Keep logged in for push stage
                        '''
                    }
                }
            }
        }
        
        stage('Container Security Scan') {
            steps {
                script {
                    echo "🔍 Scanning container image for vulnerabilities..."
                    sh '''
                        # Install or use container scanning tool (example with Trivy)
                        # In production, you might use Twistlock, Aqua, or similar
                        
                        # Example with Trivy (install if not available)
                        # curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
                        
                        # Scan the image
                        # trivy image --format json --output trivy-report.json "${FULL_IMAGE_NAME}"
                        # trivy image "${FULL_IMAGE_NAME}"
                        
                        echo "Container security scan completed (mock)"
                        echo "Configure actual container scanner (Trivy, Clair, etc.) here"
                    '''
                }
            }
        }
        
        stage('Push to Nexus Registry') {
            steps {
                script {
                    echo "📦 Pushing image to Nexus Docker registry..."
                    withCredentials([usernamePassword(credentialsId: "${NEXUS_CREDENTIALS_ID}", 
                                                    usernameVariable: 'NEXUS_USER', 
                                                    passwordVariable: 'NEXUS_PASS')]) {
                        sh '''
                            # Login to Nexus Docker registry
                            echo "${NEXUS_PASS}" | docker login "${NEXUS_REGISTRY}" -u "${NEXUS_USER}" --password-stdin
                            
                            # Push versioned image
                            docker push "${FULL_IMAGE_NAME}"
                            
                            # Push latest tag
                            docker push "${IMAGE_NAME}:latest"
                            
                            # Logout
                            docker logout "${NEXUS_REGISTRY}"
                            
                            echo "✅ Image pushed successfully:"
                            echo "   - ${FULL_IMAGE_NAME}"
                            echo "   - ${IMAGE_NAME}:latest"
                        '''
                    }
                }
            }
        }
        
        stage('Prepare OpenShift Deployment') {
            steps {
                script {
                    echo "🚀 Preparing OpenShift deployment manifests..."
                    sh '''
                        # Create deployment manifests directory
                        mkdir -p openshift
                        
                        # Generate deployment.yaml
                        cat > openshift/deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
    version: "${APP_VERSION}"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${APP_NAME}
  template:
    metadata:
      labels:
        app: ${APP_NAME}
        version: "${APP_VERSION}"
    spec:
      containers:
      - name: ${APP_NAME}
        image: ${FULL_IMAGE_NAME}
        ports:
        - containerPort: 5000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: APP_VERSION
          value: "${APP_VERSION}"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

                        # Generate service.yaml
                        cat > openshift/service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: ${APP_NAME}-service
  labels:
    app: ${APP_NAME}
spec:
  selector:
    app: ${APP_NAME}
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
  type: ClusterIP
EOF

                        # Generate route.yaml for OpenShift
                        cat > openshift/route.yaml << EOF
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ${APP_NAME}-route
  labels:
    app: ${APP_NAME}
spec:
  to:
    kind: Service
    name: ${APP_NAME}-service
  port:
    targetPort: 5000
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
EOF
                    '''
                    
                    // Archive deployment manifests
                    archiveArtifacts artifacts: 'openshift/**', fingerprint: true
                }
            }
        }
    }
    /*
    post {
        always {
            script {
                echo "🧹 Cleaning up..."
                
                // Clean up Docker images to save space
                sh '''
                    # Remove local images
                    docker rmi "${FULL_IMAGE_NAME}" || true
                    docker rmi "${IMAGE_NAME}:latest" || true
                    
                    # Clean up dangling images
                    docker image prune -f || true
                '''
                
                // Clean up Python virtual environment
                sh 'rm -rf venv || true'
            }
        }
        
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                echo "📦 Image: ${FULL_IMAGE_NAME}"
                echo "🔗 Ready for deployment to OpenShift"
                
                // Send success notification (configure based on your notification system)
                // slackSend(channel: '#deployments', 
                //          color: 'good', 
                //          message: "✅ ${APP_NAME} v${APP_VERSION} built successfully and pushed to registry")
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Send failure notification
                // slackSend(channel: '#deployments', 
                //          color: 'danger', 
                //          message: "❌ ${APP_NAME} v${APP_VERSION} build failed. Check Jenkins logs.")
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline completed with warnings"
            }
        }
    }
    */
}
