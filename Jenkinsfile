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
        // Nombre del archivo de datos de cobertura para combinar
        COV_DATA_FILE = '.coverage'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // Preparar el contenedor una sola vez (instalar dependencias, etc.)
        stage('Prepare Test Container') {
            steps {
                sh '''
                    docker rm -f redpulse-ci || true
                    docker run -d --name redpulse-ci python:3.11-slim tail -f /dev/null
                    docker cp . redpulse-ci:/app
                    docker exec redpulse-ci sh -lc "
                        cd /app &&
                        pip install --upgrade pip &&
                        pip install -r requirements.txt
                    "
                '''
            }
        }

        // Pruebas de API
        stage('API Tests') {
            steps {
                sh '''
                    docker exec redpulse-ci sh -lc "
                        cd /app &&
                        pytest src/tests/api --cov=. --cov-append --cov-report= --cov-branch
                    "
                '''
            }
        }

        // Pruebas de Rendimiento (Performance)
        stage('Performance Tests') {
            steps {
                sh '''
                    docker exec redpulse-ci sh -lc "
                        cd /app &&
                        pytest src/tests/performance --cov=. --cov-append --cov-report= --cov-branch
                    "
                '''
            }
        }

        // Pruebas de Regresión
        stage('Regression Tests') {
            steps {
                sh '''
                    docker exec redpulse-ci sh -lc "
                        cd /app &&
                        pytest src/tests/regression --cov=. --cov-append --cov-report= --cov-branch
                    "
                '''
            }
        }

        // Pruebas de Seguridad
        stage('Security Tests') {
            steps {
                sh '''
                    docker exec redpulse-ci sh -lc "
                        cd /app &&
                        pytest src/tests/security --cov=. --cov-append --cov-report= --cov-branch
                    "
                '''
            }
        }

        // Generar reporte de cobertura final
        stage('Generate Coverage Report') {
            steps {
                sh '''
                    docker exec redpulse-ci sh -lc "
                        cd /app &&
                        coverage xml -o coverage.xml
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
                        ${scannerHome}/bin/sonar-scanner
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
            // El coverage.xml ya se generó y archivó en el stage correspondiente
            archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
        }
    }
}