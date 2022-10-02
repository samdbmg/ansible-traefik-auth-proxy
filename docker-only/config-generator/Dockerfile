# syntax=docker/dockerfile:1.2

FROM python:3.10

RUN pip install ansible

# Note: This should be built with the repository root as the context so the paths work
WORKDIR /ansible
COPY docker-only/config-generator/playbook.yml /ansible/playbook.yml

ADD . /ansible/traefik_auth_proxy

CMD ansible-playbook -i , /ansible/playbook.yml
