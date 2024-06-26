# k8s Demo Application

This repo shows a simple application running in minikube. It uses typical entities like deployment, services, ingress, persistent volumes, etc like in production.

## Run locally
Given you have minikube installed and you are on linux machine, simply run `./minikube.start.sh`


### Access from Browser
Open the URL generated from `echo $(minikube service --url python-app-service)`

Append DNS entry to `/etc/hosts` using `echo "$(minikube ip)  python-app.demo.com" >> /etc/hosts`

So you can access the application from browser using `python-app.demo.com`

### Verify

once the minikube start script is finished, verify you see output

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

#### Postgres
`psql -U admin -d house`