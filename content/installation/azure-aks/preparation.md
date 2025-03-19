# MTO Preparation Guide

This document provides a detailed walk through of the preparation steps required for MTO installation.

## Cluster Requirements

An AKS cluster with the following components:

- A default storage class
- An Ingress controller
- Valid certificates for MTO Gateway, MTO Console, and MTO Keycloak

DNS entries configured for MTO Gateway, MTO Console, and MTO Keycloak

A user with **cluster administrator privileges**.

## Local Setup Requirements

The installation machine must have:

- Helm installed
- kubectl installed

Once these preparations are complete, you can proceed with the [installation section](./installation.md).

## Optional: Creating and Configuring an AKS Cluster

If you already have an AKS cluster that meets the [Cluster Requirements](#cluster-requirements) you can skip this section and proceed directly to the Installation Guide.

However, if you don’t have an existing cluster, follow this step-by-step guide to create and configure one properly for MTO installation.

### Configure Admin Group

Execute the following snippet in your terminal with appropriate values. This snippet will configure the Azure CLI. See [Register a Microsoft Entra app and create a service principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) for more details about access keys

```bash
az login --service-principal --username "<SERVICE_PRINCIPAL_APP_ID>" --password "<SERVICE_PRINCIPAL_PASSWORD>" --tenant "<SERVICE_PRINCIPAL_TENANT_ID>"
```

Create a group called `mto-admins`:

```bash
az ad group create --display-name mto-admins --mail-nickname mto-admins
```

Fetch the service principal user id

```bash
SP_USER_ID=$(az ad sp show --id "$(az account show --query user.name -o tsv)" --query id -o tsv)
```

Add user to `mto-admins` group

```bash
az ad group member add --group mto-admins --member-id "$SP_USER_ID"
```

Fetch the admin group id by executing the following command. This value will be used when creating AKS cluster

```bash
ADMIN_GROUP_ID=$(az ad group show --group mto-admins --query id -o tsv)
```

### Create AKS Cluster

Create a resource group using following command

```bash
az group create --name "<RESOURCE_GROUP_NAME>" --location westus2
```

Create AKS cluster

```bash
az aks create --resource-group "<RESOURCE_GROUP_NAME>" --name "<CLUSTER_NAME>" \
              --node-count 1 --vm-set-type VirtualMachineScaleSets \
              --enable-cluster-autoscaler --min-count 1 --max-count 3 \
              --enable-aad --aad-admin-group-object-ids "<ADMIN_GROUP_ID>" \
              --generate-ssh-keys
```


Set the kubernetes context to the specified cluster.

```bash
# Update the current context
az aks get-credentials --resource-group "<RESOURCE_GROUP_NAME>" --name "<CLUSTER_NAME>" --admin```
```

### Install Ingress Controller

To install nginx Ingress Controller, run the following command:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml
```

### Install Certmanager

To install Cert-Manager, execute the following command:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.1/cert-manager.yaml
```

### Create Let's Encrypt Access Key Secret

To configure Let's Encrypt with AWS, create the Kubernetes Secret using the following command:

```bash
kubectl create secret generic letsencrypt-production-key \
  --namespace cert-manager \
  --from-literal=aws_secret_access_key=<AWS_SECRET_ACCESS_KEY>
```

Replace <AWS_SECRET_ACCESS_KEY> with your actual AWS secret key.

### Create `ClusterIssuer` for Let's Encrypt

To enable automatic SSL certificate issuance using Let’s Encrypt, you need to create a ClusterIssuer resource in Kubernetes. This issuer will use Route 53 DNS-01 challenge to validate domain ownership and issue certificates.

1. Create a YAML file named `letsencrypt-clusterissuer.yaml` for the ClusterIssuer with the following content. Replace the placeholders with your actual values:

    - `<AWS_ACCESS_KEY_ID>`: Your AWS Access Key ID.
    - `<REGION>`: The AWS region where your Route 53 hosted zone is located (e.g., us-east-1).
    - `<BASE_DOMAIN>`: Your base domain (e.g., example.com).
    - `<EMAIL>`: Your email address for Let's Encrypt notifications.

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: ClusterIssuer
    metadata:
      name: letsencrypt-production
    spec:
      acme:
        email: <EMAIL>  # Replace with your email address
        preferredChain: ISRG Root X1
        privateKeySecretRef:
          name: issuer-account-key
        server: 'https://acme-v02.api.letsencrypt.org/directory'
        solvers:
          - dns01:
              route53:
                accessKeyID: <AWS_ACCESS_KEY_ID>  # Replace with your AWS Access Key ID
                region: <REGION>  # Replace with your AWS region
                secretAccessKeySecretRef:
                  key: aws_secret_access_key
                  name: letsencrypt-production-key
            selector:
              dnsZones:
                - <BASE_DOMAIN>  # Replace with your base domain
    ```

1. Apply the YAML file to your cluster:

    ```bash
    kubectl apply -f letsencrypt-clusterissuer.yaml
    ```

1. Run the following command to ensure the ClusterIssuer is ready:

    ```bash
    kubectl get clusterissuer letsencrypt-production
    ```

### Create Wildcard DNS Record

To ensure proper routing for applications, you need to create a wildcard DNS record that points to the nginx Ingress Controller’s external IP. Follow these steps:

1. Retrieve the Ingress Controller's External IP
    Run the following command to get the external IP of the nginx Ingress Controller:

    ```bash
    kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"
    ```

    If the hostname is not available, wait for a few minutes and re-run the command.

1. Retrieve Hosted Zone and Load Balancer IDs
    Run the following commands to retrieve the Route 53 Hosted Zone ID and Load Balancer Hosted Zone ID:

    ```bash
    # Retrieve Hosted Zone ID
    HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name <BASE_DOMAIN> --query "HostedZones[0].Id" --output text | cut -d '/' -f3)

    # Retrieve Hosted Zone Load Balancer ID
    HOSTED_ZONE_LB_ID=$(aws elbv2 describe-load-balancers --query "LoadBalancers[0].CanonicalHostedZoneId" --output text)
    ```

1. Create a JSON File for the DNS Update
    Create a file named `change-batch.json` and update the placeholders:

    - `<FULL_SUBDOMAIN>` – Your subdomain (e.g., apps.example.com)
    - `<HOSTED_ZONE_LB_ID>` – Hosted Zone Load Balancer ID from Step 2
    - `<EXTERNAL_IP>` – External IP retrieved in Step 1

    ```json
    {
      "Comment": "Update wildcard DNS record to point to NGINX Ingress ELB",
      "Changes": [
        {
          "Action": "UPSERT",
          "ResourceRecordSet": {
            "Name": "*.<FULL_SUBDOMAIN>",
            "Type": "A",
            "AliasTarget": {
              "HostedZoneId": "<HOSTED_ZONE_LB_ID>",
              "DNSName": "<EXTERNAL_IP>",
              "EvaluateTargetHealth": false
            }
          }
        }
      ]
    }
    ```

1. Update the DNS Record in Route 53 by using the following command

    ```bash
    aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://change-batch.json
    ```

1. Verify DNS Configuration
    Check if the DNS record has been propagated correctly:

    ```bash
    nslookup <YOUR_DOMAIN>
    ```

    Once the record is updated, traffic will be properly routed to the nginx Ingress Controller.

### Create Wildcard Certificate

A wildcard certificate allows all applications under a given subdomain to use a single SSL certificate. MTO will use this certificate to secure the MTO Console, MTO Gateway, and MTO Keycloak.

1. Apply the Wildcard Certificate Configuration

    Create a file named `wildcard-certificate.yaml` and replace the placeholders with the appropriate values:

    - `<CERTIFICATE_NAME>` - Name of the certificate to be generated.
    - `<FULL_SUBDOMAIN>` - DNS subdomain for which the wildcard certificate will be issued.
    - `<NAMESPACE>` - Namespace where the certificate and secret will be created. If MTO is installed in a different namespace, manually copy the generated secret.
    - `<CERTIFICATE_SECRET_NAME>` - Name of the secret that will store the generated certificate. This secret will be used in MTO’s configuration to enable SSL for MTO components.

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: <CERTIFICATE_NAME>
      namespace: <NAMESPACE>
    spec:
      secretName: <CERTIFICATE_SECRET_NAME>
      issuerRef:
        name: letsencrypt-production
        kind: ClusterIssuer
      commonName: *.<FULL_SUBDOMAIN>
      dnsNames:
      - *.<FULL_SUBDOMAIN>
    ```

1. Apply the certificate configuration using the following command:

    ```bash
    kubectl apply -f wildcard-certificate.yaml
    ```

1. Verify Certificate Creation

    After applying the configuration, check if the certificate has been issued successfully:

    ```bash
    kubectl wait --for=condition=Ready certificate/<CERTIFICATE_NAME> -n <NAMESPACE> --timeout=300s
    ```

## What's Next?

All the required components have been installed and configured. Now MTO can be installed on the EKS Cluster. See [AKS MTO Installation Guide](./installation.md)
