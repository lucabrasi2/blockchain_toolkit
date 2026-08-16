###############################################################################
#
# Universal Blockchain Platform (UBP)
#
# Makefile
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

PYTHON := python3
PIP := pip3
VENV := venv
DOCKER := docker
COMPOSE := docker compose

###############################################################################
# Default
###############################################################################

.DEFAULT_GOAL := help

###############################################################################
# Help
###############################################################################

help:
	@echo ""
	@echo "==============================================================="
	@echo " Universal Blockchain Platform (UBP)"
	@echo "==============================================================="
	@echo ""
	@echo "Available Commands"
	@echo ""
	@echo "  make install      Install production dependencies"
	@echo "  make dev          Install development dependencies"
	@echo "  make venv         Create virtual environment"
	@echo "  make run          Run UBP"
	@echo "  make test         Execute tests"
	@echo "  make lint         Run flake8"
	@echo "  make format       Format code with black"
	@echo "  make docker       Build Docker image"
	@echo "  make up           Start Docker containers"
	@echo "  make down         Stop Docker containers"
	@echo "  make restart      Restart Docker containers"
	@echo "  make logs         View Docker logs"
	@echo "  make clean        Remove caches"
	@echo "  make deploy       Execute deployment script"
	@echo "  make setup        Execute server setup script"
	@echo ""

###############################################################################
# Python
###############################################################################

venv:
	$(PYTHON) -m venv $(VENV)

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements-dev.txt

run:
	$(PYTHON) app.py

###############################################################################
# Testing
###############################################################################

test:
	pytest

coverage:
	pytest --cov

###############################################################################
# Code Quality
###############################################################################

format:
	black .

isort:
	isort .

lint:
	flake8 .

typecheck:
	mypy .

security:
	bandit -r .

###############################################################################
# Docker
###############################################################################

docker:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

###############################################################################
# Deployment
###############################################################################

setup:
	chmod +x setup.sh
	sudo ./setup.sh

deploy:
	chmod +x deploy.sh
	./deploy.sh

###############################################################################
# Cleanup
###############################################################################

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

###############################################################################
# End of File
###############################################################################
