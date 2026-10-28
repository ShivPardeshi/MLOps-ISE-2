pipeline {
    agent any

    environment {
        APP_NAME     = 'student-app'
        PORT         = '5000'
        IMAGE_NAME   = "student-app:${BUILD_NUMBER}"
        LATEST_IMAGE = "student-app:latest"
    }

    stages {
        stage('1. Checkout Source') {
            steps {
                echo '=== Stage 1: Checking out source code from Git/GitHub repository ==='
                checkout scm
            }
        }

        stage('2. Lint & Dependency Setup') {
            steps {
                echo '=== Stage 2: Setting up virtual environment & validating dependencies ==='
                // Runs bat on Windows agent or sh on Unix/Linux agent
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv || python -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            python -m py_compile app.py
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                            python -m py_compile app.py
                        '''
                    }
                }
            }
        }

        stage('3. Automated Testing (Quality Gate)') {
            steps {
                echo '=== Stage 3: Executing Pytest test suite for model inference & API endpoints ==='
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            python3 -m pytest tests/test_app.py -v --junitxml=test-results.xml || python -m pytest tests/test_app.py -v --junitxml=test-results.xml
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            python -m pytest tests/test_app.py -v --junitxml=test-results.xml
                        '''
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: '**/test-results.xml'
                }
            }
        }

        stage('4. Docker Container Build') {
            steps {
                echo '=== Stage 4: Building production Docker container image ==='
                script {
                    if (isUnix()) {
                        sh """
                            docker build -t ${IMAGE_NAME} -t ${LATEST_IMAGE} .
                        """
                    } else {
                        bat """
                            docker build -t %IMAGE_NAME% -t %LATEST_IMAGE% .
                        """
                    }
                }
            }
        }

        stage('5. Container Deployment & Healthcheck') {
            steps {
                echo '=== Stage 5: Deploying student-app container and verifying health endpoint ==='
                script {
                    if (isUnix()) {
                        sh """
                            docker stop ${APP_NAME} || true
                            docker rm ${APP_NAME} || true
                            docker run -d --name ${APP_NAME} -p ${PORT}:${PORT} ${LATEST_IMAGE}
                            sleep 5
                            curl -f http://localhost:${PORT}/health || exit 1
                        """
                    } else {
                        bat """
                            docker stop %APP_NAME% 2>nul || ver>nul
                            docker rm %APP_NAME% 2>nul || ver>nul
                            docker run -d --name %APP_NAME% -p %PORT%:%PORT% %LATEST_IMAGE%
                            powershell -Command "Start-Sleep -Seconds 5; try { Invoke-RestMethod -Uri http://localhost:%PORT%/health } catch { exit 1 }"
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo '====================================================='
            echo 'SUCCESS: student-app deployed successfully via Jenkins!'
            echo 'Access Web UI at: http://localhost:5000'
            echo 'Access Healthcheck at: http://localhost:5000/health'
            echo '====================================================='
        }
        failure {
            echo 'FAILURE: Jenkins CI/CD Pipeline encountered an error. Check logs.'
        }
    }
}
