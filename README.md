


## Setup (windows) [POWERSHELL]
### Install,Setup & Run minikube
- `winget install minikube`
- `minikube start --driver=docker` (assuming docker-desktop is running)
- `& minikube -p minikube docker-env --shell powershell | Invoke-Expression` (setup minikube to run docker builds inside the cluster itself)
- `minikube addons enable ingress` 


### Interact with cluster
- `alias kubectl="minikube kubectl --"` or `set kubectl="minikube kubectl --"`, then use `kubectl` to interact

### Stop & Remove minikube
- `minikube stop`
- `minikube delete --all`

## Docker Local Dev
1. `& minikube -p minikube docker-env --shell powershell | Invoke-Expression` (setup minikube to run docker builds inside the cluster itself)
2. `docker build -t manojmanivannan18/flaskedge:master .`
   1. `minikube ssh docker images` to list docker images
3. `docker run --rm --publish 8000:8000 manojmanivannan18/flaskedge:master --bind 0.0.0.0 app:app` (to test manually)
   

### Helm Template Validation & Packaging
Install helm `choco install kubernetes-helm`
1. `cd helm` & `helm template . --values ./values.yaml -s templates/deployment.yaml --name-template flaskedge --namespace cloud`
2. `helm template . --values ./values.yaml -s templates\job.yaml --name-template flaskedge --namespace cloud`
3. `helm upgrade --install --create-namespace --namespace cloud flaskedge helm/`
   - `kubectl get pods,jobs,service,ingress -n cloud` ( to install from local & check if everything is up)
4. `helm repo add k8sessentials https://raw.githubusercontent.com/manojmanivannan/k8sEssentials/gh-pages` to add the helm repo to any setup


## Kubectl Manual Deploy
1. `kubectl apply -f .\helm\templates\namespace.yaml`
2. `kubectl apply -f .\helm\templates\deployment.yaml -f .\helm\templates\service.yaml -f .\helm\templates\ingress.yaml -f .\helm\templates\job.yaml`
   1. `kubectl delete -f .\helm\templates\deployment.yaml -f .\helm\templates\service.yaml -f .\helm\templates\ingress.yaml -f .\helm\templates\job.yaml`


Access the application through the service `minikube -n cloud service --url flaskedge-web`

### Application ToDo
[x] Push the image to dockerhub
[ ] Enable docker tags for all branches
[x] Push helm chats to github container registry
[ ] Push helm charts with auto tags instead of variable from ./helm/Chart.yaml
[ ] Enable helm chats for all branches
