#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing..."
    # check if curl is installed
    if ! command -v curl &> /dev/null; then
        sudo apt install curl -y
    fi
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo groupadd docker
    sudo usermod -aG docker $USER
    newgrp docker
    sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
    sudo chmod g+rwx "$HOME/.docker" -R

else
    echo "Docker is already installed."
fi

# Check if Docker service is enabled
if ! systemctl is-active --quiet docker; then
    echo "Enabling Docker service..."
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
    sudo systemctl start docker
else
    echo "Docker service is already enabled."
fi

echo "Docker setup complete!"