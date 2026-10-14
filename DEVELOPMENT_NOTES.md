# MENDFlow Development Notes

## Week 7 implementation checkpoint

This implementation converts the approved design into a runnable Phase II foundation.

### Reusable code examples

1. `validators.py` centralizes required-field, positive-number, and controlled-value validation.
2. `db.py` centralizes SQLite access through the `Repository` class.
3. `services.py` centralizes business workflows between the UI and repository.
4. `reports.py` provides reusable CSV generation.

### Verification focus

- Required asset code/name validation
- Positive PM frequency validation
- Controlled PM/work-order status and priority values
- Existing-asset checks before PM/work-order creation
- SQLite persistence across application restarts
- Foreign-key relationships for maintenance records

### Important scope note

The Week 3 design describes planned behavior and explicitly labels the interface mockups as design representations rather than final implementations. The current source code is the implementation checkpoint for Week 7 and should be tested locally before being presented as completed functionality.
