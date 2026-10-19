# Jenkins Inbound Agent configured with Docker CLI, AWS CLI, Terraform, and Python
FROM jenkins/inbound-agent:alpine

USER root

RUN apk add --no-cache \
    docker-cli \
    docker-cli-compose \
    python3 \
    py3-pip \
    curl \
    git \
    bash \
    aws-cli \
    terraform

# Ensure jenkins user has permission to talk to docker socket
RUN addgroup -S docker 2>/dev/null || true && \
    addgroup jenkins docker

USER jenkins
