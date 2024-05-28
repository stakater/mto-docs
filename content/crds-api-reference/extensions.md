# Extensions

Extensions in MTO enhance its functionality by allowing integration with external services. Currently, MTO supports integration with ArgoCD, enabling you to synchronize your repositories and configure AppProjects directly through MTO. Future updates will include support for additional integrations.

## Configuring ArgoCD Integration

Let us take a look at how you can create an Extension CR and integrate ArgoCD with MTO.

Before you create an Extension CR, you need to modify the Integration Config resource and add the ArgoCD configuration.

```yaml
  integrations:
    argocd:
      clusterResourceWhitelist:
        - group: tronador.stakater.com
          kind: EnvironmentProvisioner
      namespaceResourceBlacklist:
        - group: ''
          kind: ResourceQuota
      namespace: openshift-operators
```

The above configuration will allow the `EnvironmentProvisioner` CRD and blacklist the `ResourceQuota` resource. Also note that the `namespace` field is mandatory and should be set to the namespace where the ArgoCD is deployed.

Every Extension CR is associated with a specific Tenant. Here's an example of an Extension CR that is associated with a Tenant named `tenant-sample`:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Extensions
metadata:
  name: extensions-sample
spec:
  tenantName: tenant-sample
  argoCDConfig:
    purgeAppProjectOnDelete: true
    appProject:
      sourceRepos:
        - "github.com/stakater/repo"
      clusterResourceWhitelist:
        - group: ""
          kind: "Pod"
      namespaceResourceBlacklist:
        - group: "v1"
          kind: "ConfigMap"
```

The above CR creates an Extension for the Tenant named `tenant-sample` with the following configurations:

- `purgeAppProjectOnDelete`: If set to `true`, the AppProject will be deleted when the Extension is deleted.
- `sourceRepos`: List of repositories to sync with ArgoCD.
- `appProject`: Configuration for the AppProject.
    - `clusterResourceWhitelist`: List of cluster-scoped resources to sync.
    - `namespaceResourceBlacklist`: List of namespace-scoped resources to ignore.

In the backend, MTO will create an ArgoCD AppProject with the specified configurations.
