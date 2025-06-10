pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'vot-docker-file-tracker'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    apt-get update
                    apt-get install -y python3 python3-pip python3-venv curl
                    python3 --version
                    
                    # Install Docker Compose
                    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                    docker-compose --version
                '''
            }
        }
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip3 install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -m pytest tests/ || true  # Add tests when available
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
            }
        }
        
        stage('Deploy with Docker Compose') {
            steps {
                sh '''
                    if ! command -v docker-compose &> /dev/null; then
                        echo "Docker Compose is not installed. Installing..."
                        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        chmod +x /usr/local/bin/docker-compose
                    fi
                    
                    docker-compose down || true
                    docker-compose up -d || {
                        echo "Failed to start containers with docker-compose"
                        exit 1
                    }
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                docker system prune -f
                rm -rf venv
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
            sh '''
                echo "Checking Docker status..."
                docker ps
                echo "Checking Docker Compose status..."
                docker-compose ps || true
            '''
        }
    }
} 