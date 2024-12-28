pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://localhost:9000'
        SONAR_AUTH_TOKEN = credentials('sonarqube-token') // Replace 'sonar-auth-token' with the ID you used for credential
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'git@github.com:mzakir-ses/test-jenkins.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') { // Ensure 'SonarQube' matches the name in Jenkins config sonarqube server name 
                    sh 'sonar-scanner -Dsonar.login=$SONAR_AUTH_TOKEN'
                }
            }
        }
    }
}
