# Basic vs Enterprise Tier

Multi Tenant Operator offers two types of versions to the end customers

* Basic Tier (up to 2 Tenants)
* Enterprise Tier

## License Configuration

We offer a basic tier license with installation, and you can create max 2 [Tenants](../tutorials/tenant/create-tenant.md) with it.

For our Enterprise version, you need to have a configmap `license` created in MTO's namespace (multi-tenant-operator). To get this configmap, you can contact [`sales@stakater.com`](mailto:sales@stakater.com). It would look like this:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: license
  namespace: multi-tenant-operator
data:
  payload.json: |
    {
        "metaData": {
            "tier" : "paid",
            "company": "<company name here>"
        }
    }
  signature.base64.txt: <base64 signature here.>
```
