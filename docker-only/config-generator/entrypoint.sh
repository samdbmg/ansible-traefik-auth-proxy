#!/bin/bash
set -euo pipefail

# List all env vars that start PROXY_
proxy_vars=$(compgen -A variable | grep ^PROXY)

extra_ansible_args=""

# For each variable, create an Ansible extravar CLI flag with the lowercased version
for var in ${proxy_vars}; do
    lowercase_var=${var,,}
    var_flag="-e ${lowercase_var}=${!var} "
    extra_ansible_args+=${var_flag};
done

# Run the playbook
ansible-playbook -i , /ansible/playbook.yml ${extra_ansible_args} $@
