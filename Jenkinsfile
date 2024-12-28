pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://sonarqube:9000'
        SONAR_AUTH_TOKEN = credentials('sonarqube-token') // Replace with your Jenkins credentials ID
        DOCKER_IMAGE_NAME = 'python-project-image'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'git@github.com:mzakir-ses/test-jenkins.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') { // Match the name configured in Jenkins
                    sh """
                    /var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner/bin/sonar-scanner \
                    -Dsonar.projectKey=python-project \
                    -Dsonar.projectName="python-project" \
                    -Dsonar.projectVersion=1.0 \
                    -Dsonar.sources=$WORKSPACE \
                    -Dsonar.host.url=$SONAR_HOST_URL \
                    -Dsonar.login=$SONAR_AUTH_TOKEN \
                    -Dsonar.working.directory=$WORKSPACE/.scannerwork
                    """
                }
            }
        }
        stage('Wait for Quality Gate') {
            steps {
                script {
                    def maxRetries = 30 // Number of attempts
                    def delay = 10 // Delay between retries (in seconds)

                    def taskUrl = "${SONAR_HOST_URL}/api/ce/task?id=${env.SONAR_TASK_ID}"
                    def qualityGateStatus = null

                    for (int i = 0; i < maxRetries; i++) {
                        def response = sh(
                            script: "curl -u ${SONAR_AUTH_TOKEN}: ${taskUrl}",
                            returnStdout: true
                        ).trim()

                        def jsonResponse = readJSON(text: response)

                        if (jsonResponse.status == "SUCCESS") {
                            qualityGateStatus = jsonResponse.analysisStatus
                            break
                        } else if (jsonResponse.status == "FAILED") {
                            error "SonarQube task failed!"
                        }

                        sleep(delay)
                    }

                    if (qualityGateStatus != "OK") {
                        error "Quality Gate failed: ${qualityGateStatus}"
                    }
                }
            }
        }


        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t $DOCKER_IMAGE_NAME:latest $WORKSPACE
                """
            }
        }
        stage('Scan Docker Image with Trivy') {
            steps {
                sh """
                # Run Trivy to scan the built Docker image
                docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    aquasec/trivy:latest image $DOCKER_IMAGE_NAME:latest
                """
            }
        }

        // stage('Scan Docker Image with Trivy') {
        //     steps {
        //         script {
        //             // Run Trivy and fail the pipeline if critical vulnerabilities are found
        //             def scanResult = sh(
        //                 script: """
        //                 docker run --rm \
        //                     -v /var/run/docker.sock:/var/run/docker.sock \
        //                     aquasec/trivy:latest image \
        //                     --severity CRITICAL \
        //                     --exit-code 1 \
        //                     $DOCKER_IMAGE_NAME:latest
        //                 """,
        //                 returnStatus: true
        //             )
                    
        //             if (scanResult != 0) {
        //                 error "Trivy found critical vulnerabilities in the Docker image!"
        //             }
        //         }
        //     }
        // }

    }
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
