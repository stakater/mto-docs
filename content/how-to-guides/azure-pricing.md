# Azure Pricing Model

MTO supports Azure pricing model via the `integrationConfig.components.showbackOpts.azurePricingSecretRef` field. Following 3 types of pricing are supported:

- [`Azure Pricing Configuration`](https://www.opencost.io/docs/configuration/azure#azure-pricing-configuration)
- [`Customer-specific pricing`](https://www.opencost.io/docs/configuration/azure#customer-specific-pricing)
- [`Azure Cloud Costs`](https://www.opencost.io/docs/configuration/azure#azure-cloud-costs)

## Azure Standard Pricing

For Azure pricing configuration, OpenCost needs access to the Microsoft Azure Billing Rate Card API to access accurate pricing data for your Kubernetes resources.

Follow the steps below to create a custom Azure role and secret to access the Azure Rate Card API:

### Create a Custom Azure role

Start by creating an Azure role definition. Below is an example definition, replace `YOUR_SUBSCRIPTION_ID` with the ID of the subscription containing your Kubernetes cluster. [(How to find your subscription ID.)](https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id#find-your-azure-subscription)

```json
{
    "Name": "OpenCostRole",
    "IsCustom": true,
    "Description": "Rate Card query role",
    "Actions": [
        "Microsoft.Compute/virtualMachines/vmSizes/read",
        "Microsoft.Resources/subscriptions/locations/read",
        "Microsoft.Resources/providers/read",
        "Microsoft.ContainerService/containerServices/read",
        "Microsoft.Commerce/RateCard/read"
    ],
    "AssignableScopes": [
        "/subscriptions/YOUR_SUBSCRIPTION_ID"
    ]
}
```

Save this into a file called `myrole.json`

Next, you'll want to register that role with Azure:

```bash
az role definition create --verbose --role-definition @myrole.json
```

### Create an Azure Service Principal

Next, create an Azure Service Principal.

```bash
az ad sp create-for-rbac --name "OpenCostAccess" --role "OpenCostRole" --scope "/subscriptions/YOUR_SUBSCRIPTION_ID" --output json
```

Keep this information which is used in the `service-key.json` below.

### Supply Azure Service Principal details to OpenCost

Create a file called `service-key.json` and update it with the Service Principal details from the above steps:

```json
{
    "subscriptionId": "<Azure Subscription ID>",
    "serviceKey": {
        "appId": "<Azure AD App ID>",
        "displayName": "OpenCostAccess",
        "password": "<Azure AD Client Secret>",
        "tenant": "<Azure AD Tenant ID>"
    }
}
```

Next, create a secret for the Azure Service Principal

!!! note
    When managing the service account key as a Kubernetes secret, the secret must reference the service account key JSON file, and that file must be named `service-key.json`.

```bash
kubectl create secret generic azure-service-key -n multi-tenant-operator --from-file=service-key.json
```

### Update the IntegrationConfig

Finally, update the IntegrationConfig with the Azure pricing model:

```yaml
components:
    console: true # should be enabled
    showback: true # should be enabled
    showbackOpts:
      azurePricingSecretRef:
        name: azure-service-key
        namespace: multi-tenant-operator
```

## Customer-specific pricing

The Rate Card prices retrieved with the setup above are the standard prices for Azure resources offered to all customers. If your organisation has an Enterprise Agreement or Partner Agreement with Azure you may have discounts for some of the resources used by your clusters. In that case you can configure OpenCost to use the [Consumption Price Sheet API](https://learn.microsoft.com/en-us/rest/api/consumption/) to request prices specifically for your billing account.

!!! note
    Calling the Price Sheet API uses the service principal secret created above - those steps are prerequisites for this section.

### Find your billing account ID

You can find your billing account ID in the Azure portal, or using the `az` CLI:

```bash
az billing account list --query "[].{name:name, displayName:displayName}"
```

### Grant billing access to your Service Principal

To call the Price Sheet API the service principal you created above needs to be granted the EnrollmentReader billing role. You can do this by following [this Azure guide](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/assign-roles-azure-service-principals#assign-enrollment-account-role-permission-to-the-spn) and using the [Role Assignments API reference page](https://learn.microsoft.com/en-us/rest/api/billing/2019-10-01-preview/role-assignments/put?tabs=HTTP).

Assigning a billing role isn't directly supported in the `az` CLI yet, so the process is quite involved. To simplify this, you can use the `Bash` script [below](./azure-pricing.md#script-to-assign-billing-role) to collect the details of your service principal, construct the PUT request and send it with curl.

Save the script to a file named `assign-billing-role.bash` and run it:

```bash
export SP_NAME=OpenCostAccess
export BILLING_ACCOUNT_ID=<your billing account ID>
chmod u+x assign-billing-role.bash
./assign-billing-role.bash
```

### Find the offer ID for your subscription

As well as the billing account ID, OpenCost also needs the offer ID for your subscription to query the price sheet. You can find this on the [subscription page in the Azure portal](https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id#find-your-azure-subscription).

### Configure OpenCost to use the Price Sheet API

The billing account and offer ID need to be passed to OpenCost in environment variables. To do this, create a secret with the following values:

```bash
kubectl create secret generic customer-specific-pricing -n multi-tenant-operator --from-literal=azure-billing-account=<your billing account ID> --from-literal=azure-offer-id=<your offer ID>
```

Finally, update the IntegrationConfig with the Azure pricing model:

```yaml
components:
    console: true # should be enabled
    showback: true # should be enabled
    showbackOpts:
      azurePricingSecretRef:
        name: customer-specific-pricing
        namespace: multi-tenant-operator
```

### Script to assign billing role

```bash
#!/bin/bash

# Helper to assign the billing EnrollmentReader role to a service principal
# Needs SP name and billing account name variables set

set -euo pipefail

if [[ -z "${SP_NAME}" ]]; then
  echo "SP_NAME is not set"
  exit 1
fi

if [[ -z "${BILLING_ACCOUNT_ID}" ]]; then
  echo "BILLING_ACCOUNT_ID is not set"
  exit 1
fi

# Generate a unique name for the assignment.
ROLE_ASSIGNMENT_NAME="$(uuidgen)"

# Work out the SP ID and tenant ID from the name.
read -r SP_ID TENANT_ID < <(az ad sp list --display-name "${SP_NAME}" --query '[0].{id:id,tenantId:appOwnerOrganizationId}' -o tsv)

# Get bearer token for talking to API.
ACCESS_TOKEN="$(az account get-access-token --query accessToken -o tsv)"

URL="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/${BILLING_ACCOUNT_ID}/billingRoleAssignments/${ROLE_ASSIGNMENT_NAME}?api-version=2019-10-01-preview"

echo "Creating EnrollmentReader role assignment for SP ${SP_NAME} (${SP_ID}) in billing account ${BILLING_ACCOUNT_ID}"
echo "Role assignment name: ${ROLE_ASSIGNMENT_NAME}"

# This is the role definition ID for EnrollmentReader
ENROLLMENT_READER_ROLE="24f8edb6-1668-4659-b5e2-40bb5f3a7d7e"
RESPONSE="$(curl --silent --show-error -X PUT "${URL}" \
-H "Authorization: Bearer ${ACCESS_TOKEN}" \
-H "Content-type: application/json" \
-d "{
  \"properties\": {
    \"principalId\": \"${SP_ID}\",
    \"principalTenantId\": \"${TENANT_ID}\",
    \"roleDefinitionId\": \"/providers/Microsoft.Billing/billingAccounts/${BILLING_ACCOUNT_ID}/billingRoleDefinitions/${ENROLLMENT_READER_ROLE}\"
  }
}")"

echo "Response: ${RESPONSE}"
```

## Conclusion

In this guide, we have seen how to configure OpenCost to use Azure pricing model. We have seen how to configure Azure Pricing Configuration, Customer-specific pricing, and Azure Cloud Costs. To enable all three pricing models, you can create a single secret with all the required values and update the IntegrationConfig to use the secret.

for example:

```bash
kubectl create secret generic azure-pricing -n multi-tenant-operator --from-file=service-key.json --from-literal=azure-billing-account=<your billing account ID> --from-literal=azure-offer-id=<your offer ID> --from-file=./cloud-integration.json
```

Update the IntegrationConfig to use the secret:

```yaml
components:
    console: true # should be enabled
    showback: true # should be enabled
    showbackOpts:
      azurePricingSecretRef:
        name: azure-pricing
        namespace: multi-tenant-operator
```

For more information, refer to the [OpenCost documentation](https://www.opencost.io/docs/configuration/azure).
