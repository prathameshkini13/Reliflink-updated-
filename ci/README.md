# Local DevSecOps Pipeline Stack Setup

This guide walks through reproducing the complete local CI/CD stack (Jenkins, SonarQube, and Trivy) using plain Docker commands without requiring Docker Compose.

---

## 1. Create Dedicated Docker Bridge Network

```bash
docker network create relief-ci-net
```

---

## 2. Start SonarQube Community Edition

```bash
docker volume create sonarqube-data
docker volume create sonarqube-extensions

docker run -d --name sonarqube \
  --network relief-ci-net \
  -p 9000:9000 \
  -v sonarqube-data:/opt/sonarqube/data \
  -v sonarqube-extensions:/opt/sonarqube/extensions \
  sonarqube:community
```

- Access SonarQube at: `http://localhost:9000` (Default credentials: `admin` / `admin`).
- Generate an authentication token in **Administration -> Security -> Users -> Tokens** and save it.

---

## 3. Start Jenkins Controller

```bash
docker volume create jenkins-home

docker run -d --name jenkins \
  --network relief-ci-net \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins-home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -u root \
  jenkins/jenkins:lts-jdk17
```

- Retrieve initial admin unlock password:
  ```bash
  docker logs jenkins | grep -A 2 "Please use the following password"
  ```
- Install recommended plugins + **SonarQube Scanner for Jenkins** + **HTML Publisher** + **Warnings Next Generation**.
- Configure SonarQube Server in **Manage Jenkins -> System**:
  - Name: `sonarqube`
  - Server URL: `http://sonarqube:9000`
  - Server authentication token: Secret text credential pointing to your SonarQube token.

---

## 4. Run Trivy Vulnerability Scanners Locally

### Filesystem & Secret Scan
```bash
docker run --rm -v $(pwd):/workspace -w /workspace aquasec/trivy:latest fs .
```

### Container Image Vulnerability Scan
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL disaster-relief-allocator:latest
```

---

## 5. Execute Pipeline Job
1. Create a **New Item** -> **Pipeline**.
2. Select **Pipeline script from SCM** -> **Git**.
3. Set Repository URL to your repo clone and Branch to `main`.
4. Trigger **Build Now**.
