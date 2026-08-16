#!/bin/bash

###############################################################################
#
# Universal Blockchain Platform (UBP)
#
# setup.sh
#
# Purpose
# -------
# Prepare a clean Ubuntu Server for running the Universal Blockchain Platform.
#
# This script installs all operating system dependencies required before
# deploying UBP.
#
# Author:
#     Jaramogi Diddy
#
# Project:
#     Universal Blockchain Platform (UBP)
#
# Version:
#     2.0 Enterprise
#
###############################################################################

set -e

###############################################################################
# Colours
###############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

###############################################################################
# Banner
###############################################################################

echo
echo "==============================================================="
echo "      Universal Blockchain Platform (UBP)"
echo "           Production Server Setup"
echo "==============================================================="
echo

###############################################################################
# Helper Functions
###############################################################################

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ OK ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

###############################################################################
# Root Check
###############################################################################

if [[ "$EUID" -ne 0 ]]; then
    print_error "Please run this script as root."

    echo
    echo "Example:"
    echo

    echo "sudo ./setup.sh"

    echo
    exit 1
fi

print_success "Running as root."

###############################################################################
# Ubuntu Version Check
###############################################################################

print_step "Checking operating system..."

if [[ ! -f /etc/os-release ]]; then

    print_error "Unsupported operating system."

    exit 1

fi

source /etc/os-release

echo "Detected: $PRETTY_NAME"

if [[ "$ID" != "ubuntu" ]]; then

    print_warning "UBP is officially tested on Ubuntu."

fi

print_success "Operating system verified."

###############################################################################
# Update System
###############################################################################

print_step "Updating package repository..."

apt-get update

print_success "Package index updated."

###############################################################################
# Upgrade Packages
###############################################################################

print_step "Upgrading installed packages..."

apt-get upgrade -y

print_success "System upgraded."

###############################################################################
# Install Base Packages
###############################################################################

print_step "Installing required system packages..."

apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    git \
    unzip \
    zip \
    software-properties-common \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    net-tools \
    htop \
    jq \
    nano \
    vim \
    tree \
    ufw

print_success "Base packages installed."

###############################################################################
# Install Python
###############################################################################

print_step "Installing Python..."

apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

print_success "Python installed."

###############################################################################
# Upgrade pip
###############################################################################

print_step "Upgrading pip..."

python3 -m pip install --upgrade pip

print_success "pip upgraded."

###############################################################################
# Install PostgreSQL Client
###############################################################################

print_step "Installing PostgreSQL client..."

apt-get install -y \
    postgresql-client \
    libpq-dev

print_success "PostgreSQL client installed."

###############################################################################
# Install SQLite
###############################################################################

print_step "Installing SQLite..."

apt-get install -y sqlite3

print_success "SQLite installed."

###############################################################################
# Verify Python
###############################################################################

print_step "Verifying Python installation..."

python3 --version

pip3 --version

print_success "Python verified."

###############################################################################
# End Part 1
###############################################################################
###############################################################################
# Install Docker
###############################################################################

print_step "Installing Docker..."

if command -v docker >/dev/null 2>&1; then

    print_warning "Docker is already installed."

else

    curl -fsSL https://get.docker.com | sh

fi

print_success "Docker installed."

###############################################################################
# Enable Docker
###############################################################################

print_step "Enabling Docker service..."

systemctl enable docker

systemctl start docker

print_success "Docker service enabled."

###############################################################################
# Verify Docker
###############################################################################

print_step "Verifying Docker..."

docker --version

print_success "Docker verified."

###############################################################################
# Install Docker Compose
###############################################################################

print_step "Installing Docker Compose..."

if docker compose version >/dev/null 2>&1; then

    print_warning "Docker Compose already installed."

else

    mkdir -p /usr/local/lib/docker/cli-plugins

    curl -SL \
        https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
        -o /usr/local/lib/docker/cli-plugins/docker-compose

    chmod +x \
        /usr/local/lib/docker/cli-plugins/docker-compose

fi

docker compose version

print_success "Docker Compose installed."

###############################################################################
# Install Nginx
###############################################################################

print_step "Installing Nginx..."

apt-get install -y nginx

systemctl enable nginx

systemctl start nginx

print_success "Nginx installed."

###############################################################################
# Verify Nginx
###############################################################################

print_step "Verifying Nginx..."

nginx -v

systemctl status nginx --no-pager

print_success "Nginx verified."

###############################################################################
# Install Redis
###############################################################################

print_step "Installing Redis..."

apt-get install -y redis-server

systemctl enable redis-server

systemctl start redis-server

print_success "Redis installed."

###############################################################################
# Verify Redis
###############################################################################

print_step "Verifying Redis..."

redis-server --version

redis-cli ping

print_success "Redis verified."

###############################################################################
# Configure Firewall
###############################################################################

print_step "Configuring firewall..."

ufw allow OpenSSH

ufw allow 80/tcp

ufw allow 443/tcp

ufw allow 8000/tcp

ufw allow 8001/tcp

ufw --force enable

print_success "Firewall configured."

###############################################################################
# Create UBP User
###############################################################################

print_step "Creating UBP service user..."

