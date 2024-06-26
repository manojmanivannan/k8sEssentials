#!/bin/bash

# Start Minikube
minikube start

# Enable ingress
minikube addons enable ingress

# Make sure ingress is healthy

# Namespace and service names
NAMESPACE="ingress-nginx"
SERVICE="ingress-nginx-controller-admission"

# Maximum number of attempts
MAX_ATTEMPTS=30
attempt=1

echo "Waiting for the $SERVICE service to become available..."

while (( attempt <= MAX_ATTEMPTS )); do
  # Check if the service is available
  if kubectl get svc -n $NAMESPACE $SERVICE &> /dev/null; then
    # Check if the endpoints are ready
    if kubectl get endpoints -n $NAMESPACE $SERVICE -o 'jsonpath="{.subsets[*].addresses[*].ip}"' &> /dev/null; then
      echo "$SERVICE is available."
      break
    fi
  fi

  echo "Attempt $attempt/$MAX_ATTEMPTS: $SERVICE is not yet available. Waiting for 5 seconds..."
  (( attempt++ ))
  sleep 5
done

if [[ $attempt -eq $MAX_ATTEMPTS ]]
then
echo "ERROR: $SERVICE did not become available after $((MAX_ATTEMPTS * DELAY)) seconds."
exit 1
fi

# Build Docker images
eval $(minikube docker-env)

if docker images | grep -q flaskedge ;
then
  echo "Image manojmanivannan18/flaskedge:master already present"
else
  docker build -t manojmanivannan18/flaskedge:master python-app/
fi




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