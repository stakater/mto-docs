# Features

The major features of Multi Tenant Operator (MTO) are described below.

## Kubernetes Multitenancy

RBAC is one of the most complicated and error-prone parts of Kubernetes. With Multi Tenant Operator, you can rest assured that RBAC is configured with the "least privilege" mindset and all rules are kept up-to-date with zero manual effort.

Multi Tenant Operator binds existing ClusterRoles to the Tenant's Namespaces used for managing access to the Namespaces and the resources they contain. You can also modify the default roles or create new roles to have full control and customize access control for your users and teams.

Multi Tenant Operator is also able to leverage existing OpenShift groups or external groups synced from 3rd party identity management systems, for maintaining Tenant membership in your organization's current user management system.

## HashiCorp Vault Multitenancy

Multi Tenant Operator is not only providing strong Multi Tenancy for the OpenShift internals but also extends the tenants permission model to HashiCorp Vault where it can create Vault paths and greatly ease the overhead of managing RBAC in Vault.

## ArgoCD Multitenancy

Multi Tenant Operator is not only providing strong Multi Tenancy for the OpenShift internals but also extends the tenants permission model to ArgoCD were it can provision AppProjects and Allowed Repositories for your tenants greatly ease the overhead of managing RBAC in ArgoCD.

## Mattermost Multitenancy

Multi Tenant Operator can manage Mattermost to create Teams for tenant users. All tenant users get a unique team and a list of predefined channels gets created. When a user is removed from the tenant, the user is also removed from the Mattermost team corresponding to tenant.

## Cost/Resource Optimization

Multi Tenant Operator provides a mechanism for defining Resource Quotas at the tenant scope, meaning all namespaces belonging to a particular tenant share the defined quota, which is why you are able to safely enable dev teams to self serve their namespaces whilst being confident that they can only use the resources allocated based on budget and business needs.

## Remote Development Namespaces

Multi Tenant Operator can be configured to automatically provision a namespace in the cluster for every member of the specific tenant, that will also be preloaded with any selected templates and consume the same pool of resources from the tenants quota creating safe remote dev namespaces that teams can use as scratch namespace for rapid prototyping and development. So, every developer gets a Kubernetes-based cloud development environment that feel like working on localhost.

## Templates and Template distribution

Multi Tenant Operator allows admins/users to define templates for namespaces, so that others can instantiate these templates to provision namespaces with batteries loaded. A template could pre-populate a namespace for certain use cases or with basic tooling required. Templates allow you to define Kubernetes manifests, Helm chart and more to be applied when the template is used to create a namespace.

Multi Tenant Operator even allows the parameterizing of these templates for flexibility and ease of use. It also provides the option to enforce the presence of templates in one tenant's or all the tenants' namespaces for configuring secure defaults.

Common use cases for namespace templates may be:

- Adding networking policies for multitenancy
- Adding development tooling to a namespace
- Deploying pre-populated databases with test data
- Equipping new namespaces with optional credentials such as image pull secrets

## Hibernation

Multi Tenant Operator can downscale Deployments and StatefulSets in a tenant's Namespace according to a defined  sleep schedule. The Deployments and StatefulSets are brought back to their required replicas according to the provided wake schedule.

## Cross Namespace Resource Distribution

Multi Tenant Operator supports cloning of secrets and configmaps from one namespace to another namespace based on label selectors. It uses templates to enable users to provide reference to secrets and configmaps. It uses a template group instance to distribute those secrets and namespaces in matching namespaces, even if namespaces belong to different tenants. If template instance is used then the resources will only be mapped if namespaces belong to same tenant.

## Self-Service

With Multi Tenant Operator, you can empower your users to safely provision namespaces for themselves and their teams (typically mapped to SSO groups). Team-owned namespaces and the resources inside them count towards the team's quotas rather than the user's individual limits and are automatically shared with all team members according to the access rules you configure in Multi Tenant Operator.

Also, by leveraging Multi Tenant Operator's templating mechanism, namespaces can be provisioned and automatically pre-populated with any kind of resource or multiple resources such as network policies, docker pull secrets or even Helm charts etc

## Everything as Code/GitOps Ready

Multi Tenant Operator is designed and built to be 100% OpenShift-native and to be configured and managed the same familiar way as native OpenShift resources so is perfect for modern shops that are dedicated to GitOps as it is fully configurable using Custom Resources.

## Preventing Clusters Sprawl

As companies look to further harness the power of cloud-native, they are adopting container technologies at rapid speed, increasing the number of clusters and workloads. As the number of Kubernetes clusters grows, this is an increasing work for the Ops team. When it comes to patching security issues or upgrading clusters, teams are doing five times the amount of work.

With Multi Tenant Operator teams can share a single cluster with multiple teams, groups of users, or departments by saving operational and management efforts. This prevents you from Kubernetes cluster sprawl.

## Native Experience

Multi Tenant Operator provides multi-tenancy with a native Kubernetes experience without introducing additional management layers, plugins, or customized binaries.
