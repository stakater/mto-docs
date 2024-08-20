# Pricing

Multi Tenant Operator (MTO) is available in two versions: _Basic_ and _Enterprise_.

The Basic version is free.

The Enterprise version is priced according to information on the [Multi Tenant Operator website](https://www.stakater.com/mto).

## Feature Difference

The difference between the versions are highlighted here:

| Feature | Basic | Enterprise |
| :- | :-: | :-: |
| Number of possible Tenants | Two (2) | Unlimited |
| Support | Community support through [community Slack](https://stakater-community.slack.com/archives/C07HS5V9P6G) | Stakater dedicated support with Key Account Manager to build strong relationships and strong understanding of your requirements and needs |
| Custom development requests | Not possible | Possible through support requests, which will be prioritized |
| Price | Free | Pricing available on the [Multi Tenant Operator website](https://www.stakater.com/mto) |

## Demo

A web application demo of MTO is available on the [Multi Tenant Operator website](https://www.stakater.com/mto), it showcases MTO Console which is aimed at providing a more intuitive and user-friendly way for administrators and tenant users to manage tenants and their resources.

Contact [`sales@stakater.com`](mailto:sales@stakater.com) to request a custom demo.

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

## Support

See [Stakater Support](https://support.stakater.com/) for information about support for the Enterprise Version of MTO.

## Contact

For more info, contact [`sales@stakater.com`](mailto:sales@stakater.com).
