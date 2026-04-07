pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        VENV_DIR = '.venv'
        IMAGE_NAME = 'redpulse-app'
        CONTAINER_NAME = 'redpulse-app-container'
        SONAR_PROJECT_KEY = 'Redpulse'
        SONAR_PROJECT_NAME = 'Redpulse'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh '''
                docker rm -f redpulse-ci || true

                docker run -d --name redpulse-ci python:3.11-slim tail -f /dev/null

                docker cp . redpulse-ci:/app

                docker exec redpulse-ci sh -lc "
                    cd /app &&
                    pip install --upgrade pip &&
                    pip install -r requirements.txt &&
                    pytest --cov=src --cov-report=xml --cov-report=term-missing
                "

                docker cp redpulse-ci:/app/coverage.xml coverage.xml

                docker rm -f redpulse-ci
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.projectName="${SONAR_PROJECT_NAME}" \
                        -Dsonar.sources=src \
                        -Dsonar.tests=src/tests \
                        -Dsonar.exclusions=src/tests/**,src/secret_config.py \
                        -Dsonar.python.version=3.11 \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Deploy Container') {
            steps {
                sh """
                docker rm -f ${CONTAINER_NAME} || true
                docker run -d --name ${CONTAINER_NAME} -p 8000:8000 ${IMAGE_NAME}:latest
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
        }
    }
}