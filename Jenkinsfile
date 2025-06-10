pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'vot-docker-file-tracker'
        DOCKER_TAG = "${BUILD_NUMBER}"
        # Ако docker-compose.yml не е в корена на репото, добавете:
        # APP_DIR = 'your_app_directory' // Заменете с реалния път
    }

    stages {
        stage('Install System Dependencies') { // Преименувано за по-ясно
            steps {
                sh '''
                    echo "Updating apt package lists..."
                    sudo apt-get update -y || true # -y за автоматично потвърждение, || true за да не спре пайплайна при временни проблеми
                    echo "Installing Python and curl..."
                    sudo apt-get install -y python3 python3-pip python3-venv curl
                    python3 --version
                    pip3 --version

                    echo "Checking for Docker Compose plugin (new syntax)..."
                    # Проверяваме дали docker compose (без тире) работи
                    if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
                        echo "Docker Compose plugin not found or not working. Attempting to install standalone docker-compose (old syntax)..."
                        # Инсталирайте старата версия на docker-compose, ако новата не работи
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
                # Ако APP_DIR е дефиниран, влезте в него.
                // script {
                //     if (env.APP_DIR) {
                //         sh "cd ${env.APP_DIR}"
                //     }
                // }
                sh '''
                    # Уверете се, че requirements.txt е наличен тук
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                # Ако APP_DIR е дефиниран, влезте в него.
                // script {
                //     if (env.APP_DIR) {
                //         sh "cd ${env.APP_DIR}"
                //     }
                // }
                sh '''
                    source venv/bin/activate
                    python3 -m pytest tests/ || true # Уверете се, че pytest е инсталиран във requirements.txt
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
                    # Проверяваме коя команда за docker compose работи
                    if docker compose version >/dev/null 2>&1; then
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
                docker system prune -f # Премахва неизползвани Docker обекти
                rm -rf venv            # Изтрива виртуалната среда
                # Ако сте променяли директории, може да се наложи да се върнете в началната
                # cd /var/lib/jenkins/workspace/VOT\ automation # Пример за връщане
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
                docker compose ps || docker-compose ps || true # Опитва и двете команди
                echo "Recent Container Logs:"
                docker compose logs || docker-compose logs || true # Опитва и двете команди
            '''
        }
    }
}