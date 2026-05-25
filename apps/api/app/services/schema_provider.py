"""
Database Schema Provider for Natural Language to SQL
Provides comprehensive schema information to AI for accurate SQL generation
"""


def get_database_schema_context() -> str:
    """
    Returns complete database schema with relationships, data types, and constraints
    This helps AI generate valid, error-free PostgreSQL queries
    """
    
    schema = """
=================================================================================
MAVERICKS ASCEND PLATFORM - POSTGRESQL DATABASE SCHEMA
=================================================================================

DATABASE: PostgreSQL 14+
IMPORTANT: All IDs are UUID type. Use proper UUID syntax in queries.
IMPORTANT: All ENUM values are case-sensitive strings.
IMPORTANT: Use proper PostgreSQL date/time functions (NOW(), CURRENT_DATE, etc.)
IMPORTANT: JSONB fields contain arrays or objects - use JSONB operators.

=================================================================================
TABLE: mavericks (Trainee Profiles)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY - Unique maverick identifier
  user_id               UUID            FOREIGN KEY → users.id (nullable, unique)
  name                  VARCHAR(255)    NOT NULL - Maverick full name
  email                 VARCHAR(255)    NOT NULL, UNIQUE - Email address (indexed)
  phone                 VARCHAR(20)     Phone number
  college               VARCHAR(255)    College/University name
  degree                VARCHAR(255)    Degree name (e.g., "B.Tech")
  branch                VARCHAR(255)    Branch/Major (e.g., "Computer Science")
  graduation_year       INTEGER         Year of graduation
  cgpa                  INTEGER         CGPA score (0-10 scale)
  
  github_url            TEXT            GitHub profile URL
  linkedin_url          TEXT            LinkedIn profile URL
  resume_url            TEXT            Resume file URL
  
  skills                JSONB           Array of self-declared skills (e.g., ["Python", "React"])
  ai_extracted_skills   JSONB           Array of AI-parsed skills from resume
  ai_summary            TEXT            AI-generated profile summary
  ai_resume_data        JSONB           Complete AI-parsed resume data (education, experience, projects)
  
  profile_status        VARCHAR(20)     NOT NULL, INDEXED - Enum: 'pending', 'approved', 'rejected'
  deployment_status     VARCHAR(20)     NOT NULL, INDEXED - Enum: 'AVAILABLE', 'DEPLOYED', 'ON_LEAVE', 'TERMINATED'
  
  review_notes          TEXT            Notes from reviewer
  reviewed_by           UUID            FOREIGN KEY → users.id (who reviewed)
  
  current_batch_id      UUID            FOREIGN KEY → batches.id (current assigned batch, nullable)
  
  created_at            TIMESTAMP       NOT NULL - Record creation time
  updated_at            TIMESTAMP       NOT NULL - Last update time

RELATIONSHIPS:
  - ONE user (via user_id)
  - ONE current_batch (via current_batch_id)
  - MANY skill_proficiencies (→ maverick_skills.maverick_id)
  - MANY job_progress (→ maverick_job_progress.maverick_id)
  - MANY assessment_attempts (→ assessment_attempts.maverick_id)
  - MANY deployments (→ deployments.maverick_id)

COMMON QUERIES:
  - Available for deployment: WHERE deployment_status = 'AVAILABLE' AND profile_status = 'approved'
  - In training: WHERE current_batch_id IS NOT NULL
  - Skilled in X: JOIN maverick_skills WHERE skill_name = 'Python'
  - Graduated in year: WHERE graduation_year = 2024

=================================================================================
TABLE: maverick_skills (Skill Proficiency Tracking)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  maverick_id           UUID            NOT NULL, FOREIGN KEY → mavericks.id (CASCADE DELETE)
  skill_name            VARCHAR(255)    NOT NULL - Skill name (e.g., "Python", "React", "Leadership")
  category              VARCHAR(50)     Skill category: 'TECHNICAL', 'PROGRAMMING_LANGUAGE', 'FRAMEWORK', 'TOOL', 'DATABASE', 'SOFT_SKILL', 'OTHER'
  
  proficiency_score     FLOAT           NOT NULL, DEFAULT 0.0 - Score 0-100
  proficiency_level     VARCHAR(50)     Level: 'BEGINNER', 'INTERMEDIATE', 'PROFICIENT'
  
  assessment_score      FLOAT           Score from assessments (0-100)
  training_completion   FLOAT           Training completion % (0-100)
  self_declared         FLOAT           Self-assessment score (0-100)
  ai_analyzed           FLOAT           AI-analyzed score from resume/projects (0-100)
  
  assessment_count      INTEGER         DEFAULT 0 - Number of assessments taken
  training_count        INTEGER         DEFAULT 0 - Number of trainings completed
  last_assessed_at      TIMESTAMP       Last assessment date
  last_trained_at       TIMESTAMP       Last training date
  
  ai_feedback           TEXT            AI-generated feedback on skill
  improvement_suggestions JSONB         AI suggestions for improvement
  radar_data            JSONB           Pre-computed radar chart data
  
  created_at            TIMESTAMP
  updated_at            TIMESTAMP

RELATIONSHIPS:
  - ONE maverick (via maverick_id)

COMMON QUERIES:
  - High proficiency: WHERE proficiency_score >= 80
  - Specific skill: WHERE skill_name = 'Python'
  - Category filter: WHERE category = 'PROGRAMMING_LANGUAGE'
  - Top skilled: ORDER BY proficiency_score DESC LIMIT 10

=================================================================================
TABLE: batches (Training Batches)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  name                  VARCHAR(255)    NOT NULL, UNIQUE - Batch name
  description           TEXT            Batch description
  pipeline_id           UUID            NOT NULL, FOREIGN KEY → pipelines.id
  
  category              VARCHAR(50)     Batch category: 'TECH_DEVELOPMENT', 'TECH_DEVOPS', 'TECH_TESTING', 'TECH_DATA_SCIENCE', 'TECH_CYBER_SECURITY', 'SOFT_SKILLS'
  focus_areas           TEXT[]          Array of focus areas (e.g., ["React", "Node.js", "AWS"])
  required_skills       TEXT[]          Array of must-have skills
  preferred_skills      TEXT[]          Array of nice-to-have skills
  target_role           VARCHAR(255)    Target job role (e.g., "Full Stack Developer")
  
  start_date            DATE            Batch start date
  end_date              DATE            Batch end date
  
  max_capacity          INTEGER         Maximum number of students
  current_enrollment    INTEGER         NOT NULL, DEFAULT 0 - Current number of students
  
  trainer_id            UUID            FOREIGN KEY → users.id (legacy single trainer)
  created_by            UUID            NOT NULL, FOREIGN KEY → users.id
  
  status                VARCHAR(20)     NOT NULL - Enum: 'PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'ON_HOLD', 'ARCHIVED'
  
  created_at            TIMESTAMP       NOT NULL
  updated_at            TIMESTAMP

RELATIONSHIPS:
  - ONE pipeline (via pipeline_id)
  - ONE trainer (via trainer_id - legacy)
  - MANY batch_trainers (→ batch_trainers.batch_id - new multi-trainer support)
  - MANY mavericks (← mavericks.current_batch_id)
  - MANY job_schedules (→ batch_job_schedule.batch_id)

COMMON QUERIES:
  - Active batches: WHERE status = 'ACTIVE'
  - Starting this month: WHERE start_date >= DATE_TRUNC('month', CURRENT_DATE)
  - Full batches: WHERE current_enrollment >= max_capacity
  - By category: WHERE category = 'TECH_DEVELOPMENT'

=================================================================================
TABLE: users (All Platform Users)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  email                 VARCHAR(255)    NOT NULL, UNIQUE, INDEXED - User email
  password_hash         VARCHAR(255)    NOT NULL - Hashed password (never query this in SELECT)
  name                  VARCHAR(255)    NOT NULL - User full name
  role                  VARCHAR(20)     NOT NULL, INDEXED - Enum: 'maverick', 'trainer', 'hr', 'manager', 'super_admin'
  is_active             BOOLEAN         NOT NULL, DEFAULT TRUE - Account active status
  created_at            TIMESTAMP       NOT NULL
  last_login            TIMESTAMP       Last login time

RELATIONSHIPS:
  - ONE maverick profile (← mavericks.user_id)
  - MANY created_pipelines (← pipelines.created_by)
  - MANY trained_batches (← batches.trainer_id)
  - MANY trainer_assignments (← batch_trainers.trainer_id)

COMMON QUERIES:
  - Trainers: WHERE role = 'trainer' AND is_active = TRUE
  - Admins: WHERE role IN ('super_admin', 'manager', 'hr')
  - Active users: WHERE is_active = TRUE

=================================================================================
TABLE: batch_trainers (Multi-Trainer Assignment)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  batch_id              UUID            NOT NULL, FOREIGN KEY → batches.id (CASCADE DELETE)
  trainer_id            UUID            NOT NULL, FOREIGN KEY → users.id (CASCADE DELETE)
  is_lead_trainer       BOOLEAN         NOT NULL, DEFAULT FALSE - Primary trainer flag
  assigned_at           TIMESTAMP       NOT NULL, DEFAULT NOW()
  assigned_by           UUID            FOREIGN KEY → users.id (who assigned)

UNIQUE CONSTRAINT: (batch_id, trainer_id) - A trainer can't be assigned to same batch twice

RELATIONSHIPS:
  - ONE batch (via batch_id)
  - ONE trainer (via trainer_id)

COMMON QUERIES:
  - Trainers for batch: WHERE batch_id = 'uuid'
  - Lead trainer: WHERE batch_id = 'uuid' AND is_lead_trainer = TRUE
  - Batches by trainer: WHERE trainer_id = 'uuid'

=================================================================================
TABLE: pipelines (Training Programs)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  name                  VARCHAR(255)    NOT NULL - Pipeline name
  description           TEXT            Pipeline description
  created_by            UUID            NOT NULL, FOREIGN KEY → users.id
  created_at            TIMESTAMP       NOT NULL
  updated_at            TIMESTAMP
  is_template           BOOLEAN         NOT NULL, DEFAULT FALSE - Is this a template?
  status                VARCHAR(20)     NOT NULL - Enum: 'DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED'

RELATIONSHIPS:
  - ONE creator (via created_by → users.id)
  - MANY jobs (→ pipeline_jobs.pipeline_id)
  - MANY batches (→ batches.pipeline_id)

COMMON QUERIES:
  - Active pipelines: WHERE status = 'ACTIVE'
  - Templates: WHERE is_template = TRUE

=================================================================================
TABLE: pipeline_jobs (Training Stages/Jobs)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  pipeline_id           UUID            NOT NULL, FOREIGN KEY → pipelines.id (CASCADE DELETE)
  name                  VARCHAR(255)    NOT NULL - Job name
  job_type              VARCHAR(20)     NOT NULL - Enum: 'TRAINING', 'ASSESSMENT', 'DEPLOYMENT'
  sequence_order        INTEGER         NOT NULL - Order in pipeline (1, 2, 3...)
  is_mandatory          BOOLEAN         NOT NULL, DEFAULT TRUE - Is this job required?
  duration_days         INTEGER         Estimated duration in days
  description           TEXT            Job description
  prerequisites         TEXT            Prerequisites text
  status                VARCHAR(20)     NOT NULL - Enum: 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'SKIPPED'
  job_metadata          JSONB           Job-specific configuration
  created_at            TIMESTAMP       NOT NULL
  updated_at            TIMESTAMP

RELATIONSHIPS:
  - ONE pipeline (via pipeline_id)
  - MANY progress_records (→ maverick_job_progress.job_id)
  - MANY batch_schedules (→ batch_job_schedule.job_id)

COMMON QUERIES:
  - Training jobs: WHERE job_type = 'TRAINING'
  - Ordered jobs: ORDER BY sequence_order ASC
  - Mandatory jobs: WHERE is_mandatory = TRUE

=================================================================================
TABLE: deployments (Final Deployment Records)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  maverick_id           UUID            NOT NULL, FOREIGN KEY → mavericks.id (CASCADE DELETE)
  batch_id              UUID            FOREIGN KEY → batches.id

  project_name          VARCHAR(255)    NOT NULL - Project name
  vertical              VARCHAR(100)    NOT NULL - Industry vertical (Banking, Healthcare, etc.)
  competency            VARCHAR(100)    NOT NULL - Technical competency (Backend, Frontend, etc.)
  role                  VARCHAR(255)    Job role title
  manager_name          VARCHAR(255)    Manager name
  location              VARCHAR(255)    Work location

  start_date            DATE            NOT NULL - Deployment start date
  end_date              DATE            Deployment end date (null if ongoing)

  status                VARCHAR(20)     NOT NULL - Enum: 'ACTIVE', 'COMPLETED', 'TERMINATED'

  deployed_by           UUID            NOT NULL, FOREIGN KEY → users.id
  deployed_at           TIMESTAMP       NOT NULL
  notes                 TEXT            Deployment notes
  created_at            TIMESTAMP       NOT NULL
  updated_at            TIMESTAMP

RELATIONSHIPS:
  - ONE maverick (via maverick_id)
  - ONE batch (via batch_id)

COMMON QUERIES:
  - Active deployments: WHERE status = 'ACTIVE'
  - By vertical: WHERE vertical = 'Banking'
  - Recent deployments: WHERE deployed_at >= CURRENT_DATE - INTERVAL '30 days'
  - Ended deployments: WHERE end_date IS NOT NULL

=================================================================================
TABLE: deployment_requests (Deployment Requirements)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  maverick_id           UUID            FOREIGN KEY → mavericks.id (assigned later, nullable)
  requested_by          UUID            NOT NULL, FOREIGN KEY → users.id (Manager/HR)

  role_title            VARCHAR(255)    NOT NULL - Role title (e.g., "Senior Full Stack Developer")
  role_description      TEXT            Detailed role requirements
  required_skills       TEXT            JSON array as text (required skills)
  preferred_skills      TEXT            JSON array as text (preferred skills)

  project_name          VARCHAR(255)    Project name
  vertical              VARCHAR(100)    Industry vertical
  competency            VARCHAR(100)    Technical competency
  justification         TEXT            Business justification

  status                VARCHAR(20)     NOT NULL - Enum: 'PENDING', 'APPROVED', 'REJECTED'
  approved_by           UUID            FOREIGN KEY → users.id
  approved_at           TIMESTAMP
  rejection_reason      TEXT

  positions_count       INTEGER         NOT NULL, DEFAULT 1 - Number of positions
  filled_count          INTEGER         NOT NULL, DEFAULT 0 - Positions filled
  workflow_stage        VARCHAR(50)     DEFAULT 'PENDING' - Current workflow stage

  created_at            TIMESTAMP       NOT NULL
  updated_at            TIMESTAMP

RELATIONSHIPS:
  - ONE maverick (via maverick_id, nullable)
  - ONE requester (via requested_by → users.id)

COMMON QUERIES:
  - Pending requests: WHERE status = 'PENDING'
  - Unfilled positions: WHERE filled_count < positions_count
  - By vertical: WHERE vertical = 'Banking'

=================================================================================
TABLE: assessments (Assessment Configuration)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  job_id                UUID            NOT NULL, FOREIGN KEY → pipeline_jobs.id
  batch_id              UUID            NOT NULL, FOREIGN KEY → batches.id (CASCADE DELETE)

  title                 VARCHAR(255)    NOT NULL - Assessment title
  description           TEXT            Assessment description
  assessment_link       VARCHAR(500)    Link to assessment (Google Form, etc.)
  max_marks             NUMERIC(5,2)    NOT NULL - Maximum marks
  passing_marks         NUMERIC(5,2)    NOT NULL - Passing threshold
  duration_minutes      INTEGER         Assessment duration in minutes
  scheduled_date        TIMESTAMP       When assessment is scheduled

  config_metadata       JSONB           Assessment metadata (skills tested, etc.)

  created_by            UUID            NOT NULL, FOREIGN KEY → users.id
  created_at            TIMESTAMP       NOT NULL
  updated_at            TIMESTAMP

RELATIONSHIPS:
  - ONE job (via job_id)
  - ONE batch (via batch_id)
  - MANY attempts (→ assessment_attempts.assessment_id)

COMMON QUERIES:
  - By batch: WHERE batch_id = 'uuid'
  - Scheduled soon: WHERE scheduled_date >= NOW() AND scheduled_date <= NOW() + INTERVAL '7 days'

=================================================================================
TABLE: assessment_attempts (Assessment Results)
=================================================================================
PRIMARY KEY: id (UUID)

COLUMNS:
  id                    UUID            PRIMARY KEY
  assessment_id         UUID            NOT NULL, FOREIGN KEY → assessments.id (CASCADE DELETE)
  maverick_id           UUID            NOT NULL, FOREIGN KEY → mavericks.id (CASCADE DELETE)
  batch_id              UUID            NOT NULL, FOREIGN KEY → batches.id (CASCADE DELETE)

  marks_obtained        NUMERIC(5,2)    NOT NULL - Marks scored
  max_marks             NUMERIC(5,2)    NOT NULL - Maximum marks
  passed                BOOLEAN         NOT NULL - Did student pass?
  feedback              TEXT            Evaluator feedback

  evaluated_by          UUID            NOT NULL, FOREIGN KEY → users.id
  evaluated_at          TIMESTAMP       NOT NULL - When evaluated
  created_at            TIMESTAMP       NOT NULL

RELATIONSHIPS:
  - ONE assessment (via assessment_id)
  - ONE maverick (via maverick_id)
  - ONE batch (via batch_id)

COMMON QUERIES:
  - Passed attempts: WHERE passed = TRUE
  - By maverick: WHERE maverick_id = 'uuid'
  - Average score: AVG(marks_obtained / max_marks * 100)
  - Recent attempts: WHERE evaluated_at >= CURRENT_DATE - INTERVAL '30 days'

=================================================================================
IMPORTANT POSTGRESQL QUERY RULES
=================================================================================

1. UUID SYNTAX:
   - Use single quotes: WHERE id = '550e8400-e29b-41d4-a716-446655440000'
   - Use :: for casting: WHERE id = '550e8400-e29b-41d4-a716-446655440000'::uuid

2. ENUM VALUES:
   - Always use exact case: WHERE deployment_status = 'AVAILABLE' (not 'available')
   - Profile status lowercase: WHERE profile_status = 'approved' (not 'APPROVED')
   - Batch status uppercase: WHERE status = 'ACTIVE' (not 'active')

3. DATE/TIME FUNCTIONS:
   - Current date: CURRENT_DATE
   - Current timestamp: NOW() or CURRENT_TIMESTAMP
   - Date truncation: DATE_TRUNC('month', date_column)
   - Date arithmetic: CURRENT_DATE - INTERVAL '30 days'

4. JSONB OPERATIONS:
   - Check if array contains: WHERE skills @> '["Python"]'::jsonb
   - Extract array element: skills->0 (first element)
   - Array length: jsonb_array_length(skills)

5. TEXT ARRAY:
   - Check contains: WHERE 'Python' = ANY(focus_areas)
   - Array length: array_length(focus_areas, 1)

6. JOINS:
   - Always use explicit JOIN syntax
   - Specify join conditions clearly
   - Use table aliases for readability

7. AGGREGATIONS:
   - Use proper GROUP BY for aggregates
   - COUNT(*) for total rows
   - AVG(), SUM(), MIN(), MAX() available

8. LIMITS:
   - Always add LIMIT clause (max 1000)
   - Use OFFSET for pagination

9. SAFE QUERIES ONLY:
   - ONLY SELECT statements allowed
   - NO INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE
   - NO UNION, EXEC, or SQL injection attempts

=================================================================================
EXAMPLE VALID QUERIES
=================================================================================

Example 1: "Show me mavericks available for deployment"
SELECT m.id, m.name, m.email, m.skills, m.cgpa, m.college
FROM mavericks m
WHERE m.deployment_status = 'AVAILABLE'
  AND m.profile_status = 'approved'
ORDER BY m.name
LIMIT 100;

Example 2: "List Python developers with proficiency > 80"
SELECT m.name, m.email, ms.skill_name, ms.proficiency_score
FROM mavericks m
INNER JOIN maverick_skills ms ON m.id = ms.maverick_id
WHERE ms.skill_name = 'Python'
  AND ms.proficiency_score > 80
ORDER BY ms.proficiency_score DESC
LIMIT 100;

Example 3: "Show active batches with enrollment count"
SELECT b.name, b.start_date, b.end_date, b.current_enrollment, b.max_capacity,
       (b.current_enrollment::float / NULLIF(b.max_capacity, 0) * 100) as fill_percentage
FROM batches b
WHERE b.status = 'ACTIVE'
ORDER BY b.start_date
LIMIT 100;

Example 4: "Find mavericks who passed recent assessments"
SELECT DISTINCT m.name, m.email, aa.marks_obtained, aa.max_marks, aa.evaluated_at
FROM mavericks m
INNER JOIN assessment_attempts aa ON m.id = aa.maverick_id
WHERE aa.passed = TRUE
  AND aa.evaluated_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY aa.evaluated_at DESC
LIMIT 100;

Example 5: "Show trainers and their batch counts"
SELECT u.name, u.email, COUNT(bt.batch_id) as batch_count
FROM users u
LEFT JOIN batch_trainers bt ON u.id = bt.trainer_id
WHERE u.role = 'trainer' AND u.is_active = TRUE
GROUP BY u.id, u.name, u.email
ORDER BY batch_count DESC
LIMIT 100;

=================================================================================
"""

    return schema.strip()


def get_schema_summary() -> str:
    """Returns a brief schema summary for quick reference"""
    return """
    Main Tables:
    - mavericks: Trainee profiles with skills and status
    - batches: Training batches with schedules
    - users: All platform users (trainers, HR, admins)
    - maverick_skills: Detailed skill proficiency tracking
    - deployments: Deployment records
    - assessments: Assessment configurations
    - assessment_attempts: Assessment results
    - pipelines: Training programs
    - pipeline_jobs: Training stages
    """

