# Key Features

The key features of Multi Tenant Operator (MTO) are described below.

## Core Features

### Kubernetes Multitenancy

RBAC is one of the most complicated and error-prone parts of Kubernetes. With Multi Tenant Operator, you can rest assured that RBAC is configured with the "least privilege" mindset and all rules are kept up-to-date with zero manual effort.

Multi Tenant Operator binds existing ClusterRoles to the Tenant's namespaces used for managing access to the namespaces and the resources they contain. You can also modify the default roles or create new roles to have full control and customize access control for your users and teams.

Multi Tenant Operator is also able to leverage existing groups in Kubernetes and OpenShift, or external groups synced from third-party identity management systems, for maintaining tenant membership in your organization's current user management system.

More details on [Tenant](../kubernetes-resources/tenant/tenant-overview.md)

### Templates and Template Distribution

Multi Tenant Operator allows admins/users to define templates for namespaces, so that others can instantiate these templates to provision namespaces with batteries loaded. A template could pre-populate a namespace for certain use cases or with basic tooling required. Templates allow you to define Kubernetes manifests, Helm charts, and more to be applied when the template is used to create a namespace.

It also allows the parametrization of these templates for flexibility and ease of use. It also provides the option to enforce the presence of templates in one tenant's or all tenants' namespaces for configuring secure defaults.

Common use cases for namespace templates may be:

* Adding networking policies for multi-tenancy
* Adding development tooling to a namespace
* Deploying pre-populated databases with test data
* Injecting new namespaces with optional credentials such as image pull secrets

More details on [Distributing Template Resources](../kubernetes-resources/template/how-to-guides/deploying-templates.md)

### Resource Management

Multi Tenant Operator provides a mechanism for defining Resource Quotas at the tenant scope, meaning all namespaces belonging to a particular tenant share the defined quota. This enables you to safely enable dev teams to self-serve their namespaces while being confident that they can only use the resources allocated based on budget and business needs.

More details on [Quota](../kubernetes-resources/quota.md)

## FinOps Features

### Showback

The showback functionality in Multi Tenant Operator (MTO) Console is a significant feature designed to enhance the management of resources and costs in multi-tenant Kubernetes environments. This feature focuses on accurately tracking the usage of resources by each tenant and/or namespace, enabling organizations to monitor and optimize their expenditures.

Furthermore, this functionality supports financial planning and budgeting by offering a clear view of operational costs associated with each tenant. This can be particularly beneficial for organizations that chargeback internal departments or external clients based on resource usage, ensuring that billing is fair and reflective of actual consumption.

More details on [Showback](../console/showback.md)

### Hibernation

Multi Tenant Operator can downscale Deployments and StatefulSets in a tenant's namespace according to a defined sleep schedule. The Deployments and StatefulSets are brought back to their required replicas according to the provided wake schedule.

More details on [Hibernation](../kubernetes-resources/tenant/how-to-guides/hibernate-tenant.md) and [ResourceSupervisor](../kubernetes-resources/resource-supervisor.md)

### Capacity Planning

Provides tools to forecast and allocate resources effectively, ensuring optimal usage and preventing over-provisioning.

## Integration Features

### Hashicorp Vault Multi-tenancy

Multi Tenant Operator extends the tenant's permission model to Hashicorp Vault where it can create Vault paths and greatly ease the overhead of managing RBAC in Vault. Tenant users can manage their own secrets without the concern of someone else having access to their Vault paths.

More details on [Vault Multi-tenancy](../integrations/vault/vault.md)

### ArgoCD Multi-tenancy

Multi Tenant Operator not only provides strong multi-tenancy for the Kubernetes internals but also extends the tenant's permission model to ArgoCD where it can provision AppProjects and Allowed Repositories for your tenants, greatly easing the overhead of managing RBAC in ArgoCD.

More details on [ArgoCD Multi-tenancy](../integrations/argocd.md)

### Mattermost Multi-tenancy

Multi Tenant Operator can manage Mattermost to create teams for tenant users. All tenant users get a unique team and a list of predefined channels gets created. When a user is removed from the tenant, the user is also removed from the Mattermost team corresponding to the tenant.

More details on [Mattermost](../integrations/mattermost.md)

## Developer and Platform Productivity Features

### MTO Console

Multi Tenant Operator Console is a comprehensive user interface designed for both administrators and tenant users to manage multi-tenant environments. The MTO Console simplifies the complexity involved in handling various aspects of tenants and their related resources. It serves as a centralized monitoring hub, offering insights into the current state of tenants, namespaces, templates, and quotas. It is designed to provide a quick summary/snapshot of MTO's status and facilitates easier interaction with various resources such as tenants, namespaces, templates, and quotas.

More details on [Console](../console/overview.md)

### Remote Development Namespaces

Multi Tenant Operator can be configured to automatically provision a namespace in the cluster for every member of the specific tenant. This namespace will be preloaded with any selected templates and consume the same pool of resources from the tenant's quota, creating safe remote dev namespaces that teams can use as scratch namespaces for rapid prototyping and development. So, every developer gets a Kubernetes-based cloud development environment that feels like working on localhost.

More details on [Sandboxes](../kubernetes-resources/tenant/how-to-guides/create-sandbox.md)

## Security Features

### Cross Namespace Resource Distribution

Multi Tenant Operator supports cloning of secrets and configmaps from one namespace to another namespace based on label selectors. It uses templates to enable users to provide references to secrets and configmaps. It uses a template group instance to distribute those secrets and configmaps in matching namespaces, even if namespaces belong to different tenants. If a template instance is used, then the resources will only be mapped if namespaces belong to the same tenant.

More details on [Copying Secrets and Configmaps](../kubernetes-resources/template/how-to-guides/copying-resources.md)

### Self-Service

With Multi Tenant Operator, you can empower your users to safely provision namespaces for themselves and their teams (typically mapped to SSO groups). Team-owned namespaces and the resources inside them count towards the team's quotas rather than the user's individual limits and are automatically shared with all team members according to the access rules you configure in Multi Tenant Operator.

Also, by leveraging Multi Tenant Operator's templating mechanism, namespaces can be provisioned and automatically pre-populated with any kind of resource or multiple resources such as network policies, docker pull secrets, or even Helm charts, etc.

## Operational Features

### Everything as Code/GitOps Ready

Multi Tenant Operator is designed and built to be 100% Kubernetes-native, and to be configured and managed the same familiar way as native Kubernetes resources, so it's perfect for modern companies that are dedicated to GitOps as it is fully configurable using Custom Resources.

### Preventing Cluster Sprawl

As companies look to further harness the power of cloud-native, they are adopting container technologies at rapid speed, increasing the number of clusters and workloads. As the number of Kubernetes clusters grows, this is an increasing workload for the Ops team. When it comes to patching security issues or upgrading clusters, teams are doing five times the amount of work.

With Multi Tenant Operator, teams can share a single cluster with multiple teams, groups of users, or departments by saving operational and management efforts. This prevents you from Kubernetes cluster sprawl.

### Native Experience

Multi Tenant Operator provides multi-tenancy with a native Kubernetes experience without introducing additional management layers, plugins, or customized binaries.
