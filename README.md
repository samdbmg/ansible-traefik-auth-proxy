Traefik Auth Proxy
==================

[Ansible Role](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html) to set up the [Traefik](https://traefik.io/traefik/) HTTP reverse proxy running in Docker, along with https://github.com/thomseddon/traefik-forward-auth to allow sites to be secured using OIDC/OAuth2 and provide single sign-on (SSO).

Features:
- Automatic issuing of TLS certificates with LetsEncrypt et al (thanks Traefik!)
- Easy integration with OpenID Connect & OAuth2 providers or Google for auth (thanks [thomseddon/traefik-forward-auth](https://github.com/thomseddon/traefik-forward-auth))
- A proxy for the Docker socket to avoid exposing it directly to Traefik
- The Traefik Dashboard deployed behind the chosen auth provider
- [Auth Host Mode](https://github.com/thomseddon/traefik-forward-auth#auth-host-mode) so multiple sites can be hosted by the same Traefik instance without and it can be allow-listed once to get SSO.
- Generates all the required config files from Ansible variables


Requirements
------------

Docker needs to be available on your target (as does docker-compose) and the `docker` and `requests` Python modules.

Also requires the [community.docker](https://docs.ansible.com/ansible/latest/collections/community/docker/index.html) collection in a version >= 3.6.0.

Role Variables
--------------

- `proxy_domain` **(Required)**: The domain that this proxy serves subdomains of, _e.g._ `myserver.example.com`.
- `proxy_letsencrypt_email` **(Required)**: Email address to be associated with the LetsEncrypt certificates that will be issued.
- `proxy_enable_auth: true`: Should the forward-auth proxy be enabled?
- `proxy_use_le_prod: false`: Should the production LetsEncrypt be used (instead of staging).
- `proxy_network_name: traefik`: Name of the [Docker network](https://docs.docker.com/compose/networking/) that will be used by Traefik to pass traffic to containers.
- `proxy_dashboard_domain: dashboard.{{ proxy_domain }}`: Domain on which the [Traefik Dashboard](https://doc.traefik.io/traefik/operations/dashboard/) appears (only if auth is enabled). Set to an empty string to disable dashboard.
- `proxy_cert_method: http`: Which [challenge](https://letsencrypt.org/docs/challenge-types/) to use for verifying domain ownership when issuing certificates. The other option is `dns`.
- `proxy_cert_dns_provider:`: Which DNS provider is in use, from https://doc.traefik.io/traefik/https/acme/#providers. Required if using `dns` for `proxy_cert_method`.
- `proxy_dns_provider_env_vars: []`: If using `dns` for `proxy_cert_method`, the env vars needed (e.g. access keys), as - KEY=VALUE pairs (see https://doc.traefik.io/traefik/https/acme/#providers for list of env vars).
- `proxy_oauth_provider: oidc`: Chosen OAuth provider. One of `google` or `oidc` (see also `default-provider` option in https://github.com/thomseddon/traefik-forward-auth#option-details).
- `proxy_auth_provider_env_vars: {}`: The set of options to pass to the auth provider, from https://github.com/thomseddon/traefik-forward-auth/wiki/Provider-Setup.
- `proxy_requires_http: false`: Set to true to enable HTTP endpoints with traefik (rather than just redirecting to https).
- `proxy_rules: []`: List of rules to allow more fine-grained control of auth actions
- `proxy_config_dir: /etc/traefik_proxy`: Where the config files for Traefik will be written to.
- `proxy_docker_dir: /etc/traefik_proxy`: Where the Docker Compose files will be written to.

Example Playbook
----------------

```yaml
- name: Set up reverse proxying with Traefik
  hosts: webserver
  roles:
    - name: samdbmg.traefik-auth-proxy
      vars:
        proxy_domain: myserver.example.com
        proxy_letsencrypt_email: me@example.com
        proxy_use_le_prod: true
        proxy_oauth_provider: oidc
        proxy_auth_provider_env_vars:
            PROVIDERS_OIDC_ISSUER_URL: http://some-auth-server.example.com/default
            PROVIDERS_OIDC_CLIENT_ID: myid
            PROVIDERS_OIDC_CLIENT_SECRET: mysecret
```

Using the proxy
-------------

To reverse proxy a container running in Docker Compose, use a compose file along the lines of:
```yaml
---
version: '3'
services:
  webserver:
    image: nginx
    restart: unless-stopped
    labels:
      - traefik.enable=true
      - traefik.http.routers.webserver.rule=Host(`web.myserver.example.com`)
      - traefik.http.services.webserver.loadbalancer.server.port=80
      - traefik.http.routers.webserver.entrypoints=websecure
      - traefik.http.routers.webserver.tls.certresolver=default
      - traefik.http.routers.webserver.middlewares=traefik-forward-auth
    networks:
      - traefik
      - default

networks:
  traefik:
    external: true
```

Note that the container must be connected to the `traefik` network, or it won't work!

Alternatively to run a one-off container, try something like:
```
docker run --rm \
  --network=traefik \
  -l traefik.enable=true \
  -l traefik.http.routers.server.rule='Host(`nginx.myserver.example.com`)' \
  -l traefik.http.services.server.loadbalancer.server.port=80 \
  -l traefik.http.routers.server.entrypoints=websecure \
  -l traefik.http.routers.server.tls.certresolver=default \
  -l traefik.http.routers.server.middlewares=traefik-forward-auth \
  nginx
```

Rules Config
------------

To set custom rules that apply to certain endpoints, set the `proxy_rules` variable.

For example, to allow only a specific user to access a certain host, set:
```yaml
proxy_rules:
  # List of objects containing keys from the `rules` section in https://github.com/thomseddon/traefik-forward-auth?tab=readme-ov-file#option-details
  - name: allow_only_me
    action: auth
    rule: Host(`example.com`)
    whitelist:
      - me@example.com
```

The `name` and `rule` keys are required, `action`, `whitelist` (as a list), `domain` and `provider` are also permitted.

License
-------

MIT

Author Information
------------------

Sam Mesterton-Gibbons <sam@samn.co.uk>
