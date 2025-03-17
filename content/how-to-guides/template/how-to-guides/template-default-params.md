# Using Templates with Default Parameters

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: namespace-parameterized-restrictions
parameters:
  # Name of the parameter
  - name: DEFAULT_CPU_LIMIT
    # The default value of the parameter
    value: "1"
  - name: DEFAULT_CPU_REQUESTS
    value: "0.5"
    # If a parameter is required the template instance will need to set it
    # required: true
    # Make sure only values are entered for this parameter
    validation: "^[0-9]*\\.?[0-9]+$"
resources:
  manifests:
    - apiVersion: v1
      kind: LimitRange
      metadata:
        name: namespace-limit-range-${namespace}
      spec:
        limits:
          - default:
              cpu: "${{DEFAULT_CPU_LIMIT}}"
            defaultRequest:
              cpu: "${{DEFAULT_CPU_REQUESTS}}"
            type: Container
```

Parameters can be used with both `manifests` and `helm charts`
