# Security

## The trust boundary is the namespace label

**The `stakater.com/tenant` label on a namespace is what grants a tenant's Vault access.** The parent finds a tenant's namespaces by that label, and the tenant chart renders a `Policy` and login role for every annotated ServiceAccount in them. So anyone who can set `stakater.com/tenant: X` on a namespace can give their own ServiceAccounts tenant X's Vault access.

Keep the label under the platform's control: only MTO and cluster admins may set or change it, and tenant users must not hold `patch`/`update` on `namespaces` at cluster scope. MTO's own namespace handling relies on the same label, so this is a rule MTO already needs.

Inside a tenant, the ServiceAccount annotations decide which app gets which access — anyone who can annotate a ServiceAccount in a tenant namespace can request that tenant's access for it, up to `admin`. Treat "who can annotate ServiceAccounts in a tenant namespace" as part of the tenant's own trust boundary.

## What the extension validates

- A ServiceAccount carrying no `vault.stakater.com/` annotation renders nothing.
- An unknown `vault.stakater.com/` annotation is an **error**, not ignored — the app gets a `vault-config-<sa>.error` `ConfigMap` and no access. `transit` and `pki` are rejected too (this extension does not support them).
- A cross-tenant export/import names a peer that must actually exist, or the entry is dropped.
- Tenant names are checked (DNS label, ≤63 chars, not the shared-namespace name); a tenant that fails is skipped and listed, with the reason, in a `ConfigMap` — it never breaks the other tenants.

## Template authors share these permissions

The extension runs on Template Operator v2, which renders **every** `Template` on the cluster with one ServiceAccount — the one the bootstrap grants to write VCO resources, ConfigMaps and ExternalSecrets. A `Template` can target any namespace, so **anyone who can create a `Template` and a `TemplateInstance` can use those grants**, not only this chart. With them, a hostile Template could write a VCO `Policy`/role into another tenant's Vault namespace, or an `ExternalSecret` that reads another tenant's data.

MTO's tenant roles do not include Templates by default, so tenants cannot do this out of the box. It becomes reachable the moment anyone is bound to Template Operator v2's own `template-editor`/`templateinstance-editor` roles, or an equivalent. If you grant those, confine Template Operator v2's writes with a `ValidatingAdmissionPolicy` that only allows a rendered object when its owning `TemplateInstance` is in a namespace you trust. Template Operator v2 stamps `templates.v2.stakater.com/instance-namespace` on every object it renders and overwrites any value a template sets, so the policy can trust it and a template cannot spoof it.

### Confining Template Operator v2's writes

Set `is-operator` to your Template Operator v2 identity, and list the namespaces that hold extensions (here `vault-config`) in the `validations` expression. Verified on Template Operator v2 0.0.8: cross-namespace and cluster-scoped writes from a `TemplateInstance` not on the allow-list are denied, while own-namespace and allow-listed writes pass and teardown is unaffected.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: template-operator-v2-write-scope
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["*"]
        apiVersions: ["*"]
        resources: ["*"]
        operations: ["CREATE", "UPDATE", "DELETE"]
  variables:
    - name: obj
      expression: 'request.operation == "DELETE" ? oldObject : object'
    - name: owner
      expression: 'variables.obj.metadata.?labels[?"templates.v2.stakater.com/instance-namespace"].orValue("")'
  matchConditions:
    - name: is-operator
      expression: 'request.userInfo.username == "system:serviceaccount:multi-tenant-operator:tenant-operator-template-operator-v2"'
    - name: is-rendered-object
      expression: '(object != null && "templates.v2.stakater.com/instance-namespace" in object.metadata.?labels.orValue({})) || (oldObject != null && "templates.v2.stakater.com/instance-namespace" in oldObject.metadata.?labels.orValue({}))'
  validations:
    - expression: 'variables.owner in ["vault-config"] || (has(variables.obj.metadata.namespace) && variables.obj.metadata.namespace == variables.owner)'
      messageExpression: '"template-operator-v2: a TemplateInstance in namespace " + variables.owner + " may only write objects in its own namespace"'
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata: { name: template-operator-v2-write-scope }
spec:
  policyName: template-operator-v2-write-scope
  validationActions: [Deny]
```

---

**Previous:** [Delivery and login](delivery-and-login.md) · **Next:** [Operating](operating.md)
