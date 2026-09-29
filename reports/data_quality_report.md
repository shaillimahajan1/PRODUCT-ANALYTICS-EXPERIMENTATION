# Data Quality & Integrity Validation Report

**Status**: ALL CHECKS PASSED ✅
**Passed**: 9 / 9 (100.0%)

| Table / Model | Check Name | Status | Details |
|---|---|---|---|
| `dim_user` | `user_id_uniqueness` | ✅ PASSED | Total rows: 35000, Unique IDs: 35000 |
| `dim_user` | `not_null_key_attributes` | ✅ PASSED | Null counts: {'user_id': 0, 'signup_timestamp': 0, 'country': 0, 'device_type': 0} |
| `fct_events` | `event_id_uniqueness` | ✅ PASSED | Total rows: 753748, Unique IDs: 753748 |
| `fct_events` | `referential_integrity_user_id` | ✅ PASSED | Orphaned user_ids in events: 0 |
| `fct_events` | `valid_event_vocabulary` | ✅ PASSED | Invalid event names found: set() |
| `fct_sessions` | `non_negative_duration` | ✅ PASSED | Sessions with negative duration: 0 |
| `fct_sessions` | `session_id_uniqueness` | ✅ PASSED | Total rows: 241421, Unique IDs: 241421 |
| `fct_experiment_assignments` | `single_assignment_per_user_per_experiment` | ✅ PASSED | Duplicate assignments detected: 0 |
| `fct_experiment_assignments` | `valid_variant_labels` | ✅ PASSED | Null variants: 0 |