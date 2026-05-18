"""
Enhanced seed script specifically for HR Dashboard testing
Creates complete data including assessments, deployments, feedback, etc.
Run with: python scripts/seed_dashboard_data.py
"""
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import *
from app.services.auth import get_password_hash


def seed_dashboard_data():
    """Seed complete HR dashboard data"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding HR Dashboard Data...")
        print("=" * 60)
        
        # Check if data already exists
        existing_mavs = db.query(Maverick).count()
        if existing_mavs > 0:
            print(f"✓ Found {existing_mavs} existing mavericks")
            print("  Adding additional dashboard data...")
        else:
            print("  Running base seed first...")
            # Import and run base seed
            from seed_data import seed_database
            seed_database()
            db = SessionLocal()  # Reconnect
        
        # Get existing entities
        batch = db.query(Batch).first()
        trainer = db.query(User).filter(User.role == UserRole.TRAINER).first()
        hr = db.query(User).filter(User.role == UserRole.HR).first()
        manager = db.query(User).filter(User.role == UserRole.MANAGER).first()
        mavericks = db.query(Maverick).all()
        pipeline = db.query(Pipeline).first()
        
        if not all([batch, trainer, mavericks, pipeline]):
            print("❌ Base data not found. Run seed_data.py first!")
            return
        
        # Get pipeline jobs for assessments
        jobs = db.query(PipelineJob).filter(PipelineJob.pipeline_id == pipeline.id).all()
        assessment_jobs = [j for j in jobs if j.job_type == JobType.ASSESSMENT]
        
        # 1. CREATE ASSESSMENTS AND ATTEMPTS
        print("\n📝 Creating assessments and attempts...")

        # First, create Assessment records for each assessment job
        assessments_created = {}
        for assessment_job in assessment_jobs:
            assessment = Assessment(
                job_id=assessment_job.id,
                batch_id=batch.id,
                title=f"{assessment_job.name} - Assessment",
                description=f"Assessment for {assessment_job.name}",
                max_marks=100,
                passing_marks=40,
                duration_minutes=60,
                scheduled_date=datetime.utcnow() - timedelta(days=7),
                created_by=trainer.id
            )
            db.add(assessment)
            db.flush()  # Get the ID
            assessments_created[assessment_job.id] = assessment

        print(f"   ✓ Created {len(assessments_created)} assessments")

        # Now create attempts
        attempts_created = 0

        for i, maverick in enumerate(mavericks[:4]):  # First 4 mavericks
            for assessment_job in assessment_jobs:
                assessment = assessments_created[assessment_job.id]

                # Create progress first
                progress = MaverickJobProgress(
                    maverick_id=maverick.id,
                    batch_id=batch.id,
                    job_id=assessment_job.id,
                    status=JobProgressStatus.COMPLETED,
                    started_at=datetime.utcnow() - timedelta(days=10),
                    completed_at=datetime.utcnow() - timedelta(days=5)
                )
                db.add(progress)

                # Create assessment attempt
                passed = i < 3  # First 3 pass, last one fails
                marks = 75 if passed else 45

                attempt = AssessmentAttempt(
                    assessment_id=assessment.id,
                    maverick_id=maverick.id,
                    batch_id=batch.id,
                    marks_obtained=marks,
                    max_marks=100,
                    passed=passed,
                    feedback="Good work!" if passed else "Needs improvement",
                    evaluated_by=trainer.id,
                    evaluated_at=datetime.utcnow() - timedelta(days=3)
                )
                db.add(attempt)
                attempts_created += 1

        db.flush()
        print(f"   ✓ Created {attempts_created} assessment attempts")
        print(f"   Success Rate: {(3*len(assessment_jobs))}/{attempts_created} = {(3*len(assessment_jobs)/attempts_created*100):.1f}%")
        
        # 2. CREATE DEPLOYMENT REQUESTS
        print("\n🚀 Creating deployment requests...")
        
        request1 = DeploymentRequest(
            maverick_id=mavericks[0].id,
            requested_by=manager.id,
            project_name="E-Commerce Platform",
            vertical="Retail",
            competency="Full Stack Development",
            justification="Urgent client requirement",
            status=DeploymentRequestStatus.PENDING
        )
        db.add(request1)
        
        request2 = DeploymentRequest(
            maverick_id=mavericks[1].id,
            requested_by=manager.id,
            project_name="Banking Portal",
            vertical="Finance",
            competency="Frontend Development",
            justification="New project starting",
            status=DeploymentRequestStatus.APPROVED,
            approved_by=hr.id,
            approved_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(request2)
        
        db.flush()
        print(f"   ✓ Created 2 deployment requests (1 pending, 1 approved)")
        
        # 3. MARK SOME MAVERICKS AS DEPLOYED
        print("\n✈️  Updating deployment status...")
        
        mavericks[1].deployment_status = DeploymentStatus.DEPLOYED
        print(f"   ✓ Marked 1 maverick as DEPLOYED")
        
        # 4. CREATE TRAINER FEEDBACK
        print("\n⭐ Creating trainer feedback...")
        
        feedback1 = TrainerFeedback(
            maverick_id=mavericks[0].id,
            trainer_id=trainer.id,
            batch_id=batch.id,
            rating=FeedbackRating.EXCELLENT,
            subject_knowledge=5,
            communication_skills=5,
            session_quality=5,
            doubt_resolution=4,
            positive_feedback="Excellent teaching style! Very clear explanations.",
            areas_for_improvement="Could add more hands-on examples",
            additional_comments="Overall great experience"
        )
        db.add(feedback1)

        feedback2 = TrainerFeedback(
            maverick_id=mavericks[1].id,
            trainer_id=trainer.id,
            batch_id=batch.id,
            rating=FeedbackRating.GOOD,
            subject_knowledge=4,
            communication_skills=4,
            session_quality=4,
            doubt_resolution=5,
            positive_feedback="Good at explaining concepts and answering questions",
            areas_for_improvement="More real-world examples would help",
            additional_comments="Very supportive trainer"
        )
        db.add(feedback2)
        
        db.flush()
        print(f"   ✓ Created 2 trainer feedbacks")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ HR Dashboard Data Seeded Successfully!")
        print("=" * 60)
        print("\n📊 Final Summary:")
        print(f"   • Mavericks: {len(mavericks)}")
        print(f"   • Pending Profiles: {sum(1 for m in mavericks if m.profile_status == ProfileStatus.PENDING)}")
        print(f"   • Approved: {sum(1 for m in mavericks if m.profile_status == ProfileStatus.APPROVED)}")
        print(f"   • Unassigned (no batch): {sum(1 for m in mavericks if m.profile_status == ProfileStatus.APPROVED and not m.current_batch_id)}")
        print(f"   • In Training: {sum(1 for m in mavericks if m.current_batch_id and m.deployment_status != DeploymentStatus.DEPLOYED)}")
        print(f"   • Deployed: {sum(1 for m in mavericks if m.deployment_status == DeploymentStatus.DEPLOYED)}")
        print(f"   • Assessment Attempts: {attempts_created}")
        print(f"   • Deployment Requests: 2 (1 pending)")
        print(f"   • Trainer Feedbacks: 2")
        print(f"   • Active Batches: 1")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_dashboard_data()
