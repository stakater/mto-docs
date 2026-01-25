# MTO Installation Guide

Once the [necessary preparations](./preparation.md) are complete, you can proceed with the installation section.

The installation process consists of two steps:

1. [Install MTO Core](#install-mto-core)
1. [Enable MTO Console](#enable-mto-console)

## Install MTO Core

We will be using helm to install the operator.

```bash
helm install tenant-operator oci://ghcr.io/stakater/public/charts/tenant-operator --namespace multi-tenant-operator --create-namespace
```

We will wait for the pods to come in running state.

## Enable MTO Console

Execute the following command to enable MTO console

```bash
kubectl patch integrationconfig tenant-operator-config \
  -n multi-tenant-operator --type merge --patch "{
  \"spec\": {
    \"components\": {
      \"console\": true,
      \"ingress\": {
        \"console\": {
          \"host\": \"console.<FULL_SUBDOMAIN>\",
          \"tlsSecretName\": \"<SECRET_NAME>\"
        },
        \"gateway\": {
          \"host\": \"gateway.<FULL_SUBDOMAIN>\",
          \"tlsSecretName\": \"<SECRET_NAME>\"
        },
        \"keycloak\": {
          \"host\": \"keycloak.<FULL_SUBDOMAIN>\",
          \"tlsSecretName\": \"<SECRET_NAME>\"
        },
        \"ingressClassName\": \"nginx\"
      },
      \"showback\": true
    }
  }
}"
```

Placeholder         | Description
------------        |------------
`<FULL_SUBDOMAIN>`  | Full subdomain of the EKS cluster e.g. `iinhdnh6.demo.kubeapp.cloud`
`<SECRET_NAME>`     | Name of the secret that should be used as TLS secret

Wait for the pods to be ready with the following command

```bash
kubectl wait --for=condition=ready pod -n multi-tenant-operator --all --timeout=300s
```

List the ingresses to access the URL of MTO Console

```bash
> kubectl get ingress -n multi-tenant-operator

NAME                       CLASS   HOSTS                                  ADDRESS                                                                          PORTS     AGE
tenant-operator-console    nginx   console.iinhdnh6.demo.kubeapp.cloud    ae51c179026a94c90952fc50d5d91b52-a4446376b6415dcb.elb.eu-north-1.amazonaws.com   80, 443   23m
tenant-operator-gateway    nginx   gateway.iinhdnh6.demo.kubeapp.cloud    ae51c179026a94c90952fc50d5d91b52-a4446376b6415dcb.elb.eu-north-1.amazonaws.com   80, 443   23m
tenant-operator-keycloak   nginx   keycloak.iinhdnh6.demo.kubeapp.cloud   ae51c179026a94c90952fc50d5d91b52-a4446376b6415dcb.elb.eu-north-1.amazonaws.com   80, 443   24m

```

## MTO Console Admin Login

Patch the following integration config to give privileged access to MTO's default admin user

```bash
kubectl patch integrationconfigs.tenantoperator.stakater.com -n multi-tenant-operator tenant-operator-config --type=merge --patch "{
    \"spec\": {
        \"accessControl\": {
            \"privileged\": {
                \"users\": [
                    \"mto@stakater.com\"
                ]
            }
        }
    }
}"
```

Open the Console URL and Log In with the admin user. Default username and password is `mto`

![MTO Console Login Page](../../images/mto-console-login.png)

Dashboard will open after the successful login. Currently we don't have any tenants

![MTO Console Dashboard](../../images/mto-console-dashboard-0-tenants.png)

## What's Next

Now lets [create our first tenant on AKS](./validation.md).
