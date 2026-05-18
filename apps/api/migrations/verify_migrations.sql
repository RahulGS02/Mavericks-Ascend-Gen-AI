-- ============================================================================
-- Verification Script: Check Migration Success
-- Description: Run this after migrations to verify everything is created
-- Date: 2026-05-16
-- ============================================================================

\echo '========================================'
\echo 'Migration Verification Script'
\echo '========================================'
\echo ''

-- ============================================================================
-- 1. Check if new tables exist
-- ============================================================================

\echo '1. Checking if new tables exist...'
\echo ''

SELECT 
    CASE 
        WHEN COUNT(*) = 4 THEN '✅ All 4 tables created successfully'
        ELSE '❌ Missing tables! Expected 4, found ' || COUNT(*)
    END AS table_check
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'requirement_candidates',
    'requirement_interviews',
    'requirement_workflow_history',
    'requirement_notifications'
);

\echo ''

-- List all new tables
SELECT 
    table_name,
    '✅' AS status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'requirement_candidates',
    'requirement_interviews',
    'requirement_workflow_history',
    'requirement_notifications'
)
ORDER BY table_name;

\echo ''

-- ============================================================================
-- 2. Check if new columns were added to deployment_requests
-- ============================================================================

\echo '2. Checking new columns in deployment_requests...'
\echo ''

SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable,
    '✅' AS status
FROM information_schema.columns 
WHERE table_name = 'deployment_requests' 
AND column_name IN ('positions_count', 'filled_count', 'workflow_stage')
ORDER BY column_name;

\echo ''

-- ============================================================================
-- 3. Check indexes
-- ============================================================================

\echo '3. Checking indexes...'
\echo ''

SELECT 
    schemaname,
    tablename,
    indexname,
    '✅' AS status
FROM pg_indexes 
WHERE tablename IN (
    'deployment_requests',
    'requirement_candidates',
    'requirement_interviews',
    'requirement_workflow_history',
    'requirement_notifications'
)
ORDER BY tablename, indexname;

\echo ''

-- ============================================================================
-- 4. Check constraints
-- ============================================================================

\echo '4. Checking constraints...'
\echo ''

SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    '✅' AS status
FROM information_schema.table_constraints tc
WHERE tc.table_name IN (
    'deployment_requests',
    'requirement_candidates',
    'requirement_interviews'
)
AND tc.constraint_type IN ('CHECK', 'FOREIGN KEY', 'UNIQUE')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

\echo ''

-- ============================================================================
-- 5. Check foreign key relationships
-- ============================================================================

\echo '5. Checking foreign key relationships...'
\echo ''

SELECT 
    tc.table_name AS from_table,
    kcu.column_name AS from_column,
    ccu.table_name AS to_table,
    ccu.column_name AS to_column,
    '✅' AS status
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name IN (
    'requirement_candidates',
    'requirement_interviews',
    'requirement_workflow_history',
    'requirement_notifications'
)
ORDER BY tc.table_name, kcu.column_name;

\echo ''

-- ============================================================================
-- 6. Row counts
-- ============================================================================

\echo '6. Checking row counts...'
\echo ''

SELECT 'deployment_requests' AS table_name, COUNT(*) AS row_count FROM deployment_requests
UNION ALL
SELECT 'requirement_candidates', COUNT(*) FROM requirement_candidates
UNION ALL
SELECT 'requirement_interviews', COUNT(*) FROM requirement_interviews
UNION ALL
SELECT 'requirement_workflow_history', COUNT(*) FROM requirement_workflow_history
UNION ALL
SELECT 'requirement_notifications', COUNT(*) FROM requirement_notifications
ORDER BY table_name;

\echo ''

-- ============================================================================
-- 7. Sample queries to test
-- ============================================================================

\echo '7. Testing sample queries...'
\echo ''

-- Test workflow stage values
SELECT 
    workflow_stage,
    COUNT(*) AS count
FROM deployment_requests
GROUP BY workflow_stage
ORDER BY count DESC;

\echo ''

-- ============================================================================
-- Summary
-- ============================================================================

\echo '========================================'
\echo 'Verification Complete!'
\echo '========================================'
\echo ''
\echo 'If you see ✅ marks above, migrations succeeded!'
\echo 'If you see ❌ marks, check error messages and re-run migrations.'
\echo ''
