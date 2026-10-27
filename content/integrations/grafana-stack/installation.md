# Installation

These steps are done once per cluster, by a platform administrator, before any tenant gets an organisation. There is no per-tenant installation step.

## Deploy the stack

Loki, Mimir, Tempo, a collector and a Grafana instance must be running, with multi-tenancy enabled on Loki, Mimir and Tempo, and the MTO gateways in front of Loki and Mimir. Each component and how it can be deployed — operator or chart — is listed in [How it works → what it is made of](how-it-works.md#what-it-is-made-of). Stakater can deploy the whole stack, or only the MTO components in front of an LGTM stack you already run.

## Install the Grafana extension

The Grafana extension (the Grafana tenant operator) derives organisations, data sources, dashboards and access from your `Tenant` resources. It ships separately from MTO, and once running it watches all namespaces, so the `Grafana` resource can live wherever you prefer — the examples here use `mto-extension-grafana-system`.

!!! note "Install instructions coming"
    A public, verified install command for the Grafana tenant operator will be documented here once the operator is published. For now, **contact Stakater** to have the extension installed on your cluster.

## Prerequisites

Alongside the extension you will need:

- A Grafana instance managed by the [Grafana Operator](https://grafana.github.io/grafana-operator/docs/) — a `grafana.integreatly.org/v1beta1` `Grafana` resource. The extension configures an existing instance; it does not install or manage Grafana itself.
- The admin credentials secret the Grafana Operator creates alongside that instance: `<grafana-instance-name>-admin-credentials`, holding `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD`, in the instance's namespace. The extension calls the Grafana API with those credentials.
- MTO installed, with at least one `Tenant`.
- For user login, an OIDC provider — Dex, Keycloak, Microsoft Entra ID or any other — issuing a `groups` claim. Without one, set `sso.mode: disabled` and use Grafana's built-in accounts.

## Enabling the integration

Administrators point the extension at the Grafana instance with a `Grafana` resource. This one resource is the whole configuration surface:

```yaml
apiVersion: telemetry.tenantoperator.stakater.com/v1alpha1
kind: Grafana
metadata:
  name: mto-extension-grafana
  namespace: mto-extension-grafana-system
spec:
  server:
    name: grafana              # the Grafana Operator instance to manage
    namespace: telemetry
  sso:
    mode: secret
    secretRef:
      name: grafana-sso-credentials
  tenantRoleMapping:
    admin:
      grafanaRole: grafanaadmin
      pattern: clusteradmin || cluster-admin
    owner:
      grafanaRole: admin
      pattern: tenant-{{ .Tenant }}-{{ .Role }}s
    editor:
      grafanaRole: editor
      pattern: tenant-{{ .Tenant }}-{{ .Role }}s
    viewer:
      grafanaRole: viewer
      pattern: tenant-{{ .Tenant }}-{{ .Role }}s
    tieBreakStrategy: highest
    fallback: deny
  scaffolding:
    mode: OnAnnotation
```

Two fields carry more weight than their size suggests:

- **`spec.server`** names the Grafana instance, and also fixes the namespace content is read from. `GrafanaDatasource`, `GrafanaDashboard` and `GrafanaFolder` resources **must live in `spec.server.namespace`** — the extension ignores them anywhere else.
- **`pattern`** supports Go templating with `{{ .Tenant }}` (the tenant name) and `{{ .Role }}` (`owner`, `editor` or `viewer`), which is what lets one pattern cover every tenant, present and future.

!!! warning
    Exactly one `Grafana` resource may target a given instance. Organisations, data sources and dashboards are discovered from the instance itself and carry no per-resource ownership, so two of them on one instance would delete each other's content. If a duplicate is created, the extension keeps the longest-established one reconciling — earliest `metadata.creationTimestamp`, ties broken on `<namespace>/<name>`. The newcomer is refused: its `status.phase` becomes `Blocked`, Ready goes false with reason `Blocked`, and a `DuplicateInstanceTarget` warning event is emitted. An accidental duplicate can never take the instance from the resource already managing it.

## Connecting single sign-on

`spec.sso.mode` takes three values:

| Mode | Use case |
|:---|:---|
| `secret` (default) | Identity-provider details come from a Kubernetes secret. Recommended for production. |
| `inline` | Details written directly in `spec.sso.idp`. Convenient for development; puts a client secret in the resource. |
| `disabled` | No OAuth configuration is written. Grafana's built-in accounts only, and no organisation mapping. |

In `secret` mode, create the secret **in the same namespace as the `Grafana` extension resource**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: grafana-sso-credentials
  namespace: mto-extension-grafana-system
type: Opaque
stringData:
  issuer: https://dex.example.com
  clientId: grafana-client
  clientSecret: <client-secret>
  redirectUri: https://grafana.example.com/login/generic_oauth
```

- `issuer`, `clientId`, `clientSecret` and `redirectUri` are required.
- `scope` defaults to `openid email profile groups offline_access`.
- `authUrl`, `tokenUrl` and `apiUrl` default to `{issuer}/dex/auth`, `{issuer}/dex/token` and `{issuer}/dex/api` — set them explicitly for any provider that is not Dex.

!!! warning
    If you override `scope`, it must still contain `openid`, `email`, `profile` and `groups`. The extension validates all four and refuses to configure SSO without them — `groups` in particular is what the whole organisation mapping is built from.

From this the extension writes Grafana's `generic_oauth` settings: one `org_mapping` entry per tenant role — so three per tenant, for owners, editors and viewers — plus a `role_attribute_path` that detects cluster administrators only. Keeping tenant roles out of `role_attribute_path` is deliberate: Grafana would otherwise take the highest of the two and flatten per-organisation roles into one role everywhere.

You do not need to label the secret. The extension adds `mto.grafana/sso-secret: "true"` on first reconcile, so its informer cache watches only SSO secrets.

---

**Previous:** [How it works](how-it-works.md) · **Next:** [Giving a tenant a dashboard](giving-a-tenant-a-dashboard.md)
