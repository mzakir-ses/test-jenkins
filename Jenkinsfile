pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://sonarqube:9000'
        SONAR_AUTH_TOKEN = credentials('sonarqube-token') // Replace 'sonarqube-token' with your Jenkins credentials ID
    }

    stages {
        stage('Checkout') {
            steps {
                // Clone the repository
                git branch: 'main', url: 'git@github.com:mzakir-ses/test-jenkins.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // Run SonarScanner
                withSonarQubeEnv('SonarQube') { // Replace 'SonarQube' with the name configured in Jenkins SonarQube settings
                    sh """
                    #!/bin/bash
                    $(tool 'SonarScanner')/bin/sonar-scanner \
                    -Dsonar.projectKey=python-project \
                    -Dsonar.projectName="python-project" \
                    -Dsonar.projectVersion=1.0 \
                    -Dsonar.sources=$WORKSPACE \
                    -Dsonar.host.url=$SONAR_HOST_URL \
                    -Dsonar.login=$SONAR_AUTH_TOKEN \
                    -Dsonar.working.directory=$WORKSPACE/.scannerwork \
                    -Dsonar.python.version=3.x \
                    -Dsonar.scm.provider=git
                    """
                }
            }
        }
    }
}
