pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'docker.io/abdullahabaza/weather_app:latest'
        
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', credentialsId: 'github_cred', url: 'https://github.com/AbdullahAbaza/WeatherApp_CICD.git'
            }
        }
        
        stage('Dockerize') {
            steps {
                sh 'docker compose build'
            }
        }
        
        stage('Push to dockerhub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_cred', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin'
                    sh 'docker push ${DOCKER_IMAGE}'
                    sh 'docker logout'
                }
            }
        }
    }
}

