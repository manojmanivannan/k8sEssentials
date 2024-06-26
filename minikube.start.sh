#!/bin/bash

# Start Minikube
minikube start

# Enable ingress
minikube addons enable ingress

# Build Docker images
eval $(minikube docker-env)
docker build -t manojmanivannan18/flaskedge:master python-app/


# Deploy configurations
# kubectl apply -f ./postgres/charts/postgres/templates/configMap.yaml
# kubectl apply -f ./python-app/charts/python-app/templates/secrets.yaml

# Deploy Helm charts
helm install postgres ./postgres/charts/postgres
helm install python-app ./python-app/charts/python-app
helm install dbjob ./dbjob/charts/dbjob

sleep 5

# Show the running application
echo "Application running at"
echo "$(minikube service --url python-app-service)"