#!/bin/bash

# Uninstall Helm charts
helm uninstall python-app
helm uninstall postgres
helm uninstall dbjob

# Remove Docker containers
eval $(minikube docker-env)
docker rm -f $(docker ps -a -q --filter "name=python-app")
docker rm -f $(docker ps -a -q --filter "name=postgres")

# Remove Docker images
docker rmi -f manojmanivannan18/flaskedge:master
docker rmi -f postgres:12.7

# Delete Minikube cluster
minikube stop
minikube delete --all

# Optional: Clean up dangling images and volumes
docker system prune -f
docker volume prune -f

# reset docker CLI to default
eval $(minikube docker-env -u)

echo "Cleanup complete!"
