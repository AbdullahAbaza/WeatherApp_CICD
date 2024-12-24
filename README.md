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

### 4. Jenkins Setup

1. Install Required Jenkins Plugins:
   - Git plugin
   - Pipeline plugin
   - Docker Pipeline plugin
   - Ansible plugin
   - Credentials Binding plugin

2. Configure Jenkins Credentials:
   - Add GitHub credentials (username/token) with ID 'github_cred'
   - Add Docker Hub credentials with ID 'docker_hub_cred'
   - Add SSH private key for Ansible with ID 'ansible_key'

3. Create New Pipeline:
   - Click "New Item"
   - Select "Pipeline"
   - Name it "weather-app-pipeline"
   - In Pipeline section, select "Pipeline script from SCM"
   - Set SCM to Git
   - Add repository URL and credentials
   - Set branch to */main
   - Save

### 5. Docker Configuration

1. Dockerfile Structure:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY app/ .
   RUN pip install -r requirements.txt
   EXPOSE 5001
   CMD ["python", "app.py"]
   ```

2. Build and Test Locally:
   ```bash
   docker build -t weather-app .
   docker run -d -p 5001:5001 weather-app
   ```

### 6. Ansible Configuration

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

### 7. Pipeline Execution

The Jenkins pipeline (`Jenkinsfile`) executes the following stages:

1. **Checkout**: 
   - Pulls code from GitHub repository

2. **Build**:
   - Builds Docker image
   - Tags image with build number

3. **Push**:
   - Authenticates with Docker Hub
   - Pushes image to Docker Hub repository

4. **Deploy**:
   - Runs Ansible playbook
   - Installs Docker on target machines
   - Pulls latest image
   - Runs containers

### 8. Verification

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
