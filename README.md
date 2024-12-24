# Weather App - DevOps Implementation Project

This project demonstrates a complete CI/CD pipeline implementation for a simple Flask weather application. The pipeline includes containerization, automated builds, and deployment using various DevOps tools and practices.

## Project Overview

The project implements a complete DevOps pipeline with the following components:
- GitHub for source code management
- Jenkins for continuous integration and deployment
- Docker for containerization
- Vagrant for local development environments
- Ansible for configuration management and automated deployment

## Prerequisites

Before you begin, ensure you have the following installed:
- Ubuntu Server 20.04 LTS VM (Main Jenkins Server)
- Git
- GitHub Account
- Jenkins (2.x or later)
- Docker and Docker Hub Account
- Vagrant (2.x or later)
- VirtualBox (6.x or later)
- Ansible (2.9 or later)
- SSH key pair

## Project Architecture

## Detailed Setup Instructions

### 1. Main Server Configuration (Ubuntu Server VM)

#### 1.1 Setting up GitHub SSH Access

1. **Initial Git Configuration:**
   Set your global username and email for Git commits:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your-email@example.com"
   ```

2. **Generate SSH Key Pair:**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

3. **Start SSH Agent and Add Key:**
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. **Copy Public Key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

5. **Add SSH Key to GitHub:**
   - Go to GitHub Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste your public key
   - Give it a descriptive title

6. **Test GitHub SSH Connection:**
   ```bash
   ssh -T git@github.com
   ```
   You should see a message like:
   ```
   Hi USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
   ```

#### 1.2 Create Private GitHub Repository

1. On GitHub:
   - Click "+" → "New repository"
   - Select "Private"

2. Clone and Set Up Repository:
   ```bash
   git clone git@github.com:yourusername/RepositoryName.git
   cd RepositoryName
   ```

3. Add Project Files:
   ```bash
   # Add your project files
   git add .
   git commit -m "Initial commit: Add Weather App project files"
   git push origin main
   ```

4. Verify Repository Setup:
   ```bash
   git status
   git remote -v
   ```

### 2. Local Environment Setup

#### Clone the Repository
```bash
git clone https://github.com/[your-username]/WeatherApp_CICD.git
cd WeatherApp_CICD
```

#### Set Up Vagrant Machines
1. Navigate to Vagrant directory:
   ```bash
   cd Vagrant
   ```

2. Start Vagrant machines:
   ```bash
   vagrant up
   ```
   This will create two Ubuntu machines with:
   - 600MB RAM each
   - 2 CPU cores each
   - Ubuntu 22.04 LTS

   **Adjust Vagrantfile Configuration:**
   - Open the `Vagrantfile` in a text editor:
     ```bash
     nano Vagrantfile
     ```
   - Set the network configuration by adding the following lines under the `Vagrant.configure` block:
     ```ruby
     config.vm.network "private_network", ip: "192.168.33.10"
     config.vm.network "private_network", ip: "192.168.33.11"
     ```
   - To provision a custom SSH key, add the following line:
     ```ruby
     config.ssh.private_key_path = "~/.ssh/id_ed25519"
     ```
   - Save and exit the editor (for nano, use `CTRL + X`, then `Y`, then `Enter`).

3. Verify machines are running:
   ```bash
   vagrant status
   ```
   You should see the status of both machines as 'running'.

4. SSH into the first machine:
   ```bash
   vagrant ssh m01
   ```
   This command will log you into the first Vagrant machine.

5. Display SSH configuration:
   ```bash
   vagrant ssh-config
   ```
   This will show you the SSH configuration and confirm that your SSH key has been added correctly.

6. Note down the IP addresses of both machines for Ansible inventory.

### 3. Set Up the Python Virtual Environment and Run the App

1. **Navigate to the Project Directory:**
   ```bash
   cd ~/WeatherApp_CICD/app
   ```

2. **Create a Python Virtual Environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```
   You should see the environment name in your terminal prompt, indicating that the virtual environment is active.

4. **Install Required Packages:**
   Make sure you have a `requirements.txt` file in your project directory. If it doesn't exist, create one with the necessary dependencies for your app. Then, install the packages:
   ```bash
   pip install -r requirements.txt
   ```

5. **Modify the App with the Correct Weather API Key:**
   Open the `app.py` file and update the `API_KEY` variable with your actual weather API key:
   ```python
   API_KEY = 'your_actual_weather_api_key'
   ```

6. **Run the App to Test:**
   ```bash
   python app.py
   ```
   The app should start running, and you can access it at `http://localhost:5001`.

7. **Verify the Application is Working:**
   Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```
   You should see the application interface.

### 4. Docker Installation and Application Containerization

#### 4.1 Install Docker
1. **Set up Docker's apt repository:**
   ```bash
   # Add Docker's official GPG key
   sudo apt-get update
   sudo apt-get install ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc

   # Add the repository to Apt sources
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
     $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

2. **Install Docker packages:**
   ```bash
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

3. **Add your user to the docker group:**
   ```bash
   sudo groupadd docker
   sudo usermod -aG docker $USER
   newgrp docker
   ```

4. **Verify Docker installation:**
   ```bash
   docker --version
   docker run hello-world
   ```

#### 4.2 Containerize the Weather App

1. **Create a Dockerfile:**
   Create a file named `Dockerfile` in your project root:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app/ .

   ENV FLASK_APP=app.py
   ENV FLASK_ENV=development

   EXPOSE 5001

   CMD ["python", "app.py"]
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t weather-app:latest .
   ```

3. **Run the container:**
   ```bash
   docker run -d -p 5001:5001 --name weather-app weather-app:latest
   ```

4. **Test the containerized application:**
   - Open your browser and navigate to `http://localhost:5001`
   - Verify that the weather app is working correctly

5. **Basic Docker commands for management:**
   ```bash
   # Stop the container
   docker stop weather-app

   # Start the container
   docker start weather-app

   # Remove the container
   docker rm weather-app

   # List running containers
   docker ps

   # List all containers (including stopped)
   docker ps -a

   # View container logs
   docker logs weather-app
   ```

#### 4.3 Docker Compose Setup

1. **Create a Docker Compose file:**
   Create a file named `docker-compose.yml` in your project root:
   ```yaml
   version: '3.8'

   services:
     weather_app:
       build: ./app
       image: abdullahabaza/weather_app:latest
       ports:
         - "5001:5001"
       environment:
         - FLASK_APP=app.py
         - FLASK_ENV=production
         - PYTHONUNBUFFERED=1
       restart: always
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s

   networks:
     default:
       name: weather-network
       driver: bridge
   ```

2. **Key Components Explained:**
   - `build: ./app`: Builds from the Dockerfile in the app directory
   - `image: abdullahabaza/weather_app:latest`: Docker Hub image reference
   - `environment`: Production-ready environment variables
   - `healthcheck`: Container health monitoring
   - `restart: always`: Ensures container automatically restarts

3. **Build and Run with Docker Compose:**
   ```bash
   # Build and start containers
   docker-compose up -d

   # Check container status and health
   docker-compose ps

   # View logs
   docker-compose logs -f weather_app
   ```

4. **Managing the Container:**
   ```bash
   # Stop the container
   docker-compose down

   # Rebuild and restart
   docker-compose up -d --build

   # Login to Docker Hub
   docker login -u yourusername
   # When prompted for password, use the access token

   # Push to Docker Hub
   docker-compose push weather_app
   ```

