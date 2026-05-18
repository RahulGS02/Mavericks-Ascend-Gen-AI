"""
Complete Test Data Creation Script - CLEAN VERSION
Creates 10 mavericks, 2 trainers, batch, pipeline, assessments, and progress
Includes logging and cleanup of existing data
"""
import sys
import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.maverick import Maverick, ProfileStatus, DeploymentStatus
from app.models.pipeline import Pipeline, PipelineJob, JobType, JobStatus
from app.models.batch import Batch, BatchStatus
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.training import TrainingSession, SessionStatus
from app.services.auth import get_password_hash
import uuid


def setup_logging():
    """Setup logging with file and console handlers"""
    # Create test_logs directory
    log_dir = Path(__file__).parent / "test_logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_data_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"📁 Log file: {log_file}")
    return logger, log_file


def save_created_ids(created_data, logger):
    """Save IDs of created data to a tracking file"""
    log_dir = Path(__file__).parent / "test_logs"
    tracking_file = log_dir / "last_run_data.json"

    import json
    with open(tracking_file, 'w') as f:
        json.dump(created_data, f, indent=2, default=str)

    logger.info(f"📝 Saved tracking data to: {tracking_file}")


def delete_previous_run_data(db, logger):
    """Delete ONLY data created by the previous script run using tracking file"""
    logger.info("\n🗑️  Checking for previous script run data...")

    log_dir = Path(__file__).parent / "test_logs"
    tracking_file = log_dir / "last_run_data.json"

    if not tracking_file.exists():
        logger.info("   ℹ️  No previous run data found. This is the first run or tracking file was deleted.")
        return {"users": 0, "mavericks": 0, "batches": 0, "pipelines": 0}

    deleted = {"users": 0, "mavericks": 0, "batches": 0, "pipelines": 0}

    try:
        import json
        with open(tracking_file, 'r') as f:
            previous_data = json.load(f)

        logger.info(f"   📋 Found previous run data from tracking file")

        # Delete in reverse order to respect foreign key constraints

        # 1. Delete progress records
        if "progress_ids" in previous_data:
            for prog_id in previous_data["progress_ids"]:
                prog = db.query(MaverickJobProgress).filter(MaverickJobProgress.id == prog_id).first()
                if prog:
                    db.delete(prog)

        # 2. Delete assessment attempts
        if "assessment_attempt_ids" in previous_data:
            for att_id in previous_data["assessment_attempt_ids"]:
                att = db.query(AssessmentAttempt).filter(AssessmentAttempt.id == att_id).first()
                if att:
                    db.delete(att)

        # 3. Delete training sessions
        if "session_ids" in previous_data:
            for sess_id in previous_data["session_ids"]:
                sess = db.query(TrainingSession).filter(TrainingSession.id == sess_id).first()
                if sess:
                    db.delete(sess)

        # 4. Delete assessments
        if "assessment_ids" in previous_data:
            for assess_id in previous_data["assessment_ids"]:
                assess = db.query(Assessment).filter(Assessment.id == assess_id).first()
                if assess:
                    db.delete(assess)

        # 5. Delete maverick profiles
        if "maverick_ids" in previous_data:
            for mav_id in previous_data["maverick_ids"]:
                mav = db.query(Maverick).filter(Maverick.id == mav_id).first()
                if mav:
                    db.delete(mav)
                    deleted["mavericks"] += 1

        # 6. Delete users
        if "user_ids" in previous_data:
            for user_id in previous_data["user_ids"]:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    db.delete(user)
                    deleted["users"] += 1

        # 7. Delete batch
        if "batch_id" in previous_data and previous_data["batch_id"]:
            batch = db.query(Batch).filter(Batch.id == previous_data["batch_id"]).first()
            if batch:
                db.delete(batch)
                deleted["batches"] += 1

        # 8. Delete pipeline jobs
        if "job_ids" in previous_data:
            for job_id in previous_data["job_ids"]:
                job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
                if job:
                    db.delete(job)

        # 9. Delete pipeline
        if "pipeline_id" in previous_data and previous_data["pipeline_id"]:
            pipeline = db.query(Pipeline).filter(Pipeline.id == previous_data["pipeline_id"]).first()
            if pipeline:
                db.delete(pipeline)
                deleted["pipelines"] += 1

        db.commit()
        logger.info(f"   ✅ Deleted previous run data: {deleted['users']} users, {deleted['mavericks']} mavericks, {deleted['batches']} batches, {deleted['pipelines']} pipelines")

        # Remove tracking file after successful deletion
        tracking_file.unlink()
        logger.info(f"   🗑️  Removed tracking file")

    except Exception as e:
        logger.error(f"   ⚠️  Error deleting previous run data: {str(e)}")
        logger.info(f"   ℹ️  Continuing with script execution...")
        db.rollback()

    return deleted


