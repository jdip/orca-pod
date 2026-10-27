# When to Mock

Keep the subject and its internal collaborators real. Substitute at an external
dependency boundary when the assertion concerns the subject's response to that
dependency, rather than the dependency's native behavior. Who owns or deploys the
dependency does not determine the test boundary.

Use small explicit substitutes for API responses, storage outcomes, time,
randomness or filesystem failures. Supply only the outcomes the case needs;
avoid reproducing the service's implementation in a fake. Assert the subject's
observable result, not its internal call sequence.

Use native integration tests for contracts that depend on real protocol, database,
permission or persistence semantics. A substitute does not prove those contracts.
Keep the adapter real when testing its translation of the external protocol.
Native service use and fresh-instance isolation are separate choices; use the
[seam and fixture-lifetime guidance](SKILL.md#seams-where-tests-go).

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint
