# Template

Templates are used to initialize Namespaces, share common resources across namespaces, and map secrets/ConfigMaps from one namespace to other namespaces.

They can contain pre-defined parameters such as `${namespace}`/`${tenant}`.

Also, you can define custom variables in `Template`, `TemplateInstance` and `TemplateGroupInstance`. The parameters defined in `Templates` are overwritten the values defined in `TemplateInstance` and `TemplateGroupInstance`.

## Specification

`Template` Custom Resource (CR) supports three key methods for defining and managing resources: `manifests`, `helm`, and `resource mapping`. Let’s dive into each method, their differences, and their use cases:

### 1. Manifests

This approach uses raw Kubernetes manifests (YAML files) that specify resources directly in the template.

#### How It Works

* The template includes the actual YAML specifications of resources like `Deployment`, `Service`, `ConfigMap`, etc.
* These manifests are applied as-is or with minor parameter substitutions (e.g., dynamically populated `{tenant}` and `{namespace}` variables wherever added or user defined parameters).

#### Use Cases

* Best for straightforward and simple resources where you don't need advanced templating logic or dependency management.
* Ideal when the resource definitions are static or have minimal customization needs.

#### Example

```yaml
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
```

### 2. Helm

This method integrates Helm charts into the template, allowing you to leverage Helm's templating capabilities and package management.

#### How It Works

* The `Template` references a Helm chart.
* Values for the Helm chart can be passed by the `values` field.
* The Helm chart generates the necessary Kubernetes resources dynamically at runtime.

#### Use Cases

* Best for complex resource setups with interdependencies (e.g., a microservice with a Deployment, Service, Ingress, and ConfigMap).
* Useful for resources requiring advanced templating logic or modular packaging.
* Great for managing third-party tools or applications (e.g., deploying Prometheus, Keycloak, or databases).

#### Example

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
        version: 14.6.0
        repoUrl: https://charts.bitnami.com/bitnami
        username:
          key: username
          name: redis-creds
          namespace: namespace-n1
        password:
          key: password
          name: redis-creds
          namespace: namespace-n1
    setValues:
      - name: port
        value: '6379'
        forceString: false
    values: |
      redisPort: 6379
```

A brief explanation of the fields in the Helm section:

* `releaseName`: The name of the Helm release.
* `chart`: The Helm chart details.
    * `repository`: The Helm repository details.
        * `name`: The name of the Helm repository.
        * `version`: The version of the Helm chart.
        * `repoUrl`: The URL of the Helm repository.
    * `username`: A reference to the secret containing the username for the Helm repository in case the chart is in a private repository.
        * `key`: The key in the secret containing the username.
        * `name`: The name of the secret containing the username.
        * `namespace`: The namespace of the secret containing the username.
    * `password`: A reference to the secret containing the password for the Helm repository in case the chart is in a private repository.
        * `key`: The key in the secret containing the password.
        * `name`: The name of the secret containing the password.
        * `namespace`: The namespace of the secret containing the password.
* `setValues`: The values to set in the Helm chart.
    * `name`: The name of the value.
    * `value`: The value to set.
    * `forceString`: Whether to use `--set` or `--set-string` when setting the value. Default is `false` (use `--set`).
* `values`: The values file for the Helm chart.

### 3. Resource Mapping

This approach maps secrets and ConfigMaps from one tenant's namespace to another tenant's namespace, or within a tenant's namespace.

#### How It Works

* The template contains mappings to pre-existing resources (secrets and ConfigMaps only).

#### Use Cases

* Ideal for maintaining consistency across shared resources without duplicating definitions.
* Best when resources already exist.

#### Example

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: resource-mapping
resources:
  resourceMappings:
    secrets:
      - name: secret-s1
        namespace: namespace-n1
    configmaps:
      - name: configmap-c1
        namespace: namespace-n2
```
