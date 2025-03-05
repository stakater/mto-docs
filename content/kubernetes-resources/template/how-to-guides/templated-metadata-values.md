# Templated values in Labels and Annotations

Templated values are placeholders in your configuration that get replaced with actual data when the CR is processed. Below is a list of currently supported templated values, their descriptions, and where they can be used.

## Supported templated values

- `"{{ TENANT.USERNAME }}"`
    - **Description**: The username associated with users specified in [Tenant](../../tenant/tenant-overview.md) under `Owners` and `Editors`.
    - **Supported in CRs**:
        - `Tenant`: Under `sandboxMetadata.labels` and `sandboxMetadata.annotations`.
        - `IntegrationConfig`: Under `metadata.sandboxs.labels` and `metadata.sandboxs.annotations`.
    - **Example**:

      ```yaml
        annotation:
          che.eclipse.org/username: "{{ TENANT.USERNAME }}" # double quotes are required
      ```
