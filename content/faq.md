# FAQs

## Q. Error received while performing Create, Update or Delete action on namespace `"Cannot CREATE namespace test-john without label stakater.com/tenant"`

**A.** Error occurs when a user is trying to perform create, update, delete action on a namespace without the required `stakater.com/tenant` label. This label is used by the operator to see that authorized users can perform that action on the namespace. Just add the label with the tenant name so that MTO knows which tenant the namespace belongs to, and who is authorized to perform create/update/delete operations. For more details please refer to [Namespace use-case](./usecases/namespace.md).
