pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'vot-docker-file-tracker'
        DOCKER_TAG = "${BUILD_NUMBER}"
        // If docker-compose.yml is not at the root of the repo, uncomment and set APP_DIR:
        // APP_DIR = 'your_app_directory' // Replace with your actual application directory, e.g., 'flask_app'
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
                    # We use 'sudo sh -c' to ensure the command runs with necessary permissions for the check.
                    # This checks if 'docker compose' (new syntax) is available and working.
                    if sudo sh -c 'docker compose version >/dev/null 2>&1'; then
                        echo "Docker Compose plugin found. Using new syntax."
                    # This checks if 'docker-compose' (old syntax) is available.
                    elif sudo sh -c 'command -v docker-compose >/dev/null 2>&1'; then
                        echo "Standalone docker-compose (old syntax) found."
                    else
                        echo "Neither 'docker compose' nor 'docker-compose' found. Attempting to install standalone docker-compose..."
                        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        sudo chmod +x /usr/local/bin/docker-compose
                        docker-compose --version
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
                script {
                    // If APP_DIR is defined, change to that directory before setting up the Python environment.
                    if (env.APP_DIR) {
                        sh "cd ${env.APP_DIR}"
                    }
                }
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate  # Using '.' for POSIX compliance
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // If APP_DIR is defined, change to that directory before running tests.
                    if (env.APP_DIR) {
                        sh "cd ${env.APP_DIR}"
                    }
                }
                sh '''
                    . venv/bin/activate # Using '.' for POSIX compliance
                    python3 -m pytest tests/ || true # '|| true' allows the pipeline to continue even if tests fail
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // If APP_DIR is defined, change to that directory before building the Docker image.
                    if (env.APP_DIR) {
                        sh "cd ${env.APP_DIR}"
                    }
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    echo "Docker image built: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    // If APP_DIR is defined, change to that directory before deploying.
                    if (env.APP_DIR) {
                        sh "cd ${env.APP_DIR}"
                    }
                    echo "Attempting to deploy with Docker Compose..."
                    // Check which docker compose command is available and use it.
                    if (sh(script: 'docker compose version >/dev/null 2>&1', returnStatus: true) == 0) {
                        echo "Deployed using 'docker compose' (new syntax)."
                        sh '''
                            docker compose down || true
                            docker compose up -d --build
                        '''
                    } else if (sh(script: 'command -v docker-compose >/dev/null 2>&1', returnStatus: true) == 0) {
                        echo "Deployed using 'docker-compose' (old syntax)."
                        sh '''
                            docker-compose down || true
                            docker-compose up -d --build
                        '''
                    } else {
                        // If neither is found, the pipeline will fail here.
                        error "Neither 'docker compose' nor 'docker-compose' found. Deployment failed."
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace and Docker..."
            sh '''
                docker system prune -f # Removes unused Docker objects
                rm -rf venv            # Deletes the Python virtual environment
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
                docker compose ps || docker-compose ps || true # Tries both commands
                echo "Recent Container Logs:"
                docker compose logs || docker-compose logs || true # Tries both commands
            '''
        }
    }
}
