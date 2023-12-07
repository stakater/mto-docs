# Authentication and Authorization in MTO Console

## Keycloak for Authentication

MTO Console incorporates Keycloak, a leading authentication module, to manage user access securely and efficiently. Keycloak is provisioned automatically by our controllers, setting up a new realm, client, and a default user named 'mto'.

### Benefits `:`

- Industry Standard `:` Offers robust, reliable authentication in line with industry standards.
- Integration with Existing Systems `:` Enables easy linkage with existing Active Directories or SSO systems, avoiding the need for redundant user management.
- Administrative Control `:` Grants administrators full authority over user access to the console, enhancing security and operational integrity.

## PostgreSQL as Persistent Storage for Keycloak

MTO Console leverages PostgreSQL as the persistent storage solution for Keycloak, enhancing the reliability and flexibility of the authentication system.

It offers benefits such as enhanced data reliability, easy data export and import.

### Benefits `:`

- Persistent Data Storage: By using PostgreSQL, Keycloak's data, including realms, clients, and user information, is preserved even in the event of a pod restart. This ensures continuous availability and stability of the authentication system.
- Data Exportability: Customers can easily export Keycloak configurations and data from the PostgreSQL database.
- Transferability Across Environments: The exported data can be conveniently imported into another cluster or Keycloak instance, facilitating smooth transitions and backups.
- No Data Loss: Ensures that critical authentication data is not lost during system updates or maintenance.
- Operational Flexibility: Provides customers with greater control over their authentication data, enabling them to manage and migrate their configurations as needed.

## Built-in module for Authorization

The MTO Console is equipped with an authorization module, designed to manage access rights intelligently and securely.

### Benefits `:`

- User and Tenant Based: Authorization decisions are made based on the user's membership in specific tenants, ensuring appropriate access control.
- Role-Specific Access: The module considers the roles assigned to users, granting permissions accordingly to maintain operational integrity.
- Elevated Privileges for Admins: Users identified as administrators or members of the clusterAdminGroups are granted comprehensive permissions across the console.
- Database Caching: Authorization decisions are cached in the database, reducing reliance on the Kubernetes API server.
- Faster, Reliable Access: This caching mechanism ensures quicker and more reliable access for users, enhancing the overall responsiveness of the MTO Console.
