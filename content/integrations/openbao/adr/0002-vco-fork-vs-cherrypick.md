# ADR-0002: Reuse Vault Config Operator (VCO) by cherry-picking types, not forking

- **Status:** Accepted
- **Date:** 2026-04-21
- **Decision:** Cherry-pick the 11 VCO type definitions we need and write our own controllers against our OpenBao client (Option C).

## Context

Our operator needs to manage several OpenBao resources per MTO `Tenant`: policies, Kubernetes-auth roles, PKI, Transit, cert auth, and Keycloak/OIDC login.

Red Hat CoP's [Vault Config Operator (VCO)](https://github.com/redhat-cop/vault-config-operator) already manages 47 such primitives for Vault. Of those, **11 match our needs**:

| # | VCO primitive | What it's for |
|---|---|---|
| 1 | Policy | Per-tenant ACL policies |
| 2 | KubernetesAuthEngineRole | ServiceAccount → policy |
| 3 | SecretEngineMount | Mount enable (PKI, Transit, KV) |
| 4 | PKISecretEngineConfig | Per-tenant intermediate CA |
| 5 | PKISecretEngineRole | Cert issuance rules |
| 6 | CertAuthEngineConfig | Trusted `CAs` for cert auth |
| 7 | CertAuthEngineRole | Cert-auth role → policy |
| 8 | JWTOIDCAuthEngineConfig | Keycloak OIDC mount config |
| 9 | JWTOIDCAuthEngineRole | Keycloak group → policy |
| 10 | Group | Identity Group (conditional, see ADR-0003 — TBD) |
| 11 | GroupAlias | External group → Identity Group |

Transit isn't in VCO. We'd write it from scratch regardless.

No OpenBao-native config operator exists. `openbao/openbao-secrets-operator` is unmaintained and redirects users to External Secrets Operator.

## Options

Shared context for all options below: `VCO`'s upstream tests target Vault, not OpenBao — so "inherited test coverage" from B or C doesn't include OpenBao-specific assertions. OpenBao `compat` tests are on us regardless.

### A. Use VCO as-is

Install VCO alongside our operator. Our Tenant controller generates VCO CRs; VCO applies them to OpenBao.

Pros:

- No controllers to write for 11 primitives.
- Upstream bug fixes arrive automatically.

Cons:

- Users see 47 additional CRDs. Our intended surface is `OpenBaoExtension` + MTO `Tenant`.
- Two operators to deploy and debug.
- Version skew we can't fix: VCO uses `controller-runtime v0.17.3` and a pre-1.41 Operator SDK; we're on `v0.20.4` and current. `VCO`'s Operator SDK migration ([PR #290](https://github.com/redhat-cop/vault-config-operator/pull/290)) has been open 6+ months. (Under B, we'd control this; under C, it doesn't apply.)
- `VCO`'s per-CR Kubernetes auth requires us to pre-create a "driver" SA and Vault role. The auth mismatch is solvable but moves the bootstrap work to us.

### B. Fork VCO

Copy the whole repo into `stakater-ab`, patch for OpenBao, maintain long-term.

Pros:

- We own it. Can merge PR #290, add OpenBao patches, pull upstream fixes via `rebase`.
- Inherits 15,707 LOC of tests and 47 working controllers (Vault-targeted; see shared context).

Cons:

- **Scope change.** Shipping a `stakater-ab/vault-config-operator` fork makes us an OpenBao config-operator maintainer. We inherit bug reports, feature requests, and CVE disclosures for all 47 primitives, not just the 11 we use.
- **Split focus.** Engineering attention that was on tenant fan-out now also covers `rebases`, dep bumps, CVE triage, and OpenBao-compat patches across 46,000 LOC.
- **Product identity.** A new contributor finds a Vault operator with MTO bolted on, not a focused MTO extension.
- **Security surface.** The 36 dormant primitives are reachable code paths. CVEs there flag our binary regardless of whether we use the feature.
- **Hard to undo.** Once published, a fork accumulates downstream users and custom patches. Reversing later means coordinating a migration for consumers and abandoning years of divergence — a high-cost exit.

Tactical costs (`rebase` tax, Vault SDK in `go.mod`, version skew) also apply but are secondary.

### C. Cherry-pick

Copy the 11 type files (Apache-2.0 with attribution). Write our own controllers against our existing OpenBao client ([operator source](https://github.com/stakater/mto-extension-openbao)).

Pros:

- Product identity stays focused on tenant fan-out.
- Ship one CRD (`OpenBaoExtension`). Nothing dormant.
- No Vault SDK. Our thin-client design stays intact.
- Drift we care about (OpenBao `compat`) is in code we own. Drift we don't care about (VCO tracking Vault) isn't our problem.
- Apache-2.0 bulk-copy with attribution is legally and culturally standard.

Cons:

- We write our own controllers. One-time cost.
- Upstream bug fixes don't reach us automatically. Mitigation: automated drift-check (see "Staying current" below).
- Reversing is bounded but non-trivial: the 11 copied types accumulate divergence from upstream over time, and unwinding means re-homing consumers of our CRDs. Easier than B's exit, harder than A's.
- Harder to contribute fixes back to VCO.

### D. Write from scratch

Discards `VCO`'s battle-tested schemas with no benefit over C. Apache-2.0 permits reuse.

## Decision

**Option C — cherry-pick.**

Two reasons:

1. **Scope and drift control.** We're building an MTO extension, not a general-purpose Vault config operator. We care about OpenBao compatibility; VCO tracks Vault. B forces us to own both — maintaining 47 primitives and chasing two drift streams. C lets us track only OpenBao, in code we own.

1. **Design coherence.** Our thin-client design (`baoclient.Client`, no Vault SDK) is deliberate. A fork or wrap pulls the SDK back in.

## Implementation plan

1. Create `internal/vaultobject/` — our own interface over `baoclient.Client` mirroring `VCO`'s `VaultObject` contract. Do **not** copy `VCO`'s `utils/` package (it drags in the Vault SDK).

1. Copy the 11 type files one at a time as each feature lands. Every copied file gets a header:

   ```go
   // Adapted from redhat-cop/vault-config-operator
   //   <path> @ <commit-sha>
   // Apache-2.0
   ```

1. Write controllers against our OpenBao client. Use `VCO`'s controllers as a reference; translate SDK calls to `baoclient.Client` and fit our existing status/finalizer patterns.

1. Ship a `NOTICE` file and `THIRD_PARTY_NOTICES.md` listing every copied file and its source SHA.

1. Each primitive lands with unit tests for its drift comparator and at least one integration test against a live OpenBao.

1. Write Transit from scratch.

## Staying current with upstream

Write a drift-check script that runs weekly in CI:

- Reads pinned source `SHAs` from `THIRD_PARTY_NOTICES.md`
- Fetches the current version of each file from VCO
- 3-way merges any changes onto our copy
- Opens a PR with the diff, updated SHA, and test results

Turns invisible drift into a reviewable weekly PR.
