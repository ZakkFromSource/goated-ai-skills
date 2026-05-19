# Mocking And Seams

Read this reference before mocking a dependency, introducing a fake, adding dependency injection, or designing a new seam for tests.

## What To Mock

Mock at true external or system edges:

- third-party APIs, payment providers, email/SMS providers, or remote services;
- time, randomness, process environment, and generated IDs;
- filesystem access when a local in-memory substitute is not enough;
- databases only when a test database, transaction, fixture, or repository fake is not practical;
- slow, flaky, costly, nondeterministic, or unsafe operations.

Do not mock by default:

- modules, classes, functions, or services owned by the codebase;
- internal collaborators inside the behavior being tested;
- private helpers;
- a dependency just because it makes an implementation-detail assertion easy.

The question is not "can this be mocked?" The question is "is this a real seam where behavior varies between production and test?"

## Prefer Real Owned Code

If the project owns both sides of a call, prefer exercising the real path through a public interface. Mocking owned code often locks tests to the current structure and punishes refactors.

Use a fake or in-memory adapter when it represents a true external edge:

```python
class FakeEmailGateway:
    def __init__(self):
        self.sent = []

    def send_welcome_email(self, user_email: str) -> None:
        self.sent.append(user_email)


def test_signup_sends_welcome_email():
    emails = FakeEmailGateway()

    signup = SignupService(email_gateway=emails)
    signup.create_account(email="a@example.com")

    assert emails.sent == ["a@example.com"]
```

This is useful because email delivery is an external edge. The fake captures the observable interaction without sending real email.

## Dependency Injection

Accept external dependencies instead of creating them deep inside the behavior.

Prefer:

```python
def process_payment(order, payment_client):
    return payment_client.charge(order.total)
```

Avoid:

```python
def process_payment(order):
    client = StripeClient.from_environment()
    return client.charge(order.total)
```

The first shape allows tests to supply a fake or mock at the external payment seam. The second shape forces tests to patch internals, environment variables, constructors, or network behavior.

## Specific Adapter Interfaces

Prefer specific operations over one generic fetcher or catch-all dependency. Specific interfaces make tests simpler and make behavior clearer.

Prefer:

```python
class BillingClient:
    def get_customer(self, customer_id): ...
    def create_invoice(self, customer_id, line_items): ...
    def void_invoice(self, invoice_id): ...
```

Avoid:

```python
class BillingClient:
    def request(self, endpoint, method="GET", data=None): ...
```

The specific interface means each fake method returns one specific shape, test setup has less conditional logic, and the test tells readers which external operation the behavior needs.

## Real Seam Rule

Introduce a port, adapter, protocol, interface, or dependency injection point only when there is meaningful variation across the seam.

Good reasons:

- production uses a remote service and tests use a fake;
- production reads real time and tests need fixed time;
- production writes files and tests use an in-memory filesystem or temp directory;
- production sends side effects and tests need to record them safely.

Weak reasons:

- a test wants to assert an internal call happened;
- the code would be easy to patch with a mock;
- a helper is private and hard to reach;
- a new abstraction feels tidy but has only one implementation.

One production implementation and one test fake can be enough. A seam with no real variation is usually just extra interface burden.

## Mocking Checklist

Before adding a mock, answer:

- Is this dependency outside the behavior's ownership?
- Is the dependency slow, flaky, costly, unsafe, nondeterministic, or hard to run locally?
- Would a local fake, in-memory adapter, transaction, fixture, or real test dependency be better?
- Does the test still assert observable behavior instead of internal call order?
- Will the test survive a refactor that preserves behavior?

If the answer is no, keep the test on the public interface and use real owned code.
