# Uninstall via OperatorHub UI on OpenShift

You can uninstall MTO by following these steps:

* Decide on whether you want to retain tenant namespaces and ArgoCD AppProjects or not. If yes, please set `spec.onDelete.cleanNamespaces` to `false` for all those tenants whose namespaces you want to retain, and `spec.onDelete.cleanAppProject` to `false` for all those tenants whose AppProject you want to retain. For more details check out [onDelete](../../tutorials/tenant/deleting-tenant.md#retaining-tenant-namespaces-and-appproject-when-a-tenant-is-being-deleted)

* In case you have enabled console, you will have to disable it first by navigating to `Search` -> `IntegrationConfig` -> `tenant-operator-config` and set `spec.provision.console` and `spec.provision.showback` to `false`.

* Remove IntegrationConfig CR from the cluster by navigating to `Search` -> `IntegrationConfig` -> `tenant-operator-config` and select `Delete` from actions dropdown.

* After making the required changes open OpenShift console and click on `Operators`, followed by `Installed Operators` from the side menu

![image](../../images/installed-operators.png)

* Now click on uninstall and confirm uninstall.

![image](../../images/uninstall-from-ui.png)

* Now the operator has been uninstalled.

* `Optional:` you can also manually remove MTO's CRDs and its resources from the cluster.

## Notes

* For more details on how to use MTO please refer [Tenant's tutorial](../../tutorials/tenant/create-tenant.md).
* For more details on how to extend your MTO manager ClusterRole please refer [extend-default-clusterroles](../../how-to-guides/extend-default-roles.md).
