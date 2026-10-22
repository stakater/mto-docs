# Templated values in Labels and Annotations

Templated values are placeholders in your configuration that get replaced with actual data when the CR is processed. Below is a list of currently supported templated values, their descriptions, and where they can be used.

## Supported templated values

- `"{{ TENANT.USERNAME }}"`
    - **Description**: The username associated with users specified in [Tenant](../concepts/tenant.md) under `Owners` and `Editors`.
    - **Supported in CRs**:
        - `Tenant`: Under `spec.namespaces.metadata.sandbox.labels` and `spec.namespaces.metadata.sandbox.annotations`.
        - `IntegrationConfig`: Under `spec.metadata.sandboxes.labels` and `spec.metadata.sandboxes.annotations`.
    - **Example**:

      ```yaml
        annotations:
          che.eclipse.org/username: "{{ TENANT.USERNAME }}" # double quotes are required
      ```
