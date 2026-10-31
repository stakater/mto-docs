# Templated values in Labels and Annotations

Templated values are placeholders in your configuration that get replaced with actual data when the CR is processed. Below is a list of currently supported templated values, their descriptions, and where they can be used.

## Supported templated values

- `"{{ TENANT.USERNAME }}"`
    - **Description**: The username associated with users specified in [Tenant](../concepts/tenant.md) under `Owners` and `Editors`.
    - **Supported in CRs** — the key name differs between the two, and both are correct:
        - `Tenant` (one tenant): under `spec.namespaces.metadata.sandbox.labels` and `spec.namespaces.metadata.sandbox.annotations` — the key is singular `sandbox`.
        - `IntegrationConfig` (every tenant on the cluster): under `spec.metadata.sandboxes.labels` and `spec.metadata.sandboxes.annotations` — the key is plural `sandboxes`.
    - **Example**:

      ```yaml
        annotations:
          che.eclipse.org/username: "{{ TENANT.USERNAME }}" # double quotes are required
      ```
