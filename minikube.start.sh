#!/bin/bash

TOTAL_ARG_COUNT=$#
ORIG_PARAMS=$*

function show_usage(){
  echo "Usage $0 [OPTIONS]"
  echo ""
  echo "      -load_daemon_img <true|false>       Enable loading docker image from docker daemon (outside minikube) default: false"
  echo "      -disable_build                      Disable docker build process. It should attempt to pull the image from dockerhub remote repo"
}

if [ $TOTAL_ARG_COUNT -lt 1 ]
then
  show_usage
  exit 1
fi

ATTEMPT_LOAD_FROM_DAEMON="false"
DOCKER_BUILD=1
FLAG=0

while [[ $# > 0 ]]
do
  key=$(echo "$1" | sed 's/\xe2\x80\x93/-/')
    case $key in
      -load_daemon_img) shift; ATTEMPT_LOAD_FROM_DAEMON=$1 ;;
      -flag) FLAG=1 ;;
      -disable_build) DOCKER_BUILD=0 ;;
      *)
        echo -e "Error: Invalid option $1\n"
        show_usage
        exit 1
        ;;
    esac
  shift
done


function verify_ingress(){
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
}

# Start Minikube
minikube start --listen-address='0.0.0.0' --ports 32080:32080

# Enable ingress
minikube addons enable ingress

# Wait for Ingress Controller to be ready
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# verify ingress health
verify_ingress

if [[ $ATTEMPT_LOAD_FROM_DAEMON == "true" ]]; then

  # Load image from docker daemon to minikube
  echo "Attempting to load docker image from docker daemon"
  minikube image load manojmanivannan18/flaskedge:master $HOME/.minikube/cache/images/manojmanivannan18_flaskedge_master
fi


# Build Docker images
eval $(minikube docker-env)

if [[ $DOCKER_BUILD -eq 1 ]]; then
  if docker images | grep -q flaskedge; then
    echo "Image manojmanivannan18/flaskedge:master present in minikube"
  else
    echo "Image manojmanivannan18/flaskedge:master not available in minikube, building..."
    docker build -t manojmanivannan18/flaskedge:master python-app/
    echo "Saving (cache) image for next time"
    minikube image save manojmanivannan18/flaskedge:master $HOME/.minikube/cache/images/manojmanivannan18_flaskedge_master --daemon=true
  fi
  echo "Setting python-app values to use local image"
  sed -i 's/pullPolicy:.*/pullPolicy: IfNotPresent/' ./python-app/charts/python-app/values.yaml
else
  echo "Docker image build disabled"
  echo "Setting python-app values to pull remote image"
  sed -i 's/pullPolicy:.*/pullPolicy: Always/' ./python-app/charts/python-app/values.yaml
fi


# Deploy Helm charts
helm install postgres ./postgres/charts/postgres
helm install dbjob ./dbjob/charts/dbjob
helm install python-app ./python-app/charts/python-app

# Wait for the ingress resource to be created and have an IP address assigned
echo "Waiting for ingress resource to be created and assigned an IP address..."
while true; do
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