
- [Setup (windows) \[POWERSHELL\]](#setup-windows-powershell)
  - [Install,Setup \& Run minikube](#installsetup--run-minikube)
  - [Interact with cluster](#interact-with-cluster)
  - [Stop \& Remove minikube](#stop--remove-minikube)
- [Docker Local Dev](#docker-local-dev)
- [Helm](#helm)
  - [Helm Template Validation](#helm-template-validation)
- [Application ToDo](#application-todo)


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
   

## Helm
Install helm `choco install kubernetes-helm`
1. Add the helm repo to cluster
   - `helm repo add k8sessentials https://raw.githubusercontent.com/manojmanivannan/k8sEssentials/gh-pages` 
2. Install the chart 
   - `helm upgrade --install --create-namespace --namespace cloud flaskedge k8sessentials/flaskedge`

### Helm Template Validation
1. `cd helm` & `helm template . --values ./values.yaml -s templates/deployment.yaml --name-template flaskedge --namespace cloud`
2. `helm template . --values ./values.yaml -s templates\job.yaml --name-template flaskedge --namespace cloud`
3. `helm upgrade --install --create-namespace --namespace cloud flaskedge .\helm\`
4. `kubectl get pods,jobs,service,ingress -n cloud` ( to install from local & check if everything is up)


**Access the application through the service `minikube -n cloud service --url flaskedge-web`**

## Application ToDo
- [x] Push the image to dockerhub
- [ ] Enable docker tags for all branches
- [ ] Create separate charts for the application and database
- [x] Push helm chats to github container registry
- [ ] Push helm charts with auto tags instead of variable from ./helm/Chart.yaml
- [ ] Enable helm chats for all branches
