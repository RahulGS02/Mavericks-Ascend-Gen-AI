-- Fix old deployment requests that were created before the migration
-- Choose ONE of the options below:

-- OPTION 1: DELETE old records (RECOMMENDED - clean start)
-- Uncomment the line below to delete old deployment requests
-- DELETE FROM deployment_requests WHERE role_title IS NULL;

-- OPTION 2: UPDATE old records with default values (keeps history)
-- Uncomment the lines below to preserve old records
UPDATE deployment_requests 
SET 
  role_title = COALESCE(project_name, 'Legacy Deployment Request'),
  required_skills = '[]',
  preferred_skills = '[]',
  role_description = COALESCE('Project: ' || project_name, 'Migrated from old system')
WHERE role_title IS NULL;

-- Verify the fix
SELECT 
  id, 
  role_title, 
  required_skills, 
  preferred_skills,
  maverick_id,
  project_name,
  status,
  created_at
FROM deployment_requests
ORDER BY created_at DESC;
