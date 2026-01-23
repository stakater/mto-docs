# kubectl-tenant

A kubectl plugin that provides tenant-scoped access to cluster resources managed by Multi Tenant Operator.

## Overview

Kubernetes RBAC has a fundamental limitation: when granting `list` permissions on cluster-scoped resources, users can see *all* resources of that type, not just those belonging to their tenant. The kubectl-tenant plugin solves this by reading the Tenant CR status and filtering results to show only resources the tenant is permitted to access.

**Source Code:** [GitHub.com/Stakater/kubectl-tenant](https://github.com/stakater/kubectl-tenant)

## Installation

Download the binary for your platform from [GitHub Releases](https://github.com/stakater/kubectl-tenant/releases):

```bash
# Download for your OS/Arch
curl -L https://github.com/stakater/kubectl-tenant/releases/download/v0.0.1/kubectl-tenant-linux-amd64 -o kubectl-tenant
chmod +x kubectl-tenant
mv kubectl-tenant ~/.local/bin/   # ensure this path is in your $PATH
```

Verify it works:

```bash
kubectl tenant --help
```

### Build from Source

```bash
git clone https://github.com/stakater/kubectl-tenant.git
cd kubectl-tenant
go build -o kubectl-tenant
mv kubectl-tenant /usr/local/bin/
```

## Supported Resources

| Resource | Command |
|----------|---------|
| StorageClasses | `storageclasses` |
| Namespaces | `namespaces` |

## Usage

### Command Syntax

```bash
kubectl tenant get <resource-type> <tenant-name> [resource-name] [flags]
```

| Argument | Description |
|----------|-------------|
| `resource-type` | The type of resource to list (`storageclasses`, `namespaces`) |
| `tenant-name` | The name of the Tenant CR to scope the query |
| `resource-name` | (Optional) Specific resource name to retrieve |

### List Resources

List all storage classes for a tenant:

```bash
kubectl tenant get storageclasses my-tenant
```

```bash
NAME                  PROVISIONER             AGE
my-tenant-fast        kubernetes.io/aws-ebs   30d
my-tenant-standard    kubernetes.io/gp2       30d
```

List all namespaces for a tenant:

```bash
kubectl tenant get namespaces my-tenant
```

```bash
NAME                  AGE
my-tenant-prod        45d
my-tenant-staging     45d
my-tenant-dev         30d
```

### Get Specific Resource

Get a specific storage class:

```bash
kubectl tenant get storageclasses my-tenant my-tenant-fast
```

```bash
NAME                  PROVISIONER             AGE
my-tenant-fast        kubernetes.io/aws-ebs   30d
```

### Output Formats

All standard kubectl output formats and flags are supported:

```bash
# YAML output
kubectl tenant get storageclasses my-tenant -o yaml

# JSON output
kubectl tenant get namespaces my-tenant -o json

# JSONPath for specific fields
kubectl tenant get namespaces my-tenant -o jsonpath='{.items[*].metadata.name}'

# Custom columns
kubectl tenant get namespaces my-tenant -o custom-columns=NAME:.metadata.name,STATUS:.status.phase
```

## How It Works

- Reads the specified Tenant CR from `tenantoperator.stakater.com/v1beta3`
- Extracts permitted resources from the tenant's status fields
- Fetches and returns only those resources the tenant can access

## Demo

![kubectl tenant RBAC demo](../images/kubectlTenantRbacDemo.gif)
