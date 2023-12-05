# Custom Metrics Support

Multi Tenant Operator now supports custom metrics for templates, template instances and template group instances. This feature allows users to monitor the usage of templates and template instances in their cluster.

To enable custom metrics and view them in your openshift cluster, you need to follow the steps below:

- Ensure that cluster monitoring is enabled in your cluster. You can check this by going to `Observe` -> `Metrics` in the openshift console.
- Navigate to `Administration` -> `Namespaces` in the openshift console. Select the namespace where you have installed Multi Tenant Operator.
- Add the following label to the namespace: `openshift.io/cluster-monitoring=true`. This will enable cluster monitoring for the namespace.
- To ensure that the metrics are being scraped for the namespace, navigate to `Observe` -> `Targets` in the openshift console. You should see the namespace in the list of targets.
- To view the custom metrics, navigate to `Observe` -> `Metrics` in the openshift console. You should see the custom metrics for templates, template instances and template group instances in the list of metrics.
