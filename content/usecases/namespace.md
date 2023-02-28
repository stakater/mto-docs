# Creating Namespace

Anna as the tenant owner can create new namespaces for her tenant.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bluesky-production
  labels:
    stakater.com/tenant: bluesky
```

> ⚠️ Anna is required to add the tenant label `stakater.com/tenant: bluesky` which contains the name of her tenant `bluesky`, while creating the namespace. If this label is not added or if Anna does not belong to the `bluesky` tenant, then Multi Tenant Operator will not allow the creation of that namespace.

When Anna creates the namespace, MTO assigns Anna and other tenant members the roles based on their user types, such as a tenant owner getting the OpenShift `admin` role for that namespace.

As a tenant owner, Anna is able to create namespaces.

## Add Existing Namespaces to Tenant via GitOps

Using GitOps as your preferred development workflow, you can add existing namespaces for your tenants by including the tenant label.

To add an existing namespace to your tenant via GitOps:

1. First, migrate your namespace resource to your “watched” git repository
1. Edit your namespace `yaml` to include the tenant label
1. Tenant label follows the naming convention `stakater.com/tenant: <TENANT_NAME>`
1. Sync your GitOps repository with your cluster and allow changes to be propagated
1. Verify that your Tenant users now have access to the namespace

For example, If Anna, a tenant owner, wants to add the namespace `bluesky-dev` to her tenant via GitOps, after migrating her namespace manifest to a “watched repository”

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bluesky-dev
```

She can then add the tenant label

```yaml
 ...
  labels:
    stakater.com/tenant: bluesky
```

Now all the users of the `Bluesky` tenant now have access to the existing namespace.

Additionally, to remove namespaces from a tenant, simply remove the tenant label from the namespace resource and sync your changes to your cluster.

## Remove Namespaces from your Cluster via GitOps

 GitOps is a quick and efficient way to automate the management of your K8s resources.

To remove namespaces from your cluster via GitOps;

- Remove the `yaml` file containing your namespace configurations from your “watched” git repository.
- ArgoCD automatically sets the `[app.kubernetes.io/instance](http://app.kubernetes.io/instance)` label on resources it manages. It uses this label it to select resources which inform the basis of an app. To remove a namespace from a managed ArgoCD app, remove the ArgoCD label `app.kubernetes.io/instance` from the namespace manifest.
- You can edit your namespace manifest through the OpenShift Web Console or with the OpenShift command line tool.
- Now that you have removed your namespace manifest from your watched git repository, and from your managed ArgoCD apps, sync your git repository and allow your changes be propagated.
- Verify that your namespace has been deleted.

## What’s next

See how Bill can create [templates](./template.md)
