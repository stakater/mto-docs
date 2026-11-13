# Giving an application a secret

This is the day-to-day workflow — written from the developer's hands. It assumes the extension is installed ([Installation](installation.md)) and the tenant `acme` has a labelled namespace `acme-shop`.

## 1. Annotate the ServiceAccount

Give the app its own KV prefix and an access role:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: checkout
  namespace: acme-shop
  annotations:
    vault.stakater.com/kv: "true"
    vault.stakater.com/role: editor      # read + write (see Overview → roles)
```

The extension renders a Vault policy and a Kubernetes login role named `kv.acme.acme-shop.checkout`, on the tenant's auth mount `auth/acme/kubernetes/workloads`. It also renders a `ConfigMap` `vault-config-checkout` in `acme-shop` holding the `VAULT_*` values the app needs:

```text
VAULT_ADDR, VAULT_NAMESPACE="" (Community Edition has none), VAULT_K8S_MOUNT=acme/kubernetes/workloads,
VAULT_K8S_ROLE=kv.acme.acme-shop.checkout, VAULT_KV_APP_PATH=acme/kv/data/dev/acme-shop/checkout/
```

These are the keys the Vault Enterprise extension writes. `VAULT_NAMESPACE` is present and empty, and every path starts with the tenant, so a client written for Enterprise works unchanged. A `ConfigMap` `vault-apps` in the namespace lists every app there that uses Vault, with its paths.

A wrongly configured annotation produces a `vault-config-checkout.error` `ConfigMap` explaining what is wrong, and nothing else — one app's mistake never breaks the tenant's other apps.

## 2. Read and write from the pod

The pod logs in with its ServiceAccount token (which Kubernetes mounts at `/var/run/secrets/kubernetes.io/serviceaccount/token`) and uses the values from the `ConfigMap`:

```bash
# values come from the vault-config-checkout ConfigMap, mounted as env
TOKEN=$(vault write -field=token auth/"$VAULT_K8S_MOUNT"/login \
  role="$VAULT_K8S_ROLE" \
  jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token)

VAULT_TOKEN=$TOKEN vault kv put -mount=acme/kv dev/acme-shop/checkout/db-creds password=s3cret
VAULT_TOKEN=$TOKEN vault read "${VAULT_KV_APP_PATH}db-creds"     # the same secret, by its API path
```

An `editor` can write; a `viewer` can only read; an `audit-read` can list names but not read values. Nothing the app does can reach another app's path, another namespace, or another tenant's mount.

!!! tip "Prefer delivery over in-app Vault calls"
    Most apps should not call Vault at all. Annotate the Deployment instead and the secret arrives as an ordinary Kubernetes `Secret` through External Secrets — see [Delivery and login](delivery-and-login.md). Use the in-pod calls above only when an app needs the Vault API.

## 3. Mount the config into the Deployment

```yaml
spec:
  template:
    spec:
      serviceAccountName: checkout       # the annotated ServiceAccount
      containers:
        - name: checkout
          image: acme/checkout:1.0
          envFrom:
            - configMapRef:
                name: vault-config-checkout
```

## What an application cannot do

- Read or write outside its own `<tenant>/kv/data/<env>/<namespace>/<app>/` prefix (unless sharing is set up — see [Secrets and sharing](secrets-and-sharing.md)).
- Reach another tenant's mount — its policy names only its own prefix, and its login role binds the app's ServiceAccount and its namespace, by name and tenant label.
- Exceed its role — a `viewer` cannot write, an `editor` cannot destroy versions.
- Write a Vault policy, a mount, an auth role or the mount's config — no role can.
- Use an unknown `vault.stakater.com/` annotation — it is rejected with an error `ConfigMap`, not ignored.

---

**Previous:** [Installation](installation.md) · **Next:** [Secrets and sharing](secrets-and-sharing.md)
