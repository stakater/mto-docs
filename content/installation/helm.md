# Helm Chart

The following options are available in the Helm Chart for Multi Tenant Operator:

```yaml
platform: Kubernetes

# bypassedGroups are the comma-separated names of groups which are bypassed in Namespace and RoleBinding webhooks
bypassedGroups: "system:cluster-admins,system:masters"

replicaCount: 1

operator:
  image:
    repository: ghcr.io/stakater/public/tenant-operator
    tag: v0.12.64
    pullPolicy: IfNotPresent
  serviceAccount:
    # Annotations to add to the service account
    annotations: {}
    # The name of the service account to use
    # If not set and create is true, a name is generated using the fullname template
    name: "controller-manager"

imagePullSecrets: []

nameOverride: ""
fullnameOverride: ""

watchNamespaces: []

# Webhook Configuration
webhook:
  enabled: true
  certificates:
    create: true

deployment:
  annotations:
    # reloader.stakater.com/auto: "true"

service:
  type: ClusterIP
  port: 443

podSecurityContext:
  runAsNonRoot: true

securityContext:
  {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

resources:
  limits:
    cpu: 100m
    memory: 2Gi
  requests:
    cpu: 10m
    memory: 200Mi

nodeSelector: {}

tolerations: []

affinity: {}

integrationConfig:
  # create: false
  accessControl:
    privileged:
      namespaces:
        - ^default$
        - ^openshift-.*
        - ^stakater-.*
        - ^kube-.*
        - ^redhat-.*
        - ^hive-.*
      serviceAccounts:
        - ^system:serviceaccount:openshift-.*
        - ^system:serviceaccount:stakater-.*
        - ^system:serviceaccount:kube-.*
        - ^system:serviceaccount:redhat-.*
        - ^system:serviceaccount:hive-.*
      groups:
        # - saap-cluster-admins
  components:
    console: false
    showback: false

userRoles:
  create: true

# Extend tenant cluster manager role
managerRoleExtendedRules:
  {}
  # - apiGroups:
  #   - user.openshift.io
  #   resources:
  #   - groups
  #   verbs:
  #   - create
  #   - delete
  #   - get
  #   - list
  #   - patch
  #   - update
  #   - watch
```
