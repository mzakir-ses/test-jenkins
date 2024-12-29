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


        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest-cov 
                    pytest --cov=. --cov-report=xml:coverage.xml --cov-report=html:coverage-html
                '''
            }
        }


        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') { // Match the name configured in Jenkins
                    script {
                        def scannerOutput = sh(
                            script: """
                                /var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner/bin/sonar-scanner \
                                -Dsonar.projectKey=python-project \
                                -Dsonar.projectName="python-project" \
                                -Dsonar.projectVersion=1.0 \
                                -Dsonar.sources=$WORKSPACE \
                                -Dsonar.inclusions=**/*.py \
                                -Dsonar.host.url=$SONAR_HOST_URL \
                                -Dsonar.login=$SONAR_AUTH_TOKEN \
                                -Dsonar.python.coverage.reportPaths=$WORKSPACE/coverage.xml \
                                -Dsonar.working.directory=$WORKSPACE/.scannerwork
                            """.stripIndent(),
                            returnStdout: true
                        ).trim()

                        echo "SonarQube Scanner Output: ${scannerOutput}"

                        // Extract the SonarQube Task ID
                        def taskIdMatch = scannerOutput =~ /task\?id=([a-z0-9-]+)/
                        if (taskIdMatch) {
                            env.SONAR_TASK_ID = taskIdMatch[0][1]
                            echo "Captured SonarQube Task ID: ${env.SONAR_TASK_ID}"
                        } else {
                            error "Failed to capture SonarQube Task ID from scanner output."
                        }
                    }
                }
            }
        }



        stage('Wait for Quality Gate') {
            steps {
                script {
                    def maxRetries = 10
                    def delay = 10
                    def taskUrl = "${SONAR_HOST_URL}/api/ce/task?id=${env.SONAR_TASK_ID}"
                    def qualityGateStatus = null

                    if (!env.SONAR_TASK_ID) {
                        error "SonarQube Task ID is null or not properly set. Ensure the SonarQube analysis stage captures it correctly."
                    }

                    for (int i = 0; i < maxRetries; i++) {
                        def response = sh(
                            script: "curl -u ${SONAR_AUTH_TOKEN}: ${taskUrl}",
                            returnStdout: true
                        ).trim()

                        echo "SonarQube API Response: ${response}"

                        def jsonResponse = readJSON(text: response)
                        if (!jsonResponse || !jsonResponse.task) {
                            error "Failed to parse SonarQube API response or response is empty. Check API response: ${response}"
                        }

                        if (jsonResponse.task.status == "SUCCESS") {
                            def analysisId = jsonResponse.task.analysisId
                            def qualityGateUrl = "${SONAR_HOST_URL}/api/qualitygates/project_status?analysisId=${analysisId}"

                            def qualityGateResponse = sh(
                                script: "curl -u ${SONAR_AUTH_TOKEN}: ${qualityGateUrl}",
                                returnStdout: true
                            ).trim()

                            def qualityGateJson = readJSON(text: qualityGateResponse)
                            qualityGateStatus = qualityGateJson.projectStatus.status
                            break
                        } else if (jsonResponse.task.status == "FAILED") {
                            error "SonarQube task failed. Task ID: ${env.SONAR_TASK_ID}"
                        }

                        sleep(delay)
                    }

                    if (qualityGateStatus != "OK") {
                        error "Quality Gate failed: ${qualityGateStatus}"
                    }
                }
            }
        }


        stage('Get Code Coverage') {
            steps {
                script {
                    def coverageValue = null
                    def coverageUrl = "${SONAR_HOST_URL}/api/measures/component?component=python-project&metricKeys=coverage"

                    // Fetch the coverage metric
                    def coverageResponse = sh(
                        script: "curl -s -u ${SONAR_AUTH_TOKEN}: ${coverageUrl}",
                        returnStdout: true
                    ).trim()

                    echo "SonarQube Coverage API Response: ${coverageResponse}"

                    // Parse the response to extract the coverage value
                    def coverageJson = readJSON(text: coverageResponse)
                    if (coverageJson?.component?.measures) {
                        coverageValue = coverageJson.component.measures.find { it.metric == "coverage" }?.value
                    }

                    if (coverageValue == null) {
                        error "Failed to fetch coverage value from SonarQube. Response: ${coverageResponse}"
                    }

                    echo "Overall Code Coverage: ${coverageValue}%"

                    // Validate coverage
                    def coverageThreshold = 80
                    if (coverageValue.toFloat() < coverageThreshold) {
                        error "Code coverage is below the acceptable threshold (${coverageThreshold}%): ${coverageValue}%"
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