5. **Push to Docker Hub:**
   
   a. **Create Docker Hub Access Token:**
      - Log in to [Docker Hub](https://hub.docker.com)
      - Go to Account Settings → Security
      - Click "New Access Token"
      - Give it a descriptive title (e.g., "weather-app-token")
      - Choose appropriate permissions (read/write)
      - Copy the token immediately (you won't see it again!)

   b. **Login to Docker Hub:**
      ```bash
      # Login using your access token
      docker login -u yourusername
      # When prompted for password, use the access token
      ```

   c. **Push the Image:**
      ```bash
      # Push to Docker Hub
      docker-compose push weather_app
      ```

### 5. Jenkins Setup and Configuration

#### 5.1 Install Jenkins

1. **Install Java and Jenkins:**
   ```bash
   # Update and install Java
   sudo apt update
   sudo apt install fontconfig openjdk-17-jre
   
   # Verify Java installation
   java -version
   
   # Add Jenkins repository key
   sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
     https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
   
   # Add Jenkins repository
   echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]" \
     https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
     /etc/apt/sources.list.d/jenkins.list > /dev/null
   
   # Install Jenkins
   sudo apt-get update
   sudo apt-get install jenkins
   
   # Start Jenkins service
   sudo systemctl enable jenkins
   sudo systemctl start jenkins
   sudo systemctl status jenkins
   ```

2. **Configure Jenkins for Docker:**
   ```bash
   # Add Jenkins user to Docker group
   sudo usermod -aG docker jenkins

   # Restart Jenkins service
   sudo service jenkins restart
   ```

3. **Access Jenkins Web Interface:**
   - Open your browser and navigate to `http://localhost:8080`
   - For cloud installations (AWS/Azure/GCP), use the VM's public IP address
   - Ensure port 8080 is open in your firewall/security group

4. **Initial Jenkins Setup:**
   - Locate the initial admin password:
     ```bash
     sudo cat /var/lib/jenkins/secrets/initialAdminPassword
     ```
   - Enter the admin password in the Jenkins web interface
   - Install suggested plugins

#### 5.2 Install and Configure Tools

1. **Install Required Jenkins Plugins:**
   - Git plugin
   - Pipeline plugin
   - Docker plugin
   - Docker Pipeline plugin
   - Ansible plugin
   - Credentials Binding plugin

2. **Install Ansible:**
   ```bash
   # Update package list
   sudo apt update
   
   # Install dependencies
   sudo apt install software-properties-common
   
   # Add Ansible repository
   sudo apt-add-repository --yes --update ppa:ansible/ansible
   
   # Install Ansible
   sudo apt install ansible
   
   # Verify installation
   ansible --version
   ```

2. **Configure Tools in Jenkins:**
   - Go to "Manage Jenkins" → "Global Tool Configuration"
   - Configure Git:
     - Name: `git`
     - Path: `/usr/bin/git`
   - Configure Ansible:
     - Name: `ansible`
     - Path: `/usr/bin/ansible`
   - Save changes

#### 5.3 Configure Jenkins Credentials

1. **Generate GitHub Access Token:**
   - Log in to GitHub
   - Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a descriptive name (e.g., "jenkins-weather-app")
   - Select scopes:
     - `repo` (Full control of private repositories)
     - `admin:repo_hook` (Full control of repository hooks)
   - Click "Generate token"
   - Copy the token immediately (you won't see it again!)

2. **Add GitHub Credentials in Jenkins:**
   - Go to "Manage Jenkins" → "Manage Credentials"
   - Click on "System" → "Global credentials" → "Add Credentials"
   - Kind: Username with password
   - Scope: Global
   - Username: Your GitHub username
   - Password: Your GitHub access token
   - ID: `github_cred`
   - Description: "GitHub Access Token"
   - Click "Create"

3. **Add Docker Hub Credentials in Jenkins:**
   - Go to "Manage Jenkins" → "Manage Credentials"
   - Click on "System" → "Global credentials" → "Add Credentials"
   - Kind: Username with password
   - Scope: Global
   - Username: Your Docker Hub username
   - Password: Your Docker Hub access token
   - ID: `docker_hub_cred`
   - Description: "Docker Hub Access Token"
   - Click "Create"

#### 5.4 Sync with Remote Repository

Before setting up the Jenkins pipeline, push your changes to GitHub:

```bash
# Add all changes
git add .

# Commit changes
git commit -m "Add Docker Files , Jenkins configuration and pipeline setup"

# Push to main branch
git push origin main
```

#### 5.5 Create Jenkins Pipeline

1. **Create New Pipeline:**
   - Click "New Item"
   - Enter name: "weather-app-pipeline"
   - Select "Pipeline"
   - Click "OK"

2. **Configure Pipeline:**
   - In Pipeline section, select "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: Your GitHub repository URL
   - Credentials: Select github_cred
   - Branch Specifier: */main
   - Script Path: Jenkinsfile
   - Save

3. **Create Jenkinsfile:**
   Create a `Jenkinsfile` in your project root with the following content:
   ```groovy
   pipeline {
       agent any
       
       environment {
           DOCKERHUB_CREDENTIALS = credentials('docker_hub_cred')
       }
       
       stages {
           stage('Checkout SCM') {
               steps {
                   git branch: 'main',
                       credentialsId: 'github_cred',
                       url: 'https://github.com/[your-username]/WeatherApp_CICD.git'
               }
           }
           
           stage('Build Docker Image') {
               steps {
                   dir('app') {
                       sh 'docker compose build'
                   }
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

      }
       
   }
   ```

4. **Test Pipeline:**
   - Click "Build Now" to start the pipeline
   - Monitor the build progress in the Console Output
   - Verify that each stage completes successfully

### 6. SSH Key Configuration for Ansible

> **Note:** These SSH key configuration steps are ONLY needed in specific scenarios:
> 1. If you're using Vagrant machines provisioned with custom SSH keys
> 2. If you're deploying to cloud servers without a common SSH key
>
> You DON'T need these steps if:
> - You're using Vagrant machines with their default SSH setup (Vagrant generates unique private keys for each machine in `~/.vagrant.d/machines/<machine_name>/virtualbox/private_key`)
> - You're deploying to cloud servers that already have a common SSH key configured
>
> In these cases, you can use the existing keys for Ansible authentication.

#### For Vagrant Machines with Custom SSH Keys:

1. **Generate New SSH Key:**
   ```bash
   # Generate ED25519 SSH key
   ssh-keygen -ted25519 -C "Webservers-ssh Key-key generated by AbdullahAbaza"
   # When prompted, save as: id_ed25519_webservers_key
   ```

2. **Move Keys to SSH Directory:**
   ```bash
   mv id_ed25519_webservers_key id_ed25519_webservers_key.pub ./.ssh/
   ```

3. **Set Correct Permissions for Existing Keys:**
   ```bash
   # Set proper permissions for Vagrant machine keys
   chmod 600 ~/.ssh/machines/m01/virtualbox/private_key
   chmod 600 ~/.ssh/machines/m02/virtualbox/private_key
   ```

4. **Copy New Key to Target Machines:**
   ```bash
   # Copy to first machine
   cat ~/.ssh/id_ed25519_webservers_key.pub | ssh -i ~/.ssh/machines/m01/virtualbox/private_key vagrant@192.168.73.2 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

   # Copy to second machine
   cat ~/.ssh/id_ed25519_webservers_key.pub | ssh -i ~/.ssh/machines/m02/virtualbox/private_key vagrant@192.168.73.3 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
   ```

#### For Cloud Servers:
If you're deploying to cloud servers, ensure you have:
1. A single SSH key added to all target servers
2. The private key accessible to Jenkins
3. The key configured in Jenkins credentials for Ansible to use

### 7. Ansible Configuration

1. Update Inventory File (`Ansible/inventory`):
   ```ini
   [webservers]
   machine1 ansible_host=<vagrant-machine-1-ip> ansible_user=vagrant
   machine2 ansible_host=<vagrant-machine-2-ip> ansible_user=vagrant

   [all:vars]
   ansible_ssh_private_key_file=/path/to/private/key
   ```

2. Verify Ansible Connection:
   ```bash
   ansible all -m ping -i Ansible/inventory
   ```

### 8. Pipeline Execution

The Jenkins pipeline executes the following stages:

1. **Checkout**: 
   - Pulls code from GitHub repository

2. **Build Docker Image**:
   - Builds Docker image
   - Tags image with build number

3. **Push to Docker Hub**:
   - Authenticates with Docker Hub
   - Pushes image to Docker Hub repository

4. **Deploy**:
   - Runs Ansible playbook
   - Installs Docker on target machines
   - Pulls latest image
   - Runs containers

### 9. Verification

1. Check Container Status:
   ```bash
   # On each Vagrant machine
   docker ps
   ```

2. Access Application:
   - Machine 1: http://[vagrant-machine-1-ip]:5001
   - Machine 2: http://[vagrant-machine-2-ip]:5001

## Troubleshooting

1. **Jenkins Pipeline Fails**:
   - Check Jenkins console output
   - Verify credentials are correctly configured
   - Ensure Docker Hub repository exists

2. **Ansible Deployment Fails**:
   - Check SSH connectivity to Vagrant machines
   - Verify inventory file configuration
   - Check Ansible logs in Jenkins

3. **Container Issues**:
   - Check Docker logs on target machines
   - Verify Docker Hub permissions
   - Ensure ports are not in use

## Project Structure
```
WeatherApp_CICD/
├── app/                    # Flask application
├── Ansible/                # Ansible configurations
│   ├── inventory          # Target hosts inventory
│   └── playbook.yml       # Deployment playbook
├── Vagrant/               
│   └── Vagrantfile        # Vagrant configuration
├── Jenkinsfile            # Jenkins pipeline definition
├── docker-compose.yaml    # Docker Compose configuration
└── README.md
```

## Author

Abdullah Abaza

## References

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Ansible User Guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Docker Documentation](https://docs.docker.com/)
- [Vagrant Documentation](https://www.vagrantup.com/docs)
