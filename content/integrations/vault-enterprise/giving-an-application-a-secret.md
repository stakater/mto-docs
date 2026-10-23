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

The extension renders, in the tenant's Vault namespace, a `Policy` and a Kubernetes login role named `kv.acme.acme-shop.checkout`, and a `ConfigMap` `vault-config-checkout` in `acme-shop` holding the `VAULT_*` values the app needs:

```text
VAULT_ADDR, VAULT_NAMESPACE=<vco.namespace>/acme, VAULT_K8S_MOUNT=kubernetes/workloads,
VAULT_K8S_ROLE=kv.acme.acme-shop.checkout, VAULT_KV_APP_PATH=kv/data/dev/acme-shop/checkout
```

A wrongly configured annotation produces a `vault-config-checkout.error` `ConfigMap` explaining what is wrong, and nothing else — one app's mistake never breaks the tenant's other apps.

## 2. Read and write from the pod

The pod logs in with its ServiceAccount token (which Kubernetes mounts at `/var/run/secrets/kubernetes.io/serviceaccount/token`) and uses the values from the `ConfigMap`:

```bash
# values come from the vault-config-checkout ConfigMap, mounted as env
export VAULT_ADDR VAULT_NAMESPACE
TOKEN=$(vault write -field=token auth/"$VAULT_K8S_MOUNT"/login \
  role="$VAULT_K8S_ROLE" \
  jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token)

VAULT_TOKEN=$TOKEN vault kv put  -mount=kv "$VAULT_KV_APP_PATH" db-password=s3cret
VAULT_TOKEN=$TOKEN vault kv get  -mount=kv "$VAULT_KV_APP_PATH"
```

An `editor` can write; a `viewer` can only read; an `audit-read` can list names but not read values. Nothing the app does can reach another app's path, another namespace, or another tenant.

!!! tip "Prefer delivery over in-app Vault calls"
    Most apps should not call Vault at all. Annotate the Deployment instead and the secret arrives as an ordinary Kubernetes `Secret` through External Secrets — see [Delivery and login](delivery-and-login.md). Use the in-pod calls above only when an app genuinely needs the Vault API.

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

- Read or write outside its own `kv/data/<env>/<namespace>/<app>/` prefix (unless sharing is set up — see [Secrets and sharing](secrets-and-sharing.md)).
- Reach another tenant's Vault namespace — login is bound to the tenant's namespace and the app's ServiceAccount.
- Exceed its role — a `viewer` cannot write, an `editor` cannot destroy versions.
- Use an unknown `vault.stakater.com/` annotation — it is rejected with an error `ConfigMap`, not ignored.

---

**Previous:** [Installation](installation.md) · **Next:** [Secrets and sharing](secrets-and-sharing.md)
