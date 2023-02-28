# Distributing Secrets Using Sealed Secrets Template

Bill is a cluster admin who wants to provide a mechanism for distributing secrets in multiple namespaces. For this, he wants to use [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets#sealed-secrets-for-kubernetes) as the solution by adding them to MTO Template CR

First, Bill creates a Template in which Sealed Secret is mentioned:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: tenant-sealed-secret
resources:
  manifests:
  - kind: SealedSecret
    apiVersion: bitnami.com/v1alpha1
    metadata:
      name: mysecret
    spec:
      encryptedData:
        .dockerconfigjson: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq.....
      template:
        type: kubernetes.io/dockerconfigjson
        # this is an example of labels and annotations that will be added to the output secret
        metadata:
          labels:
            "jenkins.io/credentials-type": usernamePassword
          annotations:
            "jenkins.io/credentials-description": credentials from Kubernetes
```

Once the template has been created, Bill has to edit the `Tenant` to add unique label to namespaces in which the secret has to be deployed.
For this, he can use the support for [common](./tenant.md#distributing-common-labels-and-annotations-to-tenant-namespaces-via-tenant-custom-resource) and [specific](./tenant.md#distributing-specific-labels-and-annotations-to-tenant-namespaces-via-tenant-custom-resource) labels across namespaces.

Bill has to specify a label on namespaces in which he needs the secret. He can add it to all namespaces inside a tenant or some specific namespaces depending on the use case.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  editors:
    users:
    - john@aurora.org
    groups:
    - alpha
  quota: small
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod

  # use this if you want to add label to some specific namespaces
  specificMetadata:
    - namespaces:
        - test-namespace
      labels:
        distribute-image-pull-secret: true

  # use this if you want to add label to all namespaces under your tenant
  commonMetadata:
    labels:
      distribute-image-pull-secret: true

```

Bill has added support for a new label `distribute-image-pull-secret: true"` for tenant projects/namespaces, now MTO will add that label depending on the used field.

Finally Bill creates a `TemplateGroupInstance` which will deploy the sealed secrets using the newly created project label and template.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: tenant-sealed-secret
spec:
  template: tenant-sealed-secret
  selector:
    matchLabels:
      distribute-image-pull-secret: true
  sync: true
```

MTO will now deploy the sealed secrets mentioned in `Template` to namespaces which have the mentioned label. The rest of the work to deploy secret from a sealed secret has to be done by Sealed Secrets Controller.
