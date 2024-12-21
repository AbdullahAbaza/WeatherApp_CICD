pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'docker.io/abdullahabaza/weather_app:latest'
        ANSIBLE_KEY = '/tmp/VMs_Shared_ppk_ID' // Single SSH key for all servers
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', credentialsId: 'github_cred', url: 'https://github.com/AbdullahAbaza/WeatherApp_CICD.git'
            }
        }
        
        stage('Dockerize') {
            steps {
                sh 'docker compose build'
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_cred', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin'
                    sh 'docker push ${DOCKER_IMAGE}'
                    sh 'docker logout'
                }
            }
        }
        
        stage('Prepare SSH Key') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'VMs_Shared_ppk_ID', keyFileVariable: 'KEY_FILE')]) {
                    sh """
                        cp \$KEY_FILE ${env.ANSIBLE_KEY}
                        chmod 600 ${env.ANSIBLE_KEY}
                    """
                }
            }
        }
        
        stage('Run Ansible Playbook Deploy') {
            steps {
                sh """
                    cd ./Ansible/
                    ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory playbook.yml -v \
                    --private-key ${env.ANSIBLE_KEY}
                """
            }
        }
        
        stage('Cleanup SSH Key') {
            steps {
                sh """
                    rm -f ${env.ANSIBLE_KEY}
                """
            }
        }
    }
    
    post {
        always {
            sh "rm -f ${env.ANSIBLE_KEY}" // Clean up SSH key even if the job fails
        }
    }
}
