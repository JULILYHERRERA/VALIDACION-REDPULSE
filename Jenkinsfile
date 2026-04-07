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

        stage('Debug Workspace') {
            steps {
                sh '''
                echo "PWD=$PWD"
                ls -la
                echo "Archivos del workspace:"
                find . -maxdepth 3 -type f | sort
                '''
            }
        }

        stage('Run Tests with Coverage') {
            steps {
                sh '''
                docker run --rm \
                  -v "$PWD:/app" \
                  -w /app \
                  python:3.11-slim \
                  sh -lc "pip install --upgrade pip && pip install -r requirements.txt && pytest"
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
                          -Dsonar.tests=tests \
                          -Dsonar.python.version=3.11 \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.exclusions=src/secret_config.py \
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