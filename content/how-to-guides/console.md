# MTO Console

## Introduction

The Multi Tenant Operator (MTO) Console is a comprehensive user interface designed for both administrators and tenant users to manage multi-tenant environments. The MTO Console simplifies the complexity involved in handling various aspects of tenants and their related resources. 

## Dashboard Overview
The dashboard serves as a centralized monitoring hub, offering insights into the current state of tenants, namespaces, templates and quotas. It is designed to provide a quick summary/snapshot of MTO's status and facilitates easier interaction with various resources such as tenants, namespaces, templates, and quotas.

![image](../images/dashboard.png)

### Tenants
Here, admins have a bird's-eye view of all tenants, with the ability to delve into each one for detailed examination and management. This section is pivotal for observing the distribution and organization of tenants within the system. The Tenants section also provides a graph view that showcases the resources deployed under a tenant.

![image](../images/tenants.png)
![image](../images/tenant-graph.png)

### Namespaces
Users can view all the namespaces that belong to their tenant, offering a comprehensive perspective of the accessible namespaces for tenant members. This section also provides options for detailed exploration.

![image](../images/namespaces.png)

### Quotas
MTO's Quotas are crucial for managing resource allocation. In this section, administrators can assess the quotas assigned to each tenant, ensuring a balanced distribution of resources in line with operational requirements.

![image](../images/quotas.png)

### Templates
The Templates section acts as a repository for standardized resource deployment patterns, which can be utilized to maintain consistency and reliability across tenant environments. Few examples include provisioning specific k8s manifests, helm charts, secrets or configmaps across a set of namespaces.

![image](../images/templates.png)
![image](../images/templateGroupInstances.png)

### Showback
The Showback feature is an essential financial governance tool, providing detailed insights into the cost implications of resource usage by tenant or namespace or other filters. This facilitates a transparent cost management and internal chargeback or showback process, enabling informed decision-making regarding resource consumption and budgeting.

![image](../images/showback.png)

## User Roles and Permissions
### Administrators: 
Administrators have overarching access to the console, including the ability to view all namespaces and tenants. They have exclusive access to the IntegrationConfig, allowing them to define and manage system-wide settings and integrations.

![image](../images/integrationConfig.png)

### Tenant Users: 
Regular tenant users can monitor and manage their allocated resources. However, they do not have access to the IntegrationConfig and cannot view resources across different tenants, ensuring data privacy and operational integrity.

## Live YAML Configuration and Graph View

In the MTO Console, each resource section is equipped with a "View" button, revealing the live YAML configuration for complete information on the resource. For Tenant resources, a supplementary "Graph" option is available, illustrating the relationships and dependencies of all resources under a Tenant. This dual-view approach empowers users with both the detailed control of YAML and the holistic oversight of the graph view.

![image](../images/tenants_graph.png)

## Conclusion
The MTO Console is engineered to simplify complex multi-tenant management. The current iteration focuses on providing comprehensive visibility. Future updates could include direct CUD (Create/Update/Delete) capabilities from the dashboard, enhancing the console’s functionality. The Showback feature remains a standout, offering critical cost tracking and analysis. The delineation of roles between administrators and tenant users ensures a secure and organized operational framework.