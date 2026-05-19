# Test Design

Read this reference when choosing the shape of a behavior test, naming tests, or deciding whether a test is coupled to implementation.

## Good Tests

Good tests are behavior tests. They exercise the public interface that a real caller, user, job, command, route, or downstream module would use.

Characteristics:

- Tests behavior users or callers care about.
- Uses the public API or stable workflow only.
- Survives internal refactors.
- Describes what the system does, not how internals do it.
- Has one main behavior reason to fail.
- Uses project domain language in names and setup.

Python-flavored example:

```python
def test_user_can_checkout_with_valid_cart():
    cart = Cart()
    cart.add(Product(sku="book", price=1500))

    receipt = checkout(cart, payment_method=FakePaymentMethod.approved())

    assert receipt.status == "confirmed"
    assert receipt.total == 1500
```

This test proves an observable checkout behavior through the public checkout surface. It does not care whether checkout uses one helper, five helpers, a value object, or a different internal service later.

## Bad Tests

Bad tests are implementation-detail tests. They make private structure part of the contract.

Red flags:

- Mocking internal collaborators.
- Testing private methods or helper functions only because they are easier to reach.
- Asserting on call counts, call order, or exact internal method names.
- Failing when refactoring happens without behavior changing.
- Naming the test after the internal mechanism instead of the behavior.
- Verifying through external means when the public interface can prove the result.

Python-flavored example:

```python
def test_checkout_calls_payment_processor(mocker):
    payment_processor = mocker.patch("shop.checkout.payment_processor")

    checkout(Cart.with_item("book"), payment_method="card")

    payment_processor.charge.assert_called_once()
```

This test mostly proves a wiring detail. If checkout moves payment logic behind a deeper order module while user behavior remains correct, this test may fail for the wrong reason.

## Public Interface Verification

Prefer the interface that owns the behavior:

```python
def test_create_user_makes_user_retrievable():
    user = create_user({"name": "Alice"})

    retrieved = get_user(user.id)

    assert retrieved.name == "Alice"
```

Avoid reaching around the interface:

```python
def test_create_user_writes_database_row(db):
    create_user({"name": "Alice"})

    row = db.query_one("select * from users where name = ?", ["Alice"])

    assert row is not None
```

The database check may be appropriate only when the database contract itself is the public interface under test, such as testing a repository or migration. Otherwise, prefer proving the behavior through the caller-facing interface.

## Choosing What To Test

You cannot test everything. Prioritize:

- critical user or caller paths;
- regressions that motivated the issue;
- branching or stateful logic;
- risky integration seams;
- public interface contracts other modules depend on;
- behavior that would be expensive or embarrassing to break.

Avoid:

- tests that only mirror implementation structure;
- exhaustive edge cases with little behavior value;
- snapshots or golden files that fail on harmless structure changes;
- tests for code that should disappear when a deeper module replaces it.

## Test Naming

Name the behavior, not the implementation.

Prefer:

```text
test_trial_user_cannot_invite_more_than_three_teammates
test_checkout_rejects_expired_payment_method
test_import_skips_duplicate_rows_and_reports_count
```

Avoid:

```text
test_validate_invite_limit_called
test_checkout_uses_payment_service
test_importer_builds_seen_ids_set
```

If a test name needs an internal method name to be clear, either the test is too coupled or the public behavior has not been named precisely enough.
