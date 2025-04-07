# Overview

The Multi-Tenant Operator (MTO) supports two installation methods: Operator Lifecycle Manager (OLM) and Helm Chart. These methods ensure flexibility and compatibility across various Kubernetes environments, including OpenShift, Azure Kubernetes Service (AKS), Amazon Elastic Kubernetes Service (EKS), and others.

## Installation Methods

### 1. Operator Lifecycle Manager (OLM)

OLM is the recommended installation method for OpenShift. It leverages OpenShift's native operator management capabilities, ensuring seamless integration and lifecycle management.

### 2. Helm Chart

Helm is the preferred installation method for all other Kubernetes distributions, including AKS, EKS, GKE and generic Kubernetes environments. Helm simplifies the deployment process with its consistent and automated approach.

## Prerequisites

Before proceeding, ensure the following:

* Access to an OpenShift cluster (for OLM installation) or a Kubernetes cluster (for Helm installation).
* Administrator-level permissions on the cluster.
* Familiarity with kubectl or platform-specific CLI tools.
* Helm installed locally for Helm-based installations.

## Next Steps

Choose the installation guide that matches your environment:

* [Installing with OLM on OpenShift](openshift.md)
* [Installing with Helm on AKS](./azure-aks/installation.md)
* [Installing with Helm on EKS](./aws-eks/installation.md)
* [Installing with Helm on any Kubernetes](kubernetes.md)

By following the appropriate guide, you’ll be able to deploy MTO efficiently and start managing multi-tenancy in your Kubernetes environment.
