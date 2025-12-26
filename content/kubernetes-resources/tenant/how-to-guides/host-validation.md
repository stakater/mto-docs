# Restricting Hostname per Tenant

## Controlling allowed hostnames for Ingresses and Routes

The `hostValidationConfig` field in the `Tenant` CR lets you define which hostnames tenants may use when creating Ingress (Kubernetes) or Route (OpenShift) resources.

```yaml title="Tenant"
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-sample
spec:
  # other fields
  hostValidationConfig:
    allowed:
      - gateway.saap.dev
      - console.saap.dev
      - "*.saap.prod"
    allowedRegex: ^[a-zA-Z0-9-]+\.saap\.dev$
    denyWildcards: false
```

### Notes

- `allowed`: explicit hostnames or wildcard hostnames to permit (wildcards compared as-is). If you use wildcards here, they must appear literally in the list.
- `allowedRegex`: a regular expression used to validate hostnames; entries matching the regex are allowed.
- `denyWildcards`: when true, wildcard hostnames (for example `*.example.com`) are rejected even if present in `allowed`.

The operator validates the hostnames on Ingress and Route resources created by tenants and blocks or rejects hosts that do not match the policy. Use `allowed` for simple allow-lists and `allowedRegex` for pattern-based rules that are harder to express with simple wildcards.

### Example

The `allowedRegex` example above permits hostnames like `app1.saap.dev` or `api-123.saap.dev` while excluding other domains.

Allowed Ingress (host matches `allowedRegex`):

```yaml title="Allowed Ingress"
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: allowed-ingress
  namespace: tenant-ns
spec:
  rules:
    - host: app1.saap.dev
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
```

Denied Ingress (host not permitted):

```yaml title="Denied Ingress"
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: denied-ingress
  namespace: tenant-ns
spec:
  rules:
    - host: evil.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
```

### Behavior

- The first Ingress will be accepted because `app1.saap.dev` matches `allowedRegex`.
- The second Ingress will be rejected by the operator (or by its admission checks) because `evil.example.com` does not match the `hostValidationConfig` policy.

### Demo

![Ingress Host Validation](../../../images/host-validation.gif)