if id "ubp" >/dev/null 2>&1; then

    print_warning "User 'ubp' already exists."

else

    useradd \
        --system \
        --create-home \
        --shell /bin/bash \
        ubp

fi

print_success "UBP user ready."

###############################################################################
# Create Application Directory
###############################################################################

print_step "Creating application directories..."

mkdir -p /opt/ubp

mkdir -p /opt/ubp/logs

mkdir -p /opt/ubp/backups

mkdir -p /opt/ubp/data

mkdir -p /opt/ubp/config

print_success "Application directories created."

###############################################################################
# Set Permissions
###############################################################################

print_step "Setting permissions..."

chown -R ubp:ubp /opt/ubp

chmod -R 755 /opt/ubp

print_success "Permissions configured."

###############################################################################
# Install Git LFS (Optional)
###############################################################################

print_step "Installing Git LFS..."

apt-get install -y git-lfs

git lfs install

print_success "Git LFS installed."

###############################################################################
# Verify Internet Connectivity
###############################################################################

print_step "Checking Internet connectivity..."

if ping -c 2 github.com >/dev/null 2>&1; then

    print_success "Internet connectivity verified."

else

    print_warning "Unable to reach github.com."

fi

###############################################################################
# Verify Disk Space
###############################################################################

print_step "Checking disk space..."

df -h /

print_success "Disk space checked."

###############################################################################
# Verify Memory
###############################################################################

print_step "Checking memory..."

free -h

print_success "Memory checked."

###############################################################################
# End Part 2
###############################################################################
###############################################################################
# Verify Installed Software
###############################################################################

print_step "Performing final verification..."

echo
echo "---------------------------------------------------------------"
echo "Installed Software"
echo "---------------------------------------------------------------"

echo
echo "Python:"
python3 --version

echo
echo "Pip:"
pip3 --version

echo
echo "Git:"
git --version

echo
echo "Docker:"
docker --version

echo
echo "Docker Compose:"
docker compose version

echo
echo "Nginx:"
nginx -v 2>&1

echo
echo "Redis:"
redis-server --version

echo
echo "SQLite:"
sqlite3 --version

echo
echo "---------------------------------------------------------------"

print_success "Software verification completed."

###############################################################################
# Verify Services
###############################################################################

print_step "Checking system services..."

services=(
    docker
    nginx
    redis-server
)

for service in "${services[@]}"
do
    if systemctl is-active --quiet "$service"; then

        print_success "$service is running."

    else

        print_warning "$service is NOT running."

    fi
done

###############################################################################
# Docker Permissions
###############################################################################

print_step "Configuring Docker permissions..."

if getent group docker >/dev/null 2>&1; then

    usermod -aG docker ubp

    print_success "UBP user added to Docker group."

else

    print_warning "Docker group not found."

fi

###############################################################################
# Create Default Log File
###############################################################################

print_step "Creating log files..."

touch /opt/ubp/logs/ubp.log

touch /opt/ubp/logs/error.log

touch /opt/ubp/logs/access.log

chown -R ubp:ubp /opt/ubp/logs

print_success "Log files created."

###############################################################################
# Create Backup Directory
###############################################################################

print_step "Preparing backup directory..."

mkdir -p /opt/ubp/backups

chown -R ubp:ubp /opt/ubp/backups

print_success "Backup directory ready."

###############################################################################
# Final Summary
###############################################################################

echo
echo "==============================================================="
echo " Universal Blockchain Platform"
echo " Production Environment Ready"
echo "==============================================================="
echo

echo "Installation Summary"

echo
echo "✔ Ubuntu verified"
echo "✔ System updated"
echo "✔ Python installed"
echo "✔ Pip installed"
echo "✔ Git installed"
echo "✔ Build tools installed"
echo "✔ SQLite installed"
echo "✔ PostgreSQL client installed"
echo "✔ Docker installed"
echo "✔ Docker Compose installed"
echo "✔ Nginx installed"
echo "✔ Redis installed"
echo "✔ Firewall configured"
echo "✔ UBP service account created"
echo "✔ Application directories created"
echo "✔ Logging configured"

echo
echo "Application Directory"

echo
echo "    /opt/ubp"

echo
echo "Log Directory"

echo
echo "    /opt/ubp/logs"

echo
echo "Backup Directory"

echo
echo "    /opt/ubp/backups"

echo
echo "==============================================================="

###############################################################################
# Next Steps
###############################################################################

echo
echo "Next Steps"
echo

echo "1. Clone the repository"

echo
echo "   git clone <repository-url>"

echo
echo "2. Enter the project"

echo
echo "   cd blockchain_toolkit"

echo
echo "3. Copy the environment template"

echo
echo "   cp .env.example .env"

echo
echo "4. Update your API keys"

echo
echo "5. Deploy UBP"

echo
echo "   ./deploy.sh"

echo
echo "==============================================================="

print_success "Server setup completed successfully."

echo
echo "A reboot is recommended before deployment."

echo
echo "Reboot now? (y/N)"

read -r answer

if [[ "$answer" =~ ^[Yy]$ ]]; then

    reboot

fi

exit 0

###############################################################################
# End of File
###############################################################################