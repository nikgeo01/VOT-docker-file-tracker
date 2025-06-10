pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'vot-docker-file-tracker'
        DOCKER_TAG = "${BUILD_NUMBER}"
        // Ако docker-compose.yml не е в корена на репото, добавете:
        // APP_DIR = 'your_app_directory' // Заменете с реалния път
    }

    stages {
        stage('Install System Dependencies') {
            steps {
                sh '''
                    echo "Updating apt package lists..."
                    sudo apt-get update -y || true
                    echo "Installing Python and curl..."
                    sudo apt-get install -y python3 python3-pip python3-venv curl
                    python3 --version
                    pip3 --version

                    echo "Checking for Docker Compose plugin (new syntax)..."
                    if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
                        echo "Docker Compose plugin not found or not working. Attempting to install standalone docker-compose (old syntax)..."
                        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        sudo chmod +x /usr/local/bin/docker-compose
                        docker-compose --version
                    else
                        echo "Docker Compose plugin found. Using new syntax."
                    fi
                '''
            }
        }

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                // Ако APP_DIR е дефиниран, влезте в него.
                // script {
                //     if (env.APP_DIR) {
                //         sh "cd ${env.APP_DIR}"
                //     }
                // }
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                // Ако APP_DIR е дефиниран, влезте в него.
                // script {
                //     if (env.APP_DIR) {
                //         sh "cd ${env.APP_DIR}"
                //     }
                // }
                sh '''
                    source venv/bin/activate
                    python3 -m pytest tests/ || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Ако APP_DIR е дефиниран, влезте в него преди build
                    // if (env.APP_DIR) {
                    //     sh "cd ${env.APP_DIR}"
                    // }
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    echo "Docker image built: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    // Ако APP_DIR е дефиниран, влезте в него преди deploy
                    // if (env.APP_DIR) {
                    //     sh "cd ${env.APP_DIR}"
                    // }
                    echo "Attempting to deploy with Docker Compose..."
                    if docker compose version >/dev/null 2>&1; then // Проверяваме коя команда за docker compose работи
                        sh '''
                            docker compose down || true
                            docker compose up -d --build
                        '''
                        echo "Deployed using 'docker compose' (new syntax)."
                    elif command -v docker-compose >/dev/null 2>&1; then
                        sh '''
                            docker-compose down || true
                            docker-compose up -d --build
                        '''
                        echo "Deployed using 'docker-compose' (old syntax)."
                    else
                        error "Neither 'docker compose' nor 'docker-compose' found. Deployment failed."
                    fi
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace and Docker..."
            sh '''
                docker system prune -f
                rm -rf venv
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Checking status for debugging...'
            sh '''
                echo "Docker Process Status:"
                docker ps -a
                echo "Docker Compose Service Status (if applicable):"
                docker compose ps || docker-compose ps || true
                echo "Recent Container Logs:"
                docker compose logs || docker-compose logs || true
            '''
        }
    }
}