---
head:
  - - meta
    - name: keywords
      content: SEO plugin
---

# Introduction

[//]: # ( introduction.md, features.md)

Kubernetes is designed to support a single tenant platform; OpenShift brings some improvements with its "Secure by default" concepts but it is still very complex to design and orchestrate all the moving parts involved in building a secure multi-tenant platform hence making it difficult for cluster admins to host multi-tenancy in a single OpenShift cluster. If multi-tenancy is achieved by sharing a cluster, it can have many advantages, e.g. efficient resource utilization, less configuration effort and easier sharing of cluster-internal resources among different tenants. OpenShift and all managed applications provide enough primitive resources to achieve multi-tenancy, but it requires professional skills and deep knowledge of OpenShift.

This is where Multi Tenant Operator (MTO) comes in and provides easy to manage/configure multi-tenancy. MTO provides wrappers around OpenShift resources to provide a higher level of abstraction to users. With MTO admins can configure Network and Security Policies, Resource Quotas, Limit Ranges, RBAC for every tenant, which are automatically inherited by all the namespaces and users in the tenant. Depending on the user's role, they are free to operate within their tenants in complete autonomy.
MTO supports initializing new tenants using GitOps management pattern. Changes can be managed via PRs just like a typical GitOps workflow, so tenants can request changes, add new users, or remove users.

The idea of MTO is to use namespaces as independent sandboxes, where tenant applications can run independently of each other. Cluster admins shall configure MTO's custom resources, which then become a self-service system for tenants. This minimizes the efforts of the cluster admins.

MTO enables cluster admins to host multiple tenants in a single OpenShift Cluster, i.e.:

* Share an **OpenShift cluster** with multiple tenants
* Share **managed applications** with multiple tenants
* Configure and manage tenants and their sandboxes

MTO is also [OpenShift certified](https://catalog.redhat.com/software/operators/detail/618fa05e3adfdfc43f73b126)

## Features

The major features of Multi Tenant Operator (MTO) are described below.

## Kubernetes Multitenancy

RBAC is one of the most complicated and error-prone parts of Kubernetes. With Multi Tenant Operator, you can rest assured that RBAC is configured with the "least privilege" mindset and all rules are kept up-to-date with zero manual effort.

Multi Tenant Operator binds existing ClusterRoles to the Tenant's Namespaces used for managing access to the Namespaces and the resources they contain. You can also modify the default roles or create new roles to have full control and customize access control for your users and teams.

Multi Tenant Operator is also able to leverage existing OpenShift groups or external groups synced from 3rd party identity management systems, for maintaining Tenant membership in your organization's current user management system.

## Hashicorp Vault Multitenancy

Multi Tenant Operator extends the tenants permission model to Hashicorp Vault where it can create Vault paths and greatly ease the overhead of managing RBAC in Vault. Tenant users can manage their own secrets without the concern of someone else having access to their Vault paths.

More details on [Vault Multitenancy](./tutorials/vault/enabling-multi-tenancy-vault.md)

## ArgoCD Multitenancy

Multi Tenant Operator is not only providing strong Multi Tenancy for the OpenShift internals but also extends the tenants permission model to ArgoCD were it can provision AppProjects and Allowed Repositories for your tenants greatly ease the overhead of managing RBAC in ArgoCD.

More details on [ArgoCD Multitenancy](./tutorials/argocd/enabling-multi-tenancy-argocd.md)

## Resource Management

Multi Tenant Operator provides a mechanism for defining Resource Quotas at the tenant scope, meaning all namespaces belonging to a particular tenant share the defined quota, which is why you are able to safely enable dev teams to self serve their namespaces whilst being confident that they can only use the resources allocated based on budget and business needs.

More details on [Quota](./how-to-guides/quota.md)

## Templates and Template distribution

Multi Tenant Operator allows admins/users to define templates for namespaces, so that others can instantiate these templates to provision namespaces with batteries loaded. A template could pre-populate a namespace for certain use cases or with basic tooling required. Templates allow you to define Kubernetes manifests, Helm chart and more to be applied when the template is used to create a namespace.

It also allows the parameterizing of these templates for flexibility and ease of use. It also provides the option to enforce the presence of templates in one tenant's or all the tenants' namespaces for configuring secure defaults.

Common use cases for namespace templates may be:

* Adding networking policies for multitenancy
* Adding development tooling to a namespace
* Deploying pre-populated databases with test data
* Injecting new namespaces with optional credentials such as image pull secrets

More details on [Distributing Template Resources](./reference-guides/deploying-templates.md)

## MTO Console

Multi Tenant Operator Console is a comprehensive user interface designed for both administrators and tenant users to manage multi-tenant environments. The MTO Console simplifies the complexity involved in handling various aspects of tenants and their related resources. It serves as a centralized monitoring hub, offering insights into the current state of tenants, namespaces, templates and quotas. It is designed to provide a quick summary/snapshot of MTO's status and facilitates easier interaction with various resources such as tenants, namespaces, templates, and quotas.

More details on [Console](./explanation/console.md)

## Showback

The showback functionality in Multi Tenant Operator (MTO) Console is a significant feature designed to enhance the management of resources and costs in multi-tenant Kubernetes environments. This feature focuses on accurately tracking the usage of resources by each tenant, and/or namespace, enabling organizations to monitor and optimize their expenditures.
Furthermore, this functionality supports financial planning and budgeting by offering a clear view of operational costs associated with each tenant. This can be particularly beneficial for organizations that chargeback internal departments or external clients based on resource usage, ensuring that billing is fair and reflective of actual consumption.

More details on [Showback](./explanation/console.md#showback)

## Hibernation

Multi Tenant Operator can downscale Deployments and StatefulSets in a tenant's Namespace according to a defined  sleep schedule. The Deployments and StatefulSets are brought back to their required replicas according to the provided wake schedule.

More details on [Hibernation](./tutorials/tenant/tenant-hibernation.md#hibernating-a-tenant)

## Mattermost Multitenancy

Multi Tenant Operator can manage Mattermost to create Teams for tenant users. All tenant users get a unique team and a list of predefined channels gets created. When a user is removed from the tenant, the user is also removed from the Mattermost team corresponding to tenant.

More details on [Mattermost](./reference-guides/mattermost.md)

## Remote Development Namespaces

Multi Tenant Operator can be configured to automatically provision a namespace in the cluster for every member of the specific tenant, that will also be preloaded with any selected templates and consume the same pool of resources from the tenants quota creating safe remote dev namespaces that teams can use as scratch namespace for rapid prototyping and development. So, every developer gets a Kubernetes-based cloud development environment that feel like working on localhost.

More details on [Sandboxes](./tutorials/tenant/create-sandbox.md)

## Cross Namespace Resource Distribution

Multi Tenant Operator supports cloning of secrets and ConfigMaps from one namespace to another namespace based on label selectors. It uses templates to enable users to provide reference to secrets and ConfigMaps. It uses a template group instance to distribute those secrets and namespaces in matching namespaces, even if namespaces belong to different tenants. If template instance is used then the resources will only be mapped if namespaces belong to same tenant.

More details on [Distributing Secrets and ConfigMaps](./reference-guides/distributing-resources.md)

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
