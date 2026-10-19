// CI/CD DevSecOps Declarative Pipeline
// Project: Modular Design of a Disaster Relief Resource Allocation Platform
// Candidate: Kini Prathamesh Prakash (124BTCS1057) | Course Outcome: CO2 | SDG 11
pipeline {
  agent any

  parameters {
    string(name: 'BRANCH', defaultValue: 'main', description: 'Git branch to build and test')
  }

  environment {
    IMAGE_NAME    = 'disaster-relief-allocator'
    IMAGE_TAG     = "${env.BUILD_NUMBER}"
    REPO_URL      = 'https://github.com/prathamesh-kini/disaster-relief-allocation-devsecops.git'
    AWS_REGION    = 'ap-south-1'
    ECR_REGISTRY  = '123456789012.dkr.ecr.ap-south-1.amazonaws.com'
    SONAR_PROJECT = 'disaster-relief-allocation-devsecops'
    TRIVY_BIN     = 'docker run --rm -v trivy-cache:/root/.cache/trivy -v "$PWD":/workspace -w /workspace aquasec/trivy:latest'
  }

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '15'))
    disableConcurrentBuilds()
  }

  stages {
    stage('Checkout') {
      steps {
        echo "=== [1/11] Checking out source repository ==="
        git branch: "${params.BRANCH}", url: "${REPO_URL}"
        sh 'mkdir -p reports evidence/raw'
      }
    }

    stage('Static Code Linting') {
      steps {
        echo "=== [2/11] Running Flake8 static analysis & style checks ==="
        sh '''
          docker run --rm -v "$PWD":/w -w /w python:3.12-slim sh -c "
            pip install -q flake8 &&
            flake8 app/ tests/ --max-line-length=120 --exclude=app/static/*"
        '''
      }
    }

    stage('Unit Tests & Coverage') {
      steps {
        echo "=== [3/11] Running pytest unit test suite & coverage analysis ==="
        sh '''
          docker run --rm -v "$PWD":/w -w /w python:3.12-slim sh -c "
            pip install -q -r requirements-dev.txt &&
            python -m pytest -v --cov=app --cov-report=xml:reports/coverage.xml --cov-report=term --junitxml=reports/junit.xml"
        '''
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/junit.xml'
        }
      }
    }

    stage('SonarQube SAST Scan') {
      steps {
        echo "=== [4/11] Executing SonarQube Static Application Security Testing ==="
        withSonarQubeEnv('sonarqube') {
          sh '''
            docker run --rm --network host -e SONAR_HOST_URL -e SONAR_TOKEN="${SONAR_AUTH_TOKEN:-$SONAR_TOKEN}" \
              -v "$PWD":/usr/src sonarsource/sonar-scanner-cli:latest \
              -Dsonar.projectKey=${SONAR_PROJECT} \
              -Dsonar.sources=app \
              -Dsonar.tests=tests \
              -Dsonar.python.coverage.reportPaths=reports/coverage.xml \
              -Dsonar.working.directory=/usr/src/.scannerwork
          '''
        }
      }
    }

    stage('Quality Gate') {
      steps {
        echo "=== [5/11] Evaluating SonarQube Quality Gate Status ==="
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }

    stage('Trivy SCA & Secrets Scan') {
      steps {
        echo "=== [6/11] Scanning repository filesystem & dependencies for CVEs/secrets ==="
        sh """
          ${TRIVY_BIN} fs --exit-code 0 --format json --output reports/trivy-fs.json .
          ${TRIVY_BIN} fs --exit-code 1 --severity HIGH,CRITICAL --security-checks vuln,secret .
        """
      }
    }

    stage('Docker Image Build') {
      steps {
        echo "=== [7/11] Building multi-stage hardened container image ==="
        sh """
          docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
        """
      }
    }

    stage('Trivy Container Scan') {
      steps {
        echo "=== [8/11] Scanning container image for vulnerabilities ==="
        sh """
          ${TRIVY_BIN} image --exit-code 0 --format json --output reports/trivy-image-final.json ${IMAGE_NAME}:${IMAGE_TAG}
          ${TRIVY_BIN} image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed ${IMAGE_NAME}:${IMAGE_TAG}
        """
      }
    }

    stage('Push to AWS ECR') {
      when {
        branch 'main'
      }
      steps {
        echo "=== [9/11] Authenticating and pushing image to AWS ECR ==="
        sh """
          aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
          docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
          docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ECR_REGISTRY}/${IMAGE_NAME}:latest
          docker push ${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
          docker push ${ECR_REGISTRY}/${IMAGE_NAME}:latest
        """
      }
    }

    stage('Terraform AWS Provision') {
      when {
        branch 'main'
      }
      steps {
        echo "=== [10/11] Provisioning cloud infrastructure via Terraform ==="
        dir('terraform') {
          sh '''
            terraform init -input=false
            terraform validate
            terraform plan -out=tfplan -input=false
            terraform apply -input=false -auto-approve tfplan
          '''
        }
      }
    }

    stage('DAST Smoke Test') {
      steps {
        echo "=== [11/11] Dynamic verification & security header validation ==="
        sh """
          docker run -d --name smoke-test-app -p 8080:8000 ${IMAGE_NAME}:${IMAGE_TAG}
          sleep 5
          curl -f -s http://localhost:8080/health | grep '"status":"healthy"'
          curl -s -I http://localhost:8080/ | grep 'X-Content-Type-Options: nosniff'
          curl -s -I http://localhost:8080/ | grep 'X-Frame-Options: DENY'
          docker stop smoke-test-app && docker rm smoke-test-app
        """
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'reports/*, diagrams/*.png', allowEmptyArchive: true
      cleanWs notFailBuild: true
    }
    success {
      echo "=== SUCCESS: DevSecOps pipeline completed with all security gates passed ==="
    }
    failure {
      echo "=== FAILURE: DevSecOps pipeline failed a security or quality gate ==="
    }
  }
}
