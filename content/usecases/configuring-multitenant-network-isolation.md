# Configuring Multi-Tenant Isolation with Network Policy Template

Bill is a cluster admin who wants to configure network policies to provide multi-tenant network isolation.

First, Bill creates a template for network policies:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: tenant-network-policy
resources:
  manifests:
  - kind: NetworkPolicy
    apiVersion: networking.k8s.io/v1
    metadata:
      name: allow-same-namespace
    spec:
      podSelector: {}
      ingress:
      - from:
        - podSelector: {}
  - apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: allow-from-openshift-monitoring
    spec:
      ingress:
      - from:
        - namespaceSelector:
            matchLabels:
              network.openshift.io/policy-group: monitoring
      podSelector: {}
      policyTypes:
      - Ingress
  - apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: allow-from-openshift-ingress
    spec:
      ingress:
      - from:
        - namespaceSelector:
            matchLabels:
              network.openshift.io/policy-group: ingress
      podSelector: {}
      policyTypes:
      - Ingress
```

Once the template has been created, Bill edits the `IntegrationConfig` to add unique label to tenant projects:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: stakater-tenant-operator
spec:
  openshift:
    project:
      labels:
        stakater.com/workload-monitoring: "true"
        tenant-network-policy: "true"
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
    sandbox:
      labels:
        stakater.com/kind: sandbox
    privilegedNamespaces:
      - default
      - ^openshift-*
      - ^kube-*
    privilegedServiceAccounts:
      - ^system:serviceaccount:openshift-*
      - ^system:serviceaccount:kube-*
```

Bill has added a new label `tenant-network-policy: "true"` for tenant projects, now MTO will add that label in all projects of tenants.

Finally Bill creates a `TemplateGroupInstance` which will deploy the network policies using the newly created project label and template.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: tenant-network-policy-group
spec:
  template: tenant-network-policy
  selector:
    matchLabels:
      tenant-network-policy: "true"
  sync: true
```

MTO will now deploy the network policies mentioned in `Template` to all tenant projects.
