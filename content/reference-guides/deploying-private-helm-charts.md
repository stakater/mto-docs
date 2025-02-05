# Deploying Private Helm Chart to Multiple Namespaces

Multi Tenant Operator uses its `helm` functionality from `Template` and `TemplateGroupInstance` to deploy private and public charts to multiple namespaces.

## Deploying Helm Chart to Namespaces via TemplateGroupInstances from OCI Registry

Bill, the cluster admin, wants to deploy a helm chart from `OCI` registry in namespaces where certain labels exists.

First, Bill creates a template:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: chart-deploy
resources:
  helm:
    releaseName: random-release
    chart:
      repository:
        name: random-chart
        repoUrl: 'oci://ghcr.io/stakater/charts/random-chart'
        version: 0.0.15
        password:
          key: password
          name: repo-user
          namespace: shared-ns
        username:
          key: username
          name: repo-user
          namespace: shared-ns
```

Once the template has been created, Bill makes a `TemplateGroupInstance` referring to the `Template` he wants to deploy with `MatchLabels`:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: chart-deploy
spec:
  selector:
    matchExpressions:
      - key: stakater.com/kind
        operator: In
        values:
          - system
  sync: true
  template: chart-deploy
```

Multi Tenant Operator will pick up the credentials from the mentioned namespace to pull the chart and apply it.

Afterward, Bill can see that manifests in the chart have been successfully created in all label matching namespaces.

## Deploying Helm Chart to Namespaces via TemplateGroupInstances from https Registry

Bill, the cluster admin, wants to deploy a helm chart from `HTTPS` registry in namespaces where certain labels exists.

First, Bill creates a template:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: chart-deploy
resources:
  helm:
    releaseName: random-release
    chart:
      repository:
        name: random-chart
        repoUrl: 'nexus-helm-url/registry'
        version: 0.0.15
        password:
          key: password
          name: repo-user
          namespace: shared-ns
        username:
          key: username
          name: repo-user
          namespace: shared-ns
```

Once the template has been created, Bill makes a `TemplateGroupInstance` referring to the `Template` he wants to deploy with `MatchLabels`:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: chart-deploy
spec:
  selector:
    matchExpressions:
      - key: stakater.com/kind
        operator: In
        values:
          - system
  sync: true
  template: chart-deploy
```

Multi Tenant Operator will pick up the credentials from the mentioned namespace to pull the chart and apply it.

Afterward, Bill can see that manifests in the chart have been successfully created in all label matching namespaces.
