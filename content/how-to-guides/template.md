# Template

## Cluster scoped resource

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: redis
resources:
  helm:
    releaseName: redis
    chart:
      repository:
        name: redis
        repoUrl: https://charts.bitnami.com/bitnami
        version: 0.0.15
    values: |
      redisPort: 6379
---
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: networkpolicy
parameters:
  - name: CIDR_IP
    value: "172.17.0.0/16"
resources:
  manifests:
    - kind: NetworkPolicy
      apiVersion: networking.k8s.io/v1
      metadata:
        name: deny-cross-ns-traffic
      spec:
        podSelector:
          matchLabels:
            role: db
        policyTypes:
        - Ingress
        - Egress
        ingress:
        - from:
          - ipBlock:
              cidr: "${{CIDR_IP}}"
              except:
              - 172.17.1.0/24
          - namespaceSelector:
              matchLabels:
                project: myproject
          - podSelector:
              matchLabels:
                role: frontend
          ports:
          - protocol: TCP
            port: 6379
        egress:
        - to:
          - ipBlock:
              cidr: 10.0.0.0/24
          ports:
          - protocol: TCP
            port: 5978
---
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: resource-mapping
resources:
  resourceMappings:
    secrets:
      - name: secret-s1
        namespace: namespace-n1
    configMaps:
      - name: configmap-c1
        namespace: namespace-n2
```

Templates are used to initialize Namespaces, share common resources across namespaces, and map secrets/ConfigMaps from one namespace to other namespaces.

* They either contain one or more Kubernetes manifests, a reference to secrets/ConfigMaps, or a Helm chart.
* They are being tracked by TemplateInstances in each Namespace they are applied to.
* They can contain pre-defined parameters such as ${namespace}/${tenant} or user-defined ${MY_PARAMETER} that can be specified within an TemplateInstance.

Also, you can define custom variables in `Template` and `TemplateInstance` . The parameters defined in `TemplateInstance` are overwritten the values defined in `Template` .

Manifest Templates: The easiest option to define a Template is by specifying an array of Kubernetes manifests which should be applied when the Template is being instantiated.

Helm Chart Templates: Instead of manifests, a Template can specify a Helm chart that will be installed (using Helm template) when the Template is being instantiated.

Resource Mapping Templates: A template can be used to map secrets and ConfigMaps from one tenant's namespace to another tenant's namespace, or within a tenant's namespace.

## Mandatory and Optional Templates

Templates can either be mandatory or optional. By default, all Templates are optional. Cluster Admins can make Templates mandatory by adding them to the `spec.templateInstances` array within the Tenant configuration. All Templates listed in `spec.templateInstances` will always be instantiated within every `Namespace` that is created for the respective Tenant.
