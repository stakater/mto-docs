# Basic vs Enterprise Tier

Multi Tenant Operator is available in two versions: _Basic_ and _Enterprise_. The difference between the versions are highlighted here:

| Feature | Basic | Enterprise |
| :- | :-: | :-: |
| Number of possible Tenants | Two (2) | Unlimited |
| Support | Community support | Stakater support with Key Account Manager to build strong relationships and strong understanding of requirements and needs |
| Custom development requests | Not possible | Possible through support requests, which will be prioritized |
| Price | Free | Price available on the [Multi Tenant Operator website](https://www.stakater.com/mto) |

## Demo

A web application demo of MTO is available on the [Multi Tenant Operator website](https://www.stakater.com/mto), it showcases MTO Console which is aimed at providing a more intuitive and user-friendly way for administrators and tenant users to manage tenants and their resources.

Contact [`sales@stakater.com`](mailto:sales@stakater.com) if you would like a custom demo in your environment.

## Enterprise License Configuration

For the Enterprise version, you need to have a configmap `license` created in MTO's namespace `multi-tenant-operator`. You will get this configmap when purchasing the Enterprise version. It would look like this:

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
  signature.base64.txt: <base64 signature here>
```

## Pricing

See the [Multi Tenant Operator website](https://www.stakater.com/mto) for pricing of the Enterprise version.

## Contact

For more info, contact [`sales@stakater.com`](mailto:sales@stakater.com).
