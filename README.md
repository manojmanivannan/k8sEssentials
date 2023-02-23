


## Setup (windows) [POWERSHELL]
### Install & run minikube + helm
- `winget install minikube`
- `minikube start --driver=docker` (assuming docker-desktop is running)
- `minikube addons enable ingress` & `minikube tunnel`
- `choco install kubernetes-helm`

### Interact with cluster
- `alias kubectl="minikube kubectl --"` or `set kubectl="minikube kubectl --"`, then use `kubectl` to interact

### Stop & remove minikube
- `minikube stop`
- `minikube delete --all`

## Helm Package
1. Create a boiler plate with `helm create flaskedge`
2. Deploy chart `helm install flaskedge -n cloud --create-namespace .\flaskedge`
3. Uninstall chart `helm uninstall -n cloud flaskedge`
### Helm template validation
1. `cd helm-charts` & `helm template . --values ./values.yaml -s templates/deployment.yaml --name-template flaskedge --namespace cloud`
2. `helm template . --values ./values.yaml -s templates\job.yaml --name-template flaskedge --namespace cloud`


## Docker local dev
1. `& minikube -p minikube docker-env --shell powershell | Invoke-Expression` (setup minikube to run docker builds inside the cluster itself)
2. `docker build -t flaskedge:init .`
   1. `minikube ssh docker images` to list docker images
3. `docker run --rm --publish 8000:8000 flaskedge:init --bind 0.0.0.0 app:app` (to test)

## Kubectl Deploy
1. `kubectl apply -f .\helm-charts\templates\namespace.yaml`
2. `kubectl apply -f .\helm-charts\templates\deployment.yaml -f .\helm-charts\templates\service.yaml -f .\helm-charts\templates\ingress.yaml -f .\helm-charts\templates\job.yaml`
   1. `kubectl delete -f .\helm-charts\templates\deployment.yaml -f .\helm-charts\templates\service.yaml -f .\helm-charts\templates\ingress.yaml -f .\helm-charts\templates\job.yaml`
3. Access the application through the service `minikube -n cloud service --url flaskedge-web`