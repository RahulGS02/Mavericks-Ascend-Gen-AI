"""
Seed the database with initial development data
Run with: python scripts/seed_data.py
"""
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import *
from app.services.auth import get_password_hash


def seed_database():
    """Seed database with sample data for development"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database with sample data...")
        
        # 1. Create Users
        print("\n👥 Creating users...")
        
        admin_user = User(
            email="admin@maverick.com",
            name="Super Admin",
            role=UserRole.SUPER_ADMIN,
            password_hash=get_password_hash("admin123"),
            is_active=True
        )
        db.add(admin_user)
        
        hr_user = User(
            email="hr@maverick.com",
            name="HR Manager",
            role=UserRole.HR,
            password_hash=get_password_hash("hr123"),
            is_active=True
        )
        db.add(hr_user)
        
        trainer_user = User(
            email="trainer@maverick.com",
            name="John Trainer",
            role=UserRole.TRAINER,
            password_hash=get_password_hash("trainer123"),
            is_active=True
        )
        db.add(trainer_user)
        
        manager_user = User(
            email="manager@maverick.com",
            name="Project Manager",
            role=UserRole.MANAGER,
            password_hash=get_password_hash("manager123"),
            is_active=True
        )
        db.add(manager_user)
        
        db.flush()  # Flush to get IDs
        print("   ✓ Created 4 users (admin, hr, trainer, manager)")
        
        # 2. Create Sample Mavericks
        print("\n🎓 Creating sample mavericks...")
        
        maverick_users = [
            User(
                email=f"maverick{i}@example.com",
                name=f"Maverick Student {i}",
                role=UserRole.MAVERICK,
                password_hash=get_password_hash("maverick123"),
                is_active=True
            )
            for i in range(1, 6)
        ]
        
        db.add_all(maverick_users)
        db.flush()
        
        mavericks = []
        for i, user in enumerate(maverick_users, 1):
            maverick = Maverick(
                user_id=user.id,
                college=f"University {i}",
                degree="B.Tech Computer Science",
                graduation_year=2024,
                phone=f"+91-98765{i:05d}",
                skills=["Python", "JavaScript", "SQL", "React"],
                profile_status=ProfileStatus.SHORTLISTED
            )
            mavericks.append(maverick)
            db.add(maverick)
        
        db.flush()
        print(f"   ✓ Created {len(mavericks)} mavericks")
        
        # 3. Create Sample Pipeline
        print("\n🔄 Creating sample pipeline...")

        pipeline = Pipeline(
            name="Full Stack Developer Training Pipeline",
            description="Complete training pipeline for full stack developers",
            created_by=hr_user.id,
            is_template=True
        )
        db.add(pipeline)
        db.flush()

        # Create pipeline jobs
        jobs = [
            PipelineJob(
                pipeline_id=pipeline.id,
                job_name="Python Fundamentals Training",
                job_type=JobType.TRAINING,
                sequence_order=1,
                is_mandatory=True,
                duration_days=14,
                description="Learn Python basics and advanced concepts"
            ),
            PipelineJob(
                pipeline_id=pipeline.id,
                job_name="Python Assessment",
                job_type=JobType.ASSESSMENT,
                sequence_order=2,
                is_mandatory=True,
                duration_days=1,
                job_metadata={
                    "max_marks": 100,
                    "passing_marks": 60,
                    "assessment_name": "Python Fundamentals Test"
                }
            ),
            PipelineJob(
                pipeline_id=pipeline.id,
                job_name="React.js Training",
                job_type=JobType.TRAINING,
                sequence_order=3,
                is_mandatory=True,
                duration_days=14,
                description="Learn React.js for frontend development"
            ),
            PipelineJob(
                pipeline_id=pipeline.id,
                job_name="React.js Assessment",
                job_type=JobType.ASSESSMENT,
                sequence_order=4,
                is_mandatory=True,
                duration_days=1,
                job_metadata={
                    "max_marks": 100,
                    "passing_marks": 70,
                    "assessment_name": "React.js Proficiency Test"
                }
            ),
            PipelineJob(
                pipeline_id=pipeline.id,
                job_name="Final Deployment",
                job_type=JobType.DEPLOYMENT,
                sequence_order=5,
                is_mandatory=True,
                duration_days=1,
                description="Deploy to project"
            )
        ]

        db.add_all(jobs)
        db.flush()
        print(f"   ✓ Created pipeline with {len(jobs)} jobs")

        # 4. Create Sample Batch
        print("\n📚 Creating sample batch...")

        batch = Batch(
            name="Batch 2024-Q1",
            pipeline_id=pipeline.id,
            start_date=date.today(),
            expected_end_date=date.today() + timedelta(days=60),
            trainer_id=trainer_user.id,
            status=BatchStatus.ACTIVE
        )
        db.add(batch)
        db.flush()
        print(f"   ✓ Created batch: {batch.name}")

        # Assign mavericks to batch
        for maverick in mavericks[:3]:  # Assign first 3 mavericks
            maverick.current_batch_id = batch.id
            maverick.profile_status = ProfileStatus.ASSIGNED

        db.commit()

        print("\n✅ Database seeded successfully!")
        print("\n📊 Summary:")
        print(f"   • Users: 4 (1 admin, 1 hr, 1 trainer, 1 manager)")
        print(f"   • Mavericks: {len(mavericks)}")
        print(f"   • Pipelines: 1")
        print(f"   • Pipeline Jobs: {len(jobs)}")
        print(f"   • Batches: 1")
        print(f"   • Assigned Mavericks: 3")

        print("\n🔐 Login Credentials:")
        print("   Admin:   admin@maverick.com / admin123")
        print("   HR:      hr@maverick.com / hr123")
        print("   Trainer: trainer@maverick.com / trainer123")
        print("   Manager: manager@maverick.com / manager123")
        print("   Maverick: maverick1@example.com / maverick123")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("\n🎉 Seeding complete!")
