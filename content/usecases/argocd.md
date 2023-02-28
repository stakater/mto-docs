# ArgoCD

## Creating ArgoCD AppProjects for your tenant

Bill wants each tenant to also have their own ArgoCD AppProjects. To make sure this happens correctly, Bill will first specify the namespace where these AppProjects will in the IntegrationConfig:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: stakater-tenant-operator
spec:
  ...
  argocd:
    namespace: openshift-operators
  ...
```

Afterwards, Bill must specify the source GitOps repos for the tenant inside the tenant CR like so:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: sigma
spec:
  argocd:
    sourceRepos:
      # specify source repos here
      - "https://github.com/stakater/GitOps-config"
  owners:
    users:
      - user
  editors:
    users:
      - user1
  quota: medium
  sandbox: false
  namespaces:
    withTenantPrefix:
      - build
      - stage
      - dev
```

Now Bill can see an AppProject will be created for the tenant

```bash
oc get AppProject -A
NAMESPACE             NAME           AGE
openshift-operators   sigma        5d15h
```

The following AppProject is created:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: sigma
  namespace: openshift-operators
spec:
  destinations:
    - namespace: sigma-build
      server: "https://kubernetes.default.svc"
    - namespace: sigma-dev
      server: "https://kubernetes.default.svc"
    - namespace: sigma-stage
      server: "https://kubernetes.default.svc"
  roles:
    - description: >-
        Role that gives full access to all resources inside the tenant's
        namespace to the tenant owner group
      groups:
        - saap-cluster-admins
        - stakater-team
        - sigma-owner-group
      name: sigma-owner
      policies:
        - "p, proj:sigma:sigma-owner, *, *, sigma/*, allow"
    - description: >-
        Role that gives edit access to all resources inside the tenant's
        namespace to the tenant owner group
      groups:
        - saap-cluster-admins
        - stakater-team
        - sigma-edit-group
      name: sigma-edit
      policies:
        - "p, proj:sigma:sigma-edit, *, *, sigma/*, allow"
    - description: >-
        Role that gives view access to all resources inside the tenant's
        namespace to the tenant owner group
      groups:
        - saap-cluster-admins
        - stakater-team
        - sigma-view-group
      name: sigma-view
      policies:
        - "p, proj:sigma:sigma-view, *, get, sigma/*, allow"
  sourceRepos:
    - "https://github.com/stakater/gitops-config"
```

Users belonging to the Sigma group will now only see applications created by them in the ArgoCD frontend now:

![image](./../images/argocd.png)

## Prevent ArgoCD from syncing certain namespaced resources

Bill wants tenants to not be able to sync `ResourceQuota` and `LimitRange` resources to their namespaces. To do this correctly, Bill will specify these resources to blacklist in the ArgoCD portion of the Integration Config's Spec:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: stakater-tenant-operator
spec:
  ...
  argocd:
    namespace: openshift-operators
    namespaceResourceBlacklist:
      - group: ""
        kind: ResourceQuota
      - group: ""
        kind: LimitRange
  ...
```

Now, if these resources are added to any tenant's project directory in GitOps, ArgoCD will not sync them to the cluster. The AppProject will also have the blacklisted resources added to it:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: sigma
  namespace: openshift-operators
spec:
  ...
  namespaceResourceBlacklist:
    - group: ''
      kind: ResourceQuota
    - group: ''
      kind: LimitRange
  ...
```

## Allow ArgoCD to sync certain cluster-wide resources

Bill now wants tenants to be able to sync the `Environment` cluster scoped resource to the cluster. To do this correctly, Bill will specify the resource to whitelist in the ArgoCD portion of the Integration Config's Spec:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: stakater-tenant-operator
spec:
  ...
  argocd:
    namespace: openshift-operators
    clusterResourceWhitelist:
      - group: ""
        kind: Environment
  ...
```

Now, if the resource is added to any tenant's project directory in GitOps, ArgoCD will sync them to the cluster. The AppProject will also have the whitelisted resources added to it:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: sigma
  namespace: openshift-operators
spec:
  ...
  clusterResourceWhitelist:
  - group: ""
    kind: Environment
  ...
```

## Override NamespaceResourceBlacklist and/or ClusterResourceWhitelist per Tenant

Bill now wants a specific tenant to override the `namespaceResourceBlacklist` and/or `clusterResourceWhitelist` set via Integration Config. Bill will specify these in `argoCD.appProjects` section of Tenant spec.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: blue-sky
spec:
  argocd:
    sourceRepos:
      # specify source repos here
      - "https://github.com/stakater/GitOps-config"
    appProject:
      clusterResourceWhitelist:
        - group: admissionregistration.k8s.io
          kind: validatingwebhookconfigurations
      namespaceResourceBlacklist:
        - group: ""
          kind: ConfigMap
  owners:
    users:
      - user
  editors:
    users:
      - user1
  quota: medium
  sandbox: false
  namespaces:
    withTenantPrefix:
      - build
      - stage
```
