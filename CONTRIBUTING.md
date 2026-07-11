# Contributing

## Principles

- Keep business rules in the domain or application layer.
- Do not call SQLAlchemy directly from API routes.
- Do not let model output authorize a monetary action.
- Prefer small protocols over broad service interfaces.
- Add a test for every state transition or policy branch.
- Keep public functions typed and names explicit.
- Record audit events for consequential state changes.

## Development

```bash
make install
make test
make lint
```

## Adding a feature

1. Express new concepts in domain types.
2. Define required ports in `domain/ports.py`.
3. Implement the use case in `application`.
4. Add infrastructure adapters.
5. Wire dependencies in `api/dependencies.py`.
6. Expose a small route, when required.
7. Add unit and API tests.
8. Update LLD and API documentation.

## Commit hygiene

- Never commit `.env`, API keys, database files, build outputs, or
  `node_modules`.
- Use focused commits.
- Explain behavior changes in the pull-request description.
