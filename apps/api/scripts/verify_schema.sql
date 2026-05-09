SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'schools',
    'school_academics',
    'school_costs',
    'school_outcomes',
    'school_campus_life',
    'users',
    'user_preferences',
    'saved_schools',
    'comparisons',
    'comparison_schools',
    'events'
  )
ORDER BY table_name;

SELECT indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname IN (
    'ix_schools_state',
    'ix_schools_region',
    'ix_schools_type',
    'ix_schools_setting',
    'ix_schools_enrollment',
    'ix_schools_acceptance_rate',
    'ix_school_academics_graduation_rate',
    'ix_school_costs_tuition_in_state',
    'ix_school_costs_tuition_out_state',
    'ix_school_costs_net_price'
  )
ORDER BY indexname;

SELECT COUNT(*) AS seeded_school_count
FROM schools;

SELECT tc.table_name, tc.constraint_name
FROM information_schema.table_constraints tc
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name;
