#!/bin/bash

# Start Minikube
minikube start

# Enable ingress
minikube addons enable ingress

# Build Docker images
eval $(minikube docker-env)
docker build -t manojmanivannan18/flaskedge:master python-app/

# Deploy Helm charts
helm install postgres ./postgres/charts/postgres
helm install python-app ./python-app/charts/python-app
helm install dbjob ./dbjob/charts/dbjob

# Wait for the ingress resource to be created and have an IP address assigned
echo "Waiting for ingress resource to be created and assigned an IP address..."
while : ; do
  INGRESS_IP=$(kubectl get ingress -o 'jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}"' 2>/dev/null)
  if [ $? -eq 0 ] && [ -n "$INGRESS_IP" ]; then
    break
  fi
  echo "Waiting for ingress IP..."
  sleep 1
done

# Wait for the readiness of the python-app pod
echo "Waiting for python-app pod to be ready..."
kubectl wait --for=condition=ready pod -l app=python-app --timeout=120s

# Show the running application
echo "Application running at"
minikube service --url python-app-service