# Reference

## What you can tailor

The tenant boundary is the part that stays constant. Most of what surrounds it is a choice, and much of it can be changed after the stack is running.

| Choice | Options |
|:---|:---|
| Which signals you run | Logs, metrics and traces are independent — run any combination, and add another later |
| How telemetry is written | OTLP from a collector, Prometheus remote write for metrics, or Loki's push API for logs |
| Who deploys the stack | Stakater deploys all of it, or only the MTO components in front of one you already run |
| How callers are authorised at the gateways | A ServiceAccount allow-list, or Kubernetes RBAC through SubjectAccessReview |
| Which requests the gateways accept | The standard route set for each backend, plus any extra routes you add |
| How the Loki gateway reaches Loki | TLS managed with a `LokiStack`, or certificates from a Secret you supply |
| How tenant members sign in | Identity-provider details from a Secret, written inline, or single sign-on turned off |
| Which tenants receive a dashboard or data source | Every tenant, or only the ones an annotation names |
| Which group names grant which role | A templated pattern per role, so one pattern covers every tenant |
| Views across several tenants | Off, or on with a choice of role, cross-tenant traces, and dashboard sharing |

The last four rows — sign-in, targeting, role patterns and cross-tenant views — belong to the Grafana extension and are set on its `Grafana` resource, covered in [Installation](installation.md), [Choosing which tenants get a resource](choosing-which-tenants.md) and [Tenant access and roles](tenant-access-and-roles.md). The field-level reference is below.

## The `Grafana` resource

Configuration lives entirely in the `Grafana` resource (`grafanas.telemetry.tenantoperator.stakater.com`).

| Field | Default | Description |
|:---|:---|:---|
| `spec.server.name` | required | Name of the Grafana Operator instance to manage |
| `spec.server.namespace` | required | Its namespace, and the only namespace content resources are read from |
| `spec.sso.mode` | `secret` | `secret`, `inline` or `disabled` |
| `spec.sso.secretRef.name` | — | Secret holding the identity-provider details, in the extension's namespace |
| `spec.sso.idp` | — | Inline identity-provider details, for `mode: inline` |
| `spec.tenantRoleMapping.<role>.pattern` | `tenant-{{ .Tenant }}-{{ .Role }}s` | Group name to match, per role |
| `spec.tenantRoleMapping.<role>.grafanaRole` | see role table | `grafanaadmin`, `admin`, `editor`, `viewer` or `none` |
| `spec.tenantRoleMapping.tieBreakStrategy` | `highest` | Resolution when two patterns render identically: `highest`, `lowest`, `deny` |
| `spec.tenantRoleMapping.fallback` | `deny` | Server-level role when nothing matches: `deny`, `allow`, `viewer`, `editor`, `admin` |
| `spec.scaffolding.mode` | `OnAnnotation` | `OnAnnotation` or `Always` |
| `spec.scaffolding.annotations` | — | Overrides the annotation keys, via its `tenant` and `enable` entries |
| `spec.resyncInterval` | `30s`, or `10s` with aggregated views | Reconcile cadence, floored at `10s` |
| `spec.aggregatedViews` | disabled | Per-user aggregated views; see [Tenant access and roles](tenant-access-and-roles.md#one-organisation-across-a-users-tenants) |
| `spec.deletionPolicy` | `Delete` | Reserved; not acted on today |

Identity-provider fields, whether inline under `spec.sso.idp` or as keys in the SSO secret:

| Field | Default | Description |
|:---|:---|:---|
| `issuer` | required | OIDC provider URL |
| `clientId` | required | OAuth2 client ID |
| `clientSecret` | required | OAuth2 client secret |
| `redirectUri` | required | Grafana callback URL, ending in `/login/generic_oauth` |
| `scope` | `openid email profile groups offline_access` | OAuth2 scopes |
| `authUrl` | `{issuer}/dex/auth` | Authorization endpoint |
| `tokenUrl` | `{issuer}/dex/token` | Token endpoint |
| `apiUrl` | `{issuer}/dex/api` | User-info endpoint |
| `loginAttributePath` | `preferred_username` | `JMESPath` expression for the username |
| `orgAttributeName` | `groups` | Claim used for organisation mapping |
| `roleAttributeName` | `groups` | Claim used for cluster-admin detection |

## Where to go next

- [Create a tenant](../../guides/create-tenant.md) — the resource everything else is derived from.

---

**Previous:** [Operating](operating.md)
