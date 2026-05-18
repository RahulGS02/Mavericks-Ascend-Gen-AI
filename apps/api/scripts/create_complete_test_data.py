"""
Complete Test Data Creation Script
Creates 10 mavericks, trainers, batch, pipeline, assessments, and progress
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
    # Create test_data_logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "test_data_logs"
    log_dir.mkdir(exist_ok=True)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_data_creation_{timestamp}.log"

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
    logger.info(f"Log file created: {log_file}")
    return logger, log_file


def delete_existing_test_data(db, logger):
    """Delete existing test users and related data"""
    logger.info("Checking for existing test data...")

    # Get all test maverick users
    test_emails = [f"maverick{i}@test.com" for i in range(1, 11)]
    test_emails.extend(["sarah.trainer@maverick.com", "david.trainer@maverick.com"])

    deleted_counts = {
        "users": 0,
        "mavericks": 0,
        "batches": 0,
        "pipelines": 0
    }

    # Delete test users
    for email in test_emails:
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Delete related maverick profile
            maverick = db.query(Maverick).filter(Maverick.user_id == user.id).first()
            if maverick:
                # Delete progress records
                db.query(MaverickJobProgress).filter(MaverickJobProgress.maverick_id == maverick.id).delete()
                # Delete assessment attempts
                db.query(AssessmentAttempt).filter(AssessmentAttempt.maverick_id == maverick.id).delete()
                db.delete(maverick)
                deleted_counts["mavericks"] += 1

            db.delete(user)
            deleted_counts["users"] += 1
            logger.info(f"  Deleted user: {email}")

    # Delete test batches
    test_batch = db.query(Batch).filter(Batch.name == "SQL Advanced Batch - Q2 2026").first()
    if test_batch:
        # Delete related assessments
        db.query(Assessment).filter(Assessment.batch_id == test_batch.id).delete()
        # Delete training sessions
        db.query(TrainingSession).filter(TrainingSession.batch_id == test_batch.id).delete()
        db.delete(test_batch)
        deleted_counts["batches"] += 1
        logger.info(f"  Deleted batch: {test_batch.name}")

    # Delete test pipeline
    test_pipeline = db.query(Pipeline).filter(Pipeline.name == "SQL Advanced Training").first()
    if test_pipeline:
        # Delete pipeline jobs
        db.query(PipelineJob).filter(PipelineJob.pipeline_id == test_pipeline.id).delete()
        db.delete(test_pipeline)
        deleted_counts["pipelines"] += 1
        logger.info(f"  Deleted pipeline: {test_pipeline.name}")

    db.commit()

    logger.info(f"✅ Cleanup complete: {deleted_counts['users']} users, {deleted_counts['mavericks']} mavericks, {deleted_counts['batches']} batches, {deleted_counts['pipelines']} pipelines")
    return deleted_counts


def main():
    # Setup logging
    logger, log_file = setup_logging()

    db = SessionLocal()

    try:
        logger.info("="*70)
        logger.info("CREATING COMPLETE TEST DATA")
        logger.info("="*70)

        # Delete existing test data first
        logger.info("\n🗑️  STEP 0: Cleaning up existing test data...")
        delete_existing_test_data(db, logger)
        
        # Store credentials for output
        credentials = {
            "mavericks": [],
            "trainers": [],
            "hr": {"email": "hr@maverick.com", "password": "hr123"}
        }
        
        # Step 1: Get HR user (should exist from seed data)
        logger.info("\n1️⃣  Getting HR user...")
        hr_user = db.query(User).filter(User.email == "hr@maverick.com").first()
        if not hr_user:
            logger.info("   Creating HR user...")
            hr_user = User(
                email="hr@maverick.com",
                name="HR Manager",
                password_hash=get_password_hash("hr123"),
                role=UserRole.HR,
                is_active=True
            )
            db.add(hr_user)
            db.flush()
        logger.info(f"   ✓ HR User: {hr_user.email}")
        
        # Step 2: Create or Get 10 Mavericks
        print("\n2️⃣  Creating 10 Mavericks...")

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
            password = "mav123"

            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"   ⚠️  User exists: {email}, getting existing maverick...")
                existing_maverick = db.query(Maverick).filter(Maverick.user_id == existing_user.id).first()
                if existing_maverick:
                    mavericks.append(existing_maverick)
                    credentials["mavericks"].append({
                        "name": data["name"],
                        "email": email,
                        "password": password
                    })
                    continue

            # Create User
            user = User(
                email=email,
                name=data["name"],
                password_hash=get_password_hash(password),
                role=UserRole.MAVERICK,
                is_active=True
            )
            db.add(user)
            db.flush()

            # Create Maverick Profile
            maverick = Maverick(
                user_id=user.id,
                name=data["name"],
                email=email,
                phone=f"98765432{i:02d}",
                college=data["college"],
                degree="B.Tech",
                branch="Computer Science",
                graduation_year=2024,
                cgpa=data["cgpa"],
                skills=["Python", "SQL", "JavaScript", "React", "Node.js"],
                profile_status=ProfileStatus.APPROVED,  # Pre-approved
                deployment_status=DeploymentStatus.AVAILABLE
            )
            db.add(maverick)
            db.flush()
            mavericks.append(maverick)

            credentials["mavericks"].append({
                "name": data["name"],
                "email": email,
                "password": password
            })

            print(f"   ✓ Created: {data['name']} ({email})")
        
        db.commit()
        print(f"\n   ✓ Created {len(mavericks)} mavericks (all APPROVED)")
        
        # Step 3: Create or Get 2 Trainers
        print("\n3️⃣  Creating 2 Trainers...")

        trainer_data = [
            {"name": "Sarah Johnson", "email": "sarah.trainer@maverick.com"},
            {"name": "David Lee", "email": "david.trainer@maverick.com"}
        ]

        trainers = []
        for data in trainer_data:
            password = "trainer123"

            # Check if trainer already exists
            existing_trainer = db.query(User).filter(User.email == data["email"]).first()
            if existing_trainer:
                print(f"   ⚠️  Trainer exists: {data['email']}, using existing")
                trainers.append(existing_trainer)
                credentials["trainers"].append({
                    "name": data["name"],
                    "email": data["email"],
                    "password": password
                })
                continue

            trainer_user = User(
                email=data["email"],
                name=data["name"],
                password_hash=get_password_hash(password),
                role=UserRole.TRAINER,
                is_active=True
            )
            db.add(trainer_user)
            db.flush()
            trainers.append(trainer_user)

            credentials["trainers"].append({
                "name": data["name"],
                "email": data["email"],
                "password": password
            })

            print(f"   ✓ Created: {data['name']} ({data['email']})")

        db.commit()
        
        # Step 4: Create Pipeline "SQL Advanced"
        print("\n4️⃣  Creating Pipeline: SQL Advanced...")
        
        pipeline = Pipeline(
            name="SQL Advanced Training",
            description="Complete SQL training from basics to advanced",
            created_by=hr_user.id,
            is_template=False
        )
        db.add(pipeline)
        db.flush()
        print(f"   ✓ Pipeline created: {pipeline.name}")
        
        # Step 5: Create Pipeline Jobs
        print("\n5️⃣  Creating Pipeline Jobs...")
        
        jobs_data = [
            {"name": "SQL Basics Training", "type": JobType.TRAINING, "order": 1, "duration": 5},
            {"name": "SQL Basics Assessment", "type": JobType.ASSESSMENT, "order": 2, "duration": 1},
            {"name": "SQL Advanced Training", "type": JobType.TRAINING, "order": 3, "duration": 7},
            {"name": "SQL Advanced Assessment", "type": JobType.ASSESSMENT, "order": 4, "duration": 1},
            {"name": "Deployment", "type": JobType.DEPLOYMENT, "order": 5, "duration": 1}
        ]
        
        pipeline_jobs = []
        for job_data in jobs_data:
            job = PipelineJob(
                pipeline_id=pipeline.id,
                name=job_data["name"],
                job_type=job_data["type"],
                sequence_order=job_data["order"],
                is_mandatory=True,
                duration_days=job_data["duration"],
                description=f"{job_data['name']} - Part of SQL Advanced Training",
                status=JobStatus.PENDING
            )
            db.add(job)
            db.flush()
            pipeline_jobs.append(job)
            print(f"   ✓ Job {job_data['order']}: {job_data['name']}")
        
        db.commit()

        # Step 6: Create Batch
        print("\n6️⃣  Creating Batch...")

        batch = Batch(
            name="SQL Advanced Batch - Q2 2026",
            pipeline_id=pipeline.id,
            trainer_id=trainers[0].id,  # Sarah Johnson
            created_by=hr_user.id,
            start_date=datetime.now() - timedelta(days=30),  # Started 30 days ago
            end_date=datetime.now() + timedelta(days=30),  # Ends in 30 days
            status=BatchStatus.ACTIVE,
            max_capacity=15,
            current_enrollment=10
        )
        db.add(batch)
        db.flush()
        print(f"   ✓ Batch created: {batch.name}")
        print(f"   ✓ Trainer: {trainers[0].name}")

        # Step 7: Assign all mavericks to batch
        print("\n7️⃣  Assigning Mavericks to Batch...")

        for maverick in mavericks:
            maverick.current_batch_id = batch.id
            print(f"   ✓ Assigned: {maverick.name}")

        db.commit()

        # Step 8: Create Training Sessions
        print("\n8️⃣  Creating Training Sessions...")

        # SQL Basics Training (Job 1) - Already completed
        session1 = TrainingSession(
            batch_id=batch.id,
            job_id=pipeline_jobs[0].id,  # SQL Basics Training
            trainer_id=trainers[0].id,
            scheduled_date=datetime.now() - timedelta(days=25),
            duration_minutes=300,  # 5 hours
            location="Training Room A",
            mode="OFFLINE",
            status=SessionStatus.COMPLETED,
            attendance_required=True
        )
        db.add(session1)

        # SQL Advanced Training (Job 3) - Already completed
        session2 = TrainingSession(
            batch_id=batch.id,
            job_id=pipeline_jobs[2].id,  # SQL Advanced Training
            trainer_id=trainers[0].id,
            scheduled_date=datetime.now() - timedelta(days=10),
            duration_minutes=420,  # 7 hours
            location="Training Room A",
            mode="OFFLINE",
            status=SessionStatus.COMPLETED,
            attendance_required=True
        )
        db.add(session2)

        # Future session
        session3 = TrainingSession(
            batch_id=batch.id,
            job_id=pipeline_jobs[2].id,
            trainer_id=trainers[1].id,  # David Lee
            scheduled_date=datetime.now() + timedelta(days=7),
            duration_minutes=240,
            location="Online",
            mode="ONLINE",
            status=SessionStatus.SCHEDULED,
            attendance_required=False
        )
        db.add(session3)

        db.flush()
        print(f"   ✓ Created 3 training sessions")

        # Step 9: Create Assessments
        print("\n9️⃣  Creating Assessments...")

        # SQL Basics Assessment (Job 2)
        assessment1 = Assessment(
            batch_id=batch.id,
            job_id=pipeline_jobs[1].id,
            title="SQL Basics Assessment",
            description="Test on SQL fundamentals",
            max_marks=100,
            passing_marks=60,
            duration_minutes=60,
            scheduled_date=datetime.now() - timedelta(days=20),
            created_by=trainers[0].id
        )
        db.add(assessment1)

        # SQL Advanced Assessment (Job 4)
        assessment2 = Assessment(
            batch_id=batch.id,
            job_id=pipeline_jobs[3].id,
            title="SQL Advanced Assessment",
            description="Test on advanced SQL concepts",
            max_marks=100,
            passing_marks=70,
            duration_minutes=90,
            scheduled_date=datetime.now() - timedelta(days=5),
            created_by=trainers[0].id
        )
        db.add(assessment2)

        db.flush()
        print(f"   ✓ Created 2 assessments")

        # Step 10: Create Progress Records and Assessment Attempts
        print("\n🔟  Creating Progress and Marks (Edge Cases)...")

        # Define different scenarios for each maverick
        scenarios = [
            # Maverick 1: Top performer - all pass, high scores
            {"name": mavericks[0].name, "basic_score": 95, "advanced_score": 92, "progress": [100, 100, 100, 100, 90]},
            # Maverick 2: Second best - all pass, good scores
            {"name": mavericks[1].name, "basic_score": 90, "advanced_score": 88, "progress": [100, 100, 95, 95, 80]},
            # Maverick 3: Good student - all pass
            {"name": mavericks[2].name, "basic_score": 85, "advanced_score": 75, "progress": [100, 100, 90, 90, 70]},
            # Maverick 4: Average - all pass, on edge
            {"name": mavericks[3].name, "basic_score": 78, "advanced_score": 72, "progress": [100, 100, 85, 85, 60]},
            # Maverick 5: Borderline - basic pass, advanced just pass
            {"name": mavericks[4].name, "basic_score": 65, "advanced_score": 70, "progress": [100, 100, 80, 80, 50]},
            # Maverick 6: Failed advanced - needs retry
            {"name": mavericks[5].name, "basic_score": 82, "advanced_score": 65, "progress": [100, 100, 75, 75, 0]},
            # Maverick 7: Failed both - struggling
            {"name": mavericks[6].name, "basic_score": 55, "advanced_score": 58, "progress": [100, 100, 60, 60, 0]},
            # Maverick 8: In progress - completed basic only
            {"name": mavericks[7].name, "basic_score": 88, "advanced_score": None, "progress": [100, 100, 50, 0, 0]},
            # Maverick 9: Just started - only training done
            {"name": mavericks[8].name, "basic_score": None, "advanced_score": None, "progress": [100, 0, 0, 0, 0]},
            # Maverick 10: Excellent performer - ready for deployment
            {"name": mavericks[9].name, "basic_score": 98, "advanced_score": 95, "progress": [100, 100, 100, 100, 100]},
        ]

        for idx, scenario in enumerate(scenarios):
            maverick = mavericks[idx]
            print(f"\n   Setting up: {scenario['name']}")

            # Create progress for all jobs
            for job_idx, job in enumerate(pipeline_jobs):
                progress = MaverickJobProgress(
                    maverick_id=maverick.id,
                    job_id=job.id,
                    batch_id=batch.id,
                    completion_percentage=Decimal(str(scenario["progress"][job_idx])),
                    status=ProgressStatus.COMPLETED if scenario["progress"][job_idx] == 100 else
                          (ProgressStatus.IN_PROGRESS if scenario["progress"][job_idx] > 0 else ProgressStatus.NOT_STARTED),
                    started_at=datetime.now() - timedelta(days=25) if scenario["progress"][job_idx] > 0 else None,
                    completed_at=datetime.now() - timedelta(days=20-job_idx*5) if scenario["progress"][job_idx] == 100 else None
                )
                db.add(progress)

            # Create assessment attempts
            # SQL Basics Assessment
            if scenario["basic_score"] is not None:
                basic_passed = scenario["basic_score"] >= 60
                attempt1 = AssessmentAttempt(
                    assessment_id=assessment1.id,
                    maverick_id=maverick.id,
                    batch_id=batch.id,
                    marks_obtained=Decimal(str(scenario["basic_score"])),
                    max_marks=Decimal('100'),
                    passed=basic_passed,
                    submitted_at=datetime.now() - timedelta(days=20),
                    evaluated_at=datetime.now() - timedelta(days=19),
                    evaluated_by=trainers[0].id
                )
                db.add(attempt1)
                print(f"      ✓ Basic Assessment: {scenario['basic_score']}/100 - {'PASS' if basic_passed else 'FAIL'}")

            # SQL Advanced Assessment
            if scenario["advanced_score"] is not None:
                advanced_passed = scenario["advanced_score"] >= 70
                attempt2 = AssessmentAttempt(
                    assessment_id=assessment2.id,
                    maverick_id=maverick.id,
                    batch_id=batch.id,
                    marks_obtained=Decimal(str(scenario["advanced_score"])),
                    max_marks=Decimal('100'),
                    passed=advanced_passed,
                    submitted_at=datetime.now() - timedelta(days=5),
                    evaluated_at=datetime.now() - timedelta(days=4),
                    evaluated_by=trainers[0].id
                )
                db.add(attempt2)
                print(f"      ✓ Advanced Assessment: {scenario['advanced_score']}/100 - {'PASS' if advanced_passed else 'FAIL'}")

            # Update deployment status
            if scenario["progress"][4] == 100:  # Deployment job completed
                maverick.deployment_status = DeploymentStatus.DEPLOYED
                print(f"      ✓ Status: READY FOR DEPLOYMENT")

        db.commit()

        # Final Summary
        print("\n" + "="*70)
        print("✅ TEST DATA CREATION COMPLETE!")
        print("="*70)

        print("\n📊 Summary:")
        print(f"   • Created 10 Mavericks (all APPROVED)")
        print(f"   • Created 2 Trainers")
        print(f"   • Created 1 Pipeline: {pipeline.name}")
        print(f"   • Created 5 Jobs in pipeline")
        print(f"   • Created 1 Batch: {batch.name}")
        print(f"   • Created 3 Training Sessions")
        print(f"   • Created 2 Assessments")
        print(f"   • Added progress and marks for all mavericks")

        print("\n🎯 Edge Cases Covered:")
        print("   • Top performers (ready for deployment)")
        print("   • Average performers (all pass)")
        print("   • Borderline pass (just met criteria)")
        print("   • Failed assessments (need retry)")
        print("   • In-progress students")
        print("   • Just started students")

        print("\n" + "="*70)
        print("🔑 LOGIN CREDENTIALS")
        print("="*70)

        print("\n👔 HR Account:")
        print(f"   Email:    {credentials['hr']['email']}")
        print(f"   Password: {credentials['hr']['password']}")

        print("\n👨‍🏫 Trainers:")
        for trainer in credentials['trainers']:
            print(f"\n   {trainer['name']}")
            print(f"   Email:    {trainer['email']}")
            print(f"   Password: {trainer['password']}")

        print("\n🎓 Mavericks:")
        for i, mav in enumerate(credentials['mavericks'], 1):
            status = ""
            if i == 1 or i == 10:
                status = " (TOP PERFORMER - Ready for Deployment)"
            elif i == 6 or i == 7:
                status = " (FAILED - Needs Retry)"
            elif i == 8:
                status = " (IN PROGRESS)"
            elif i == 9:
                status = " (JUST STARTED)"

            print(f"\n   {i}. {mav['name']}{status}")
            print(f"      Email:    {mav['email']}")
            print(f"      Password: {mav['password']}")

        print("\n" + "="*70)
        print("🚀 VERIFICATION STEPS")
        print("="*70)
        print("""
1. Test Leaderboard Rankings:
   • Login as any maverick
   • Go to 'My Batch' page
   • Verify rankings are correct
   • Rahul Kumar should be #1
   • Divya Nair should be #2

2. Test Assessment Scores:
   • Check 'My Assessments' page
   • Verify pass/fail status
   • Check different edge cases

3. Test Progress:
   • Check 'My Progress' page
   • Verify completion percentages
   • Check deployment readiness

4. Test as Trainer:
   • Login as trainer
   • View batch students
   • Check assessment results

5. Test as HR:
   • View all mavericks
   • Check deployment status
   • Verify batch assignments
        """)

        print("=" * 70)
        print("✅ All test data created successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
