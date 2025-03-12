# Custom Metrics Support

Multi Tenant Operator now supports custom metrics for templates, template instances and template group instances. This feature allows users to monitor the usage of templates and template instances in their cluster.

To enable custom metrics and view them in your OpenShift cluster, you need to follow the steps below:

- Ensure that cluster monitoring is enabled in your cluster. You can check this by going to `Observe` -> `Metrics` in the OpenShift console.
- Navigate to `Administration` -> `Namespaces` in the OpenShift console. Select the namespace where you have installed Multi Tenant Operator.
- Add the following label to the namespace: `openshift.io/cluster-monitoring=true`. This will enable cluster monitoring for the namespace.
- To ensure that the metrics are being scraped for the namespace, navigate to `Observe` -> `Targets` in the OpenShift console. You should see the namespace in the list of targets.
- To view the custom metrics, navigate to `Observe` -> `Metrics` in the OpenShift console. You should see the custom metrics for templates, template instances and template group instances in the list of metrics.

Details of metrics can be found at [Metrics and Logs](./logs-metrics.md)
