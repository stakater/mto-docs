# MTO Preparation Guide

This document provides a detailed walkthrough of the preparation steps required for MTO installation.

## Cluster Requirements

An EKS 1.28+ cluster with the following components:
- Valid certificates for MTO Gateway, MTO Console, and MTO Keycloak
- A default storage class
- An Ingress controller
- DNS entries configured for MTO Gateway, MTO Console, and MTO Keycloak

## Local Setup Requirements

The installation machine must have:
- Helm installed
- kubectl installed

Once these preparations are complete, you can proceed with the [installation section](./installation.md).

## Optional: Creating and Configuring an EKS Cluster

If you already have an EKS 1.28+ cluster that meets the [Cluster Requirements](#cluster-requirements) you can skip this section and proceed directly to the Installation Guide.

However, if you don’t have an existing cluster, follow this step-by-step guide to create and configure one properly for MTO installation.

### Create EKS Cluster

Execute the following snippet in your terminal with appropriate values. This snippet will configure the AWS Credentials. See [Manage access keys for IAM users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) for more details about access keys

```bash
aws configure set region <AWS_REGION>
aws configure set aws_access_key_id <AWS_ACCESS_KEY_ID>
aws configure set aws_secret_access_key <AWS_SECRET_ACCESS_KEY>
```

Use the following command to create an EKS cluster if it doesn't exist

```bash
eksctl create cluster \
    --name <CLUSTER_NAME> \
    --region <AWS_REGION> \
    --nodegroup-name standard-workers \
    --node-type t3.xlarge \
    --nodes 1 \
    --nodes-min 1 \
    --nodes-max 3 \
    --managed
```

Set the kubernetes context to the specified cluster.

```bash
# Update the current context
aws eks update-kubeconfig --name <CLUSTER_NAME> --region <AWS_REGION>
```

### Install Ingress Controller

To install NGINX Ingress Controller, run the following command:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml
```

### Install CertManager

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
- <AWS_ACCESS_KEY_ID>: Your AWS Access Key ID.
- <REGION>: The AWS region where your Route 53 hosted zone is located (e.g., us-east-1).
- <BASE_DOMAIN>: Your base domain (e.g., example.com).
- <EMAIL>: Your email address for Let's Encrypt notifications.

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
kubectl apply -f letsencrypt-clusterissuer.yaml.yaml
```

1. Verify the ClusterIssuer:

Run the following command to ensure the ClusterIssuer is ready:

```bash
kubectl get clusterissuer letsencrypt-production
```

### Install AWS EBS CSI Driver

The Amazon EBS CSI Driver enables Kubernetes to manage Amazon Elastic Block Store (EBS) volumes, handling their lifecycle as persistent storage for workloads. 

To install the AWS EBS CSI Driver, execute the following command:

```bash
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.38"
```

Once installed, verify that the driver is running by checking the pods in the kube-system namespace:

```bash
kubectl get pods -n kube-system | grep ebs
```

### Create Storage Class for EBS

1. Create a file named `storage-class.yaml` and add the following content:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
metadata:
  name: ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
parameters:
  type: gp3
```

1. Apply the configuration using the following command:

```bash
kubectl apply -f storage-class.yaml
```

1. Verify that the StorageClass has been created:

```bash
kubectl get storageclass
```

### Create Wildcard DNS Record

To ensure proper routing for applications, you need to create a wildcard DNS record that points to the NGINX Ingress Controller’s external IP. Follow these steps:

1. Retrieve the Ingress Controller's External IP
Run the following command to get the external IP of the NGINX Ingress Controller:
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

1.  Create a JSON File for the DNS Update
Create a file named change-batch.json and update the placeholders:
- <FULL_SUBDOMAIN> – Your subdomain (e.g., apps.example.com)
- <HOSTED_ZONE_LB_ID> – Hosted Zone Load Balancer ID from Step 2
- <EXTERNAL_IP> – External IP retrieved in Step 1

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

1. Update the DNS Record in Route 53
Apply the DNS update using the following command:
```bash
aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://change-batch.json
```

1. Verify DNS Configuration
Check if the DNS record has been propagated correctly:
```bash
nslookup <YOUR_DOMAIN>
```
Once the record is updated, traffic will be properly routed to the NGINX Ingress Controller.

### Create Wildcard Certificate

A wildcard certificate allows all applications under a given subdomain to use a single SSL certificate. MTO will use this certificate to secure the MTO Console, MTO Gateway, and MTO Keycloak.

1. Apply the Wildcard Certificate Configuration

Create a file named `wildcard-certificate.yaml` and replace the placeholders with the appropriate values:
- <CERTIFICATE_NAME> - Name of the certificate to be generated.
- <FULL_SUBDOMAIN> - DNS subdomain for which the wildcard certificate will be issued.
- <NAMESPACE> - Namespace where the certificate and secret will be created. If MTO is installed in a different namespace, manually copy the generated secret.
- <CERTIFICATE_SECRET_NAME> - Name of the secret that will store the generated certificate. This secret will be used in MTO’s configuration to enable SSL for MTO components.

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
kubectl apply -f wildcard-certificate.yaml
```

## What's Next?

All the required have been installed and configured. Now MTO can be installed on the EKS Cluster. See [EKS MTO Installation Guide](./installation.md)
