#!/bin/bash
set -euo pipefail

LOCAL_IMAGE=local/traefik_auth_proxy_config_generator

(cd ../../ && docker buildx build -t ${LOCAL_IMAGE} -f docker-only/config-generator/Dockerfile .)

export CONFIG_GENERATOR_DOCKER_IMAGE=${LOCAL_IMAGE}
export RUN_TYPE=local-do

(cd ../ && ansible-playbook -i tests/inventory tests/test.yml $@)