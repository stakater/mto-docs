# Graph Visualization on MTO Console

Effortlessly associate tenants with their respective resources using the enhanced graph feature on the MTO console front end. This dynamic graph illustrates the relationships between tenants and the resources they create, encompassing both MTO's proprietary resources and native Kubernetes/Openshift elements.

Example Graph:

```mermaid
  graph LR;
      A(alpha)-->B(dev);
      A-->C(prod);
      B-->D(limitrange);
      B-->E(owner-rolebinding);
      B-->F(editor-rolebinding);
      B-->G(viewer-rolebinding);
      C-->H(limitrange);
      C-->I(owner-rolebinding);
      C-->J(editor-rolebinding);
      C-->K(viewer-rolebinding);
```

Explore your multi-tenant architecture with an intuitive graph that showcases the relationships between tenants and their resources. The MTO console's graph feature simplifies the understanding of complex structures, providing you with a visual representation of your system's organization. Uncover and manage your resources effortlessly with MTO's enhanced graph visualization.

To view the graph of your tenant, follow the steps below:

- Navigate to `Tenants` page on the MTO console using the left navigation bar.
![Tenants](../images/graph-1.png)
- Click on `View` of the tenant for which you want to view the graph.
![Tenant View](../images/graph-2.png)
- Click on `Graph` tab on the tenant details page.
![Tenant Graph](../images/graph-3.png)
