# MTO Architecture

The Multi-Tenant Operator (MTO) is a comprehensive system designed to manage multi-tenancy in Kubernetes environments. It consists of two major components: MTO Core and MTO UI, each fulfilling distinct roles in the lifecycle management of tenants.

![architecture](../images/architecture.png)

## MTO Core

The MTO Core contains a suite of controllers responsible for orchestrating tenant lifecycle operations:

**Tenant Controller**: Handles the creation and management of tenants, ensuring consistent provisioning.
**Namespace Controller**: Manages tenant-specific namespaces and enforces isolation.
**Resource Supervisor Controller**: Oversees sleep and hibernation for tenants and namespaces.
**Extensions Controller**: Provides support for extensibility by enabling integration with additional services.
**Template Quota Integration Config Controller**: Handles predifined templates, ensures quota enforcement, and manages integration configurations.
**Template Instance Controller**: Manages the lifecycle of resource instances based on predefined templates.
**Template Group Instance Controller** Manages the lifecycle of resource instances deployed as a group in multiple namespaces based on predefined templates.
**Webhook Controller**: Manages webhooks for automation and event-driven processes.
**Pilot Controller**: Acts as an interface between the MTO Core and other components, facilitating provisioning tasks.

## MTO UI

The MTO UI layer provides a user-friendly interface for interacting with the MTO system and integrates key services to enhance functionality:

**MTO Console & API Gateway**: Enable users to manage tenants, resources, and configurations efficiently.
**Keycloak**: Manages authentication and authorization, ensuring secure access control.
**Prometheus**: Monitors system health, resource usage, and performance metrics.
**OpenCost**: Provides cost visibility for tenant-specific resource consumption.
**ShowBack**: Generates detailed reports on tenant usage and resource allocation.
**PostgreSQL**: Acts as the central data store for tenant configurations, usage data, and other critical information.

## Key Features

**Extensibility**: The architecture allows integration with external tools and services to adapt to diverse use cases.
**Scalability**: Designed to manage multiple tenants effectively, scaling with growing workloads.
**Observability**: Prometheus and OpenCost provide robust monitoring and cost-tracking capabilities.
**Security**: Keycloak ensures secure authentication and access management across the system.
