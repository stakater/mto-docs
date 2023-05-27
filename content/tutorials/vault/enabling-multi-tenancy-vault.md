# Enabling Multi-Tenancy in Vault

# Vault Multitenancy

HashiCorp Vault is an identity-based secret and encryption management system. Vault validates and authorizes a system's clients (users, machines, apps) before providing them access to secrets or stored sensitive data.

## Vault integration in Multi Tenant Operator

### Service Account Auth in Vault

MTO enables the [Kubernetes auth method](https://www.Vaultproject.io/docs/auth/kubernetes) which can be used to authenticate with Vault using a Kubernetes Service Account Token. When enabled, for every tenant namespace, MTO automatically creates policies and roles that allow the service accounts present in those namespaces to **read** secrets at tenant's path in Vault. The name of the role is the same as **namespace** name.

These service accounts are required to have `stakater.com/vault-access: true` label, so they can be authenticated with Vault via MTO.

The Diagram shows how MTO enables ServiceAccounts to read secrets from Vault.

![image](./images/mto-vault-k8s-auth-workflow.png)

### User OIDC Auth in Vault

This requires a running `RHSSO(RedHat Single Sign On)` instance integrated with Vault over [OIDC](https://developer.hashicorp.com/vault/docs/auth/jwt) login method.

MTO integration with Vault and RHSSO provides a way for users to log in to Vault where they only have access to relevant tenant paths.

Once both integrations are set-up with [IntegrationConfig CR](/content/integration-config.md), MTO links tenant users to specific client roles named after their tenant under Vault client in RHSSO.

After that, MTO creates specific policies in Vault for its tenant users.

Mapping of tenant roles to Vault is shown below

|  Tenant Role  |        Vault Path       |         Vault Capabilities       |
|:--------------|:------------------------|:---------------------------------|
|Owner, Editor  |(tenantName)/*           |Create, Read, Update, Delete, List|
|Owner, Editor  |sys/mounts/(tenantName)/*|Create, Read, Update, Delete, List|
|Owner, Editor  |managed-addons/*         |Read, List                        |
|Viewer         |(tenantName)/*           |Read                              |

A simple user login workflow is shown in the diagram below.

![image](./images/mto-vault-integration-user-workflow.png)
