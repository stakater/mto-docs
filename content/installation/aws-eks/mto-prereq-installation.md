# MTO Prerequisites Installation Guide

This document provides detailed walk-through of installation of different MTO dependencies. Alternatively, you can use our

## Prerequisites

1. [`eksctl`](https://eksctl.io/installation/)
1. [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl) (1.18.3 or later).
1. [Helm CLI](https://helm.sh/docs/intro/install/)
1. A DNS service (Route53 will be used for this tutorial)

## Setting up Cluster

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


## Installation

Following steps can be used to configure an EKS cluster for MTO installation. Alternatively, [install-mto-prereqs.sh](#) script can be used automate these steps

### 1. Install NGINX Ingress Controller

NGINX ingress controller can be installed using 

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml
```

### 2. Install Cert Manager
Cert Manager can be installed by running the following command 
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.1/cert-manager.yaml
```

### 3. Create Let's Encrypt Access Key Secret

Create a YAML file with the following spec and replace `AWS_SECRET_ACCESS_KEY` with its value

```yaml
kind: Secret
apiVersion: v1
metadata:
  name:  letsencrypt-production-key
  namespace: cert-manager
stringData:
  aws_secret_access_key: <AWS_SECRET_ACCESS_KEY>
type: Opaque
```

Apply YAML file using following command

```bash
kubectl apply -f <FILENAME>.yaml
```

### 4. Create `ClusterIssuer` for Let's Encrypt

Create a YAML file with following the CR definition and replace `<AWS_ACCESS_KEY_ID>`, `<REGION>`, `<BASE_DOMAIN>` with their values

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-production
spec:
  acme:
    email: sre@stakater.com
    preferredChain: ISRG Root X1
    privateKeySecretRef:
      name: issuer-account-key
    server: 'https://acme-v02.api.letsencrypt.org/directory'
    solvers:
      - dns01:
          route53:
            accessKeyID: <AWS_ACCESS_KEY_ID>
            region: <REGION>
            secretAccessKeySecretRef:
              key: aws_secret_access_key
              name: letsencrypt-production-key
        selector:
          dnsZones:
            - <BASE_DOMAIN>

```

Apply YAML file using following command

```bash
kubectl apply -f <FILENAME>.yaml
```

### 5. Install AWS EBS CSI Driver

The [Amazon Elastic Block Store (Amazon EBS) Container Storage Interface (CSI) driver](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) manages the lifecycle of Amazon EBS volumes as storage for the Kubernetes Volumes that you create. The Amazon EBS CSI driver makes Amazon EBS volumes for these types of Kubernetes volumes: generic ephemeral volumes and persistent volumes.

Execute the following command to install EBS CSI Driver

```bash
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.38"
```

### 6. Create Storage Class for EBS

Apply the following YAML to create a storage class for EBS

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

### 7. Create Wildcard DNS Record

Retrieve NGINX ingress controller external IP using following command

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx -o yaml
```

External IP should be available at `status > loadBalanacer > ingress[0] > hostname`. Execute the command again after sometime if hostname is not available

Retrieve hosted zone id and hosted zone load balancer id using the following commands

```bash
# Retrieve Hosted Zone ID
aws route53 list-hosted-zones-by-name --dns-name <BASE_DOMAIN> --query "HostedZones[0].Id" --output text | cut -d '/' -f3)

# Retrieve Hosted Zone Load Balancer ID
aws elbv2 describe-load-balancers --query "LoadBalancers[0].CanonicalHostedZoneId" --output text
```

Create a JSON file with following data and replace values

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

Updated the DNS record with the following command

```bash
aws route53 change-resource-record-sets --hosted-zone-id <HOSTED_ZONE_ID> --change-batch file://change-batch.json
```

### 8. Create Wildcard Certificate

This certificate can be used by all the application under the given subdomain. MTO will use this certificate to secure MTO Console and Keycloak

Apply the following YAML after replacing values

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

| Parameter                     | Description   |
| ------                        | ------        |
| `<CERTIFICATE_NAME>`          | Name of the certificate to be generated  |
`<FULL_SUBDOMAIN>`              | DNS Subdomain of EKS cluster
| `<NAMESPACE>`                 | Namespace where generated certificate and secret will be placed. Use same namespace as MTO or copy the generated secret to MTO's namespace if MTO is installed in different namespace  |
| `<CERTIFICATE_SECRET_NAME>`   | Certificate secret will be generated with this name. This secret can be used in MTO's CR to enable SSL on MTO components  |

## What's Next?

All the required have been installed and configured. Now MTO can be installed on the EKS Cluster. See [EKS MTO Installation Guide](./mto-installation.md)