def main():
    logger, log_file = setup_logging()
    db = SessionLocal()
    credentials = {"mavericks": [], "trainers": [], "hr": {"email": "hr@maverick.com", "password": "hr123"}}

    # Track all created IDs for next run cleanup
    created_data = {
        "user_ids": [],
        "maverick_ids": [],
        "pipeline_id": None,
        "job_ids": [],
        "batch_id": None,
        "session_ids": [],
        "assessment_ids": [],
        "assessment_attempt_ids": [],
        "progress_ids": []
    }

    try:
        logger.info("\n" + "="*70)
        logger.info("🚀 MAVERICK ASCEND - TEST DATA CREATION")
        logger.info("="*70)

        # Step 0: Delete ONLY previous script run data
        delete_previous_run_data(db, logger)
        
        # Step 1: Get/Create HR user
        logger.info("\n1️⃣  Getting HR user...")
        hr_user = db.query(User).filter(User.email == "hr@maverick.com").first()
        if not hr_user:
            hr_user = User(
                email="hr@maverick.com", name="HR Manager",
                password_hash=get_password_hash("hr123"),
                role=UserRole.HR, is_active=True
            )
            db.add(hr_user)
            db.flush()
        logger.info(f"   ✓ HR: {hr_user.email}")
        
        # Step 2: Create 10 Mavericks
        logger.info("\n2️⃣  Creating 10 Mavericks...")
        maverick_data = [
            {"name": "Rahul Kumar", "cgpa": 8.5, "college": "IIT Delhi"},
            {"name": "Priya Sharma", "cgpa": 9.2, "college": "BITS Pilani"},
            {"name": "Amit Patel", "cgpa": 7.8, "college": "NIT Trichy"},
            {"name": "Sneha Reddy", "cgpa": 8.9, "college": "VIT Vellore"},
            {"name": "Rohan Gupta", "cgpa": 7.5, "college": "SRM Chennai"},
            {"name": "Anjali Singh", "cgpa": 9.0, "college": "IIIT Hyderabad"},
            {"name": "Vikram Mehta", "cgpa": 8.2, "college": "DTU Delhi"},
            {"name": "Pooja Iyer", "cgpa": 8.7, "college": "Anna University"},
            {"name": "Karthik Rao", "cgpa": 7.9, "college": "PEC Chandigarh"},
            {"name": "Divya Nair", "cgpa": 9.1, "college": "MNIT Jaipur"}
        ]
        
        mavericks = []
        for i, data in enumerate(maverick_data, 1):
            email = f"maverick{i}@test.com"
            user = User(email=email, name=data["name"], password_hash=get_password_hash("mav123"),
                       role=UserRole.MAVERICK, is_active=True)
            db.add(user)
            db.flush()
            created_data["user_ids"].append(str(user.id))  # Track user ID

            maverick = Maverick(
                user_id=user.id, name=data["name"], email=email,
                phone=f"98765432{i:02d}", college=data["college"],
                degree="B.Tech", branch="Computer Science", graduation_year=2024,
                cgpa=data["cgpa"], skills=["Python", "SQL", "JavaScript", "React"],
                profile_status=ProfileStatus.APPROVED,
                deployment_status=DeploymentStatus.AVAILABLE
            )
            db.add(maverick)
            db.flush()
            mavericks.append(maverick)
            created_data["maverick_ids"].append(str(maverick.id))  # Track maverick ID
            credentials["mavericks"].append({"name": data["name"], "email": email, "password": "mav123"})
            logger.info(f"   ✓ {data['name']}")

        db.commit()
        logger.info(f"   ✅ Created {len(mavericks)} mavericks")

        # Step 3: Create 2 Trainers
        logger.info("\n3️⃣  Creating 2 Trainers...")
        trainer_data = [
            {"name": "Sarah Johnson", "email": "sarah.trainer@maverick.com"},
            {"name": "David Lee", "email": "david.trainer@maverick.com"}
        ]

        trainers = []
        for data in trainer_data:
            user = User(email=data["email"], name=data["name"],
                       password_hash=get_password_hash("trainer123"),
                       role=UserRole.TRAINER, is_active=True)
            db.add(user)
            db.flush()
            trainers.append(user)
            created_data["user_ids"].append(str(user.id))  # Track trainer user ID
            credentials["trainers"].append({"name": data["name"], "email": data["email"], "password": "trainer123"})
            logger.info(f"   ✓ {data['name']}")

        db.commit()

        # Step 4: Create Pipeline
        logger.info("\n4️⃣  Creating Pipeline: SQL Advanced...")
        pipeline = Pipeline(
            name="SQL Advanced Training",
            description="Complete SQL training from basics to advanced",
            created_by=hr_user.id, is_template=False
        )
        db.add(pipeline)
        db.flush()
        created_data["pipeline_id"] = str(pipeline.id)  # Track pipeline ID
        logger.info(f"   ✓ {pipeline.name}")

        # Step 5: Create Jobs
        logger.info("\n5️⃣  Creating Pipeline Jobs...")
        jobs_data = [
            {"name": "SQL Basics Training", "type": JobType.TRAINING, "order": 1, "duration": 5},
            {"name": "SQL Basics Assessment", "type": JobType.ASSESSMENT, "order": 2, "duration": 1},
            {"name": "SQL Advanced Training", "type": JobType.TRAINING, "order": 3, "duration": 7},
            {"name": "SQL Advanced Assessment", "type": JobType.ASSESSMENT, "order": 4, "duration": 1},
            {"name": "Deployment", "type": JobType.DEPLOYMENT, "order": 5, "duration": 1}
        ]

        pipeline_jobs = []
        for jd in jobs_data:
            job = PipelineJob(
                pipeline_id=pipeline.id, name=jd["name"], job_type=jd["type"],
                sequence_order=jd["order"], is_mandatory=True, duration_days=jd["duration"],
                description=f"{jd['name']} - Part of SQL Advanced Training",
                status=JobStatus.PENDING
            )
            db.add(job)
            db.flush()
            pipeline_jobs.append(job)
            created_data["job_ids"].append(str(job.id))  # Track job ID
            logger.info(f"   ✓ Job {jd['order']}: {jd['name']}")

        db.commit()

        # Step 6: Create Batch
        logger.info("\n6️⃣  Creating Batch...")
        batch = Batch(
            name="SQL Advanced Batch - Q2 2026",
            pipeline_id=pipeline.id, trainer_id=trainers[0].id, created_by=hr_user.id,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=30),
            status=BatchStatus.ACTIVE, max_capacity=15, current_enrollment=10
        )
        db.add(batch)
        db.flush()
        created_data["batch_id"] = str(batch.id)  # Track batch ID
        logger.info(f"   ✓ Batch: {batch.name}")
        logger.info(f"   ✓ Trainer: {trainers[0].name}")

        # Step 7: Assign Mavericks to Batch
        logger.info("\n7️⃣  Assigning Mavericks to Batch...")
        for mav in mavericks:
            mav.current_batch_id = batch.id
        db.commit()
        logger.info(f"   ✅ Assigned {len(mavericks)} mavericks to batch")

        # Step 8: Create Training Sessions
        logger.info("\n8️⃣  Creating Training Sessions...")
        sessions = [
            TrainingSession(
                batch_id=batch.id, job_id=pipeline_jobs[0].id, trainer_id=trainers[0].id,
                title="SQL Basics Training Session",
                description="Introduction to SQL fundamentals",
                scheduled_date=datetime.now() - timedelta(days=25),
                duration_minutes=300, location="Training Room A",
                status=SessionStatus.COMPLETED
            ),
            TrainingSession(
                batch_id=batch.id, job_id=pipeline_jobs[2].id, trainer_id=trainers[0].id,
                title="SQL Advanced Training Session",
                description="Advanced SQL concepts and optimization",
                scheduled_date=datetime.now() - timedelta(days=10),
                duration_minutes=420, location="Training Room A",
                status=SessionStatus.COMPLETED
            ),
            TrainingSession(
                batch_id=batch.id, job_id=pipeline_jobs[2].id, trainer_id=trainers[1].id,
                title="SQL Advanced Training - Part 2",
                description="Advanced queries and performance tuning",
                scheduled_date=datetime.now() + timedelta(days=7),
                duration_minutes=240,
                meeting_link="https://meet.google.com/test-session",
                status=SessionStatus.SCHEDULED
            )
        ]
        for s in sessions:
            db.add(s)
        db.flush()
        for s in sessions:
            created_data["session_ids"].append(str(s.id))  # Track session IDs
        logger.info(f"   ✅ Created {len(sessions)} training sessions")

        # Step 9: Create Assessments
        logger.info("\n9️⃣  Creating Assessments...")
        assessment1 = Assessment(
            batch_id=batch.id, job_id=pipeline_jobs[1].id,
            title="SQL Basics Assessment", description="Test on SQL fundamentals",
            max_marks=100, passing_marks=60, duration_minutes=60,
            scheduled_date=datetime.now() - timedelta(days=20),
            created_by=trainers[0].id
        )
        assessment2 = Assessment(
            batch_id=batch.id, job_id=pipeline_jobs[3].id,
            title="SQL Advanced Assessment", description="Test on advanced SQL concepts",
            max_marks=100, passing_marks=70, duration_minutes=90,
            scheduled_date=datetime.now() - timedelta(days=5),
            created_by=trainers[0].id
        )
        db.add(assessment1)
        db.add(assessment2)
        db.flush()
        created_data["assessment_ids"].append(str(assessment1.id))  # Track assessment IDs
        created_data["assessment_ids"].append(str(assessment2.id))
        logger.info(f"   ✅ Created 2 assessments")

        # Step 10: Create Progress & Marks (Edge Cases)
        logger.info("\n🔟  Creating Progress and Assessment Marks...")

        # Different scenarios for each maverick
        scenarios = [
            # Maverick 1: Top performer
            {"name": mavericks[0].name, "basic": 95, "advanced": 92, "progress": [100, 100, 100, 100, 90]},
            # Maverick 2: Second best
            {"name": mavericks[1].name, "basic": 90, "advanced": 88, "progress": [100, 100, 95, 95, 80]},
            # Maverick 3: Good student
            {"name": mavericks[2].name, "basic": 85, "advanced": 75, "progress": [100, 100, 90, 90, 70]},
            # Maverick 4: Average
            {"name": mavericks[3].name, "basic": 78, "advanced": 72, "progress": [100, 100, 85, 85, 60]},
            # Maverick 5: Borderline
            {"name": mavericks[4].name, "basic": 65, "advanced": 70, "progress": [100, 100, 80, 80, 50]},
            # Maverick 6: Failed advanced
            {"name": mavericks[5].name, "basic": 82, "advanced": 65, "progress": [100, 100, 75, 75, 0]},
            # Maverick 7: Failed both
            {"name": mavericks[6].name, "basic": 55, "advanced": 58, "progress": [100, 100, 60, 60, 0]},
            # Maverick 8: In progress - basic only
            {"name": mavericks[7].name, "basic": 88, "advanced": None, "progress": [100, 100, 50, 0, 0]},
            # Maverick 9: Just started
            {"name": mavericks[8].name, "basic": None, "advanced": None, "progress": [100, 0, 0, 0, 0]},
            # Maverick 10: Top performer - ready for deployment
            {"name": mavericks[9].name, "basic": 98, "advanced": 95, "progress": [100, 100, 100, 100, 100]},
        ]

        for idx, scenario in enumerate(scenarios):
            mav = mavericks[idx]

            # Create progress for all jobs
            for job_idx, job in enumerate(pipeline_jobs):
                prog_pct = scenario["progress"][job_idx]
                progress = MaverickJobProgress(
                    maverick_id=mav.id, job_id=job.id, batch_id=batch.id,
                    completion_percentage=Decimal(str(prog_pct)),
                    status=ProgressStatus.COMPLETED if prog_pct == 100 else
                          (ProgressStatus.IN_PROGRESS if prog_pct > 0 else ProgressStatus.PENDING),
                    started_at=datetime.now() - timedelta(days=25) if prog_pct > 0 else None,
                    completed_at=datetime.now() - timedelta(days=20-job_idx*5) if prog_pct == 100 else None
                )
                db.add(progress)
                db.flush()
                created_data["progress_ids"].append(str(progress.id))  # Track progress ID

            # SQL Basics Assessment
            if scenario["basic"] is not None:
                basic_passed = scenario["basic"] >= 60
                attempt1 = AssessmentAttempt(
                    assessment_id=assessment1.id, maverick_id=mav.id, batch_id=batch.id,
                    marks_obtained=Decimal(str(scenario["basic"])), max_marks=Decimal('100'),
                    passed=basic_passed,
                    evaluated_at=datetime.now() - timedelta(days=19),
                    evaluated_by=trainers[0].id
                )
                db.add(attempt1)
                db.flush()
                created_data["assessment_attempt_ids"].append(str(attempt1.id))  # Track attempt ID

            # SQL Advanced Assessment
            if scenario["advanced"] is not None:
                advanced_passed = scenario["advanced"] >= 70
                attempt2 = AssessmentAttempt(
                    assessment_id=assessment2.id, maverick_id=mav.id, batch_id=batch.id,
                    marks_obtained=Decimal(str(scenario["advanced"])), max_marks=Decimal('100'),
                    passed=advanced_passed,
                    evaluated_at=datetime.now() - timedelta(days=4),
                    evaluated_by=trainers[0].id
                )
                db.add(attempt2)
                db.flush()
                created_data["assessment_attempt_ids"].append(str(attempt2.id))  # Track attempt ID

            # Update deployment status
            if scenario["progress"][4] == 100:
                mav.deployment_status = DeploymentStatus.DEPLOYED

            logger.info(f"   ✓ {scenario['name']}: Basic={scenario['basic']}, Advanced={scenario['advanced']}, Progress={scenario['progress'][4]}%")

        db.commit()

        # Final Summary
        logger.info("\n" + "="*70)
        logger.info("✅ TEST DATA CREATION COMPLETE!")
        logger.info("="*70)
        logger.info(f"\n📊 Summary:")
        logger.info(f"   • 10 Mavericks (all APPROVED)")
        logger.info(f"   • 2 Trainers")
        logger.info(f"   • 1 Pipeline: {pipeline.name}")
        logger.info(f"   • 5 Jobs in pipeline")
        logger.info(f"   • 1 Batch: {batch.name}")
        logger.info(f"   • 3 Training Sessions")
        logger.info(f"   • 2 Assessments")
        logger.info(f"   • Progress and marks for all mavericks")

        logger.info("\n🎯 Edge Cases Covered:")
        logger.info("   • Top performers (ready for deployment)")
        logger.info("   • Average performers (all pass)")
        logger.info("   • Borderline pass (just met criteria)")
        logger.info("   • Failed assessments (need retry)")
        logger.info("   • In-progress students")
        logger.info("   • Just started students")

        logger.info("\n" + "="*70)
        logger.info("🔑 LOGIN CREDENTIALS")
        logger.info("="*70)

        logger.info("\n👔 HR Account:")
        logger.info(f"   Email:    {credentials['hr']['email']}")
        logger.info(f"   Password: {credentials['hr']['password']}")

        logger.info("\n👨‍🏫 Trainers:")
        for t in credentials['trainers']:
            logger.info(f"\n   {t['name']}")
            logger.info(f"   Email:    {t['email']}")
            logger.info(f"   Password: {t['password']}")

        logger.info("\n🎓 Mavericks:")
        for i, m in enumerate(credentials['mavericks'], 1):
            status = ""
            if i == 1 or i == 10:
                status = " (TOP - DEPLOYED)"
            elif i == 6 or i == 7:
                status = " (FAILED)"
            elif i == 8:
                status = " (IN PROGRESS)"
            elif i == 9:
                status = " (JUST STARTED)"
            logger.info(f"\n   {i}. {m['name']}{status}")
            logger.info(f"      Email:    {m['email']}")
            logger.info(f"      Password: {m['password']}")

        logger.info("\n" + "="*70)
        logger.info("🚀 NEXT STEPS")
        logger.info("="*70)
        logger.info("""
1. Start backend: cd apps/api && uvicorn app.main:app --reload
2. Start frontend: cd apps/web && npm run dev
3. Login with any maverick credentials
4. Test 'My Batch' leaderboard feature
5. Verify rankings and edge cases
        """)

        logger.info("="*70)
        logger.info(f"✅ All test data created successfully!")
        logger.info(f"📁 Full log saved to: {log_file}")
        logger.info("="*70)

        # Save tracking data for next run
        save_created_ids(created_data, logger)

    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

