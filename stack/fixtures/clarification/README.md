# Proportional Clarification Fixtures

These YAML fixtures describe observable expectations for the integrated grill
skills. They cover lightweight evidence-only clarification, rapid questioning,
irreversible choices, architecture deep-dives, and both branches of prototype
routing.

The fixture contract is checked by `scripts/validate_skills.py`. Like the
adaptive-routing fixtures, it deliberately remains validator-owned while V2
fixture serialization matures.

Manual review should confirm that questions seek human decisions rather than
discoverable facts, deep-dive summaries preserve decision state, prototypes
produce decision evidence instead of production work, and specialist results
update the shared envelope without producing another full task closeout.
