# k8s Demo Application

This repo shows a simple application running in minikube. It uses typical entities like deployment, services, ingress, persistent volumes, etc like in production.

### Dependencies
1. minikube
2. helm
3. kubectl

## Run locally

Given you have minikube installed and you are on linux machine, simply run `./minikube.start.sh`. Each time, the docker image is built inside the minikube cluster, in order avoid it, build outside minikube,
`docker build -t manojmanivannan18/flaskedge:master python-app/`
The start script will load the image during the script


### Access from Browser

Open the URL generated from `echo $(minikube service --url python-app-service)` or `localhost:32080`

#### Optional Domain
Append DNS entry to `/etc/hosts` using `echo "$(minikube ip)  python-app.demo.com" >> /etc/hosts`

So you can access the application from browser using `python-app.demo.com`

### Verify

once the minikube start script is finished, verify you see output

Command: `curl --resolve "0.0.0.0:32080:$( minikube ip )" -i http://0.0.0.0:32080`

Or if you used the optional domain:

Command: `curl --resolve "python-app.demo.com:80:$( minikube ip )" -i http://python-app.demo.com`

Output: 
```bash
HTTP/1.1 302 FOUND
Date: Wed, 26 Jun 2024 13:24:40 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 199
Connection: keep-alive
Location: /rooms

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/rooms">/rooms</a>. If not, click the link.
```

Since the minikube exposed to localhost on the host machine, you can even access the application from remote servers using the host machine's IP:32080

#### Postgres
`psql -U admin -d house`

## Application ToDo
- [x] Push the image to dockerhub
- [ ] Enable docker tags for all branches
- [x] Create separate charts for the application and database
- [x] Push helm chats to github container registry
- [ ] Push helm charts with auto tags instead of variable from Chart.yaml
- [ ] Enable helm charts for all branches