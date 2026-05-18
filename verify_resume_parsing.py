"""
Script to verify resume parsing results in the database
Run this after uploading a resume to check if AI parsing worked
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Load environment variables from .env file
load_dotenv('apps/api/.env')

def check_latest_maverick():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Make sure apps/api/.env file exists with DATABASE_URL")
        return

    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get the latest maverick (most recently created)
    cursor.execute("""
        SELECT * FROM mavericks
        ORDER BY created_at DESC
        LIMIT 1
    """)

    maverick = cursor.fetchone()

    if not maverick:
        print("❌ No mavericks found in database")
        conn.close()
        return
    
    print("=" * 80)
    print(f"📋 LATEST MAVERICK: {maverick['name']} ({maverick['email']})")
    print("=" * 80)

    print(f"\n📧 Email: {maverick['email']}")
    print(f"📞 Phone: {maverick['phone']}")
    print(f"🎓 College: {maverick['college']}")
    print(f"📚 Degree: {maverick['degree']} - {maverick['branch']}")
    print(f"📅 Graduation: {maverick['graduation_year']}")
    print(f"📊 CGPA: {maverick['cgpa']}")

    print(f"\n📄 Resume URL: {maverick['resume_url'] or 'Not uploaded'}")
    print(f"✅ Profile Status: {maverick['profile_status']}")
    print(f"🚀 Deployment Status: {maverick['deployment_status']}")
    
    print("\n" + "=" * 80)
    print("🤖 AI PARSING RESULTS")
    print("=" * 80)
    
    # Check AI extracted skills
    ai_skills = maverick['ai_extracted_skills'] or []
    if ai_skills:
        print(f"\n✅ AI Extracted Skills ({len(ai_skills)} skills):")
        for skill in ai_skills[:20]:  # Show first 20
            print(f"  • {skill}")
        if len(ai_skills) > 20:
            print(f"  ... and {len(ai_skills) - 20} more")
    else:
        print("\n❌ No AI extracted skills found")

    # Check AI summary
    if maverick['ai_summary']:
        print(f"\n✅ AI Generated Summary:")
        print(f"  {maverick['ai_summary']}")
    else:
        print("\n❌ No AI summary generated")

    # Check complete AI resume data
    if maverick['ai_resume_data']:
        print(f"\n✅ Complete AI Resume Data Available:")
        data = maverick['ai_resume_data']
        
        if data.get("personal_info"):
            print("\n  📇 Personal Info:")
            for key, value in data["personal_info"].items():
                if value:
                    print(f"    - {key}: {value}")
        
        if data.get("education"):
            print(f"\n  🎓 Education ({len(data['education'])} entries):")
            for edu in data["education"][:3]:  # Show first 3
                print(f"    - {edu.get('degree')} in {edu.get('branch')} from {edu.get('college')}")
        
        if data.get("experience"):
            print(f"\n  💼 Experience ({len(data['experience'])} entries):")
            for exp in data["experience"][:3]:  # Show first 3
                print(f"    - {exp.get('role')} at {exp.get('company')} ({exp.get('duration')})")
        
        if data.get("projects"):
            print(f"\n  🚀 Projects ({len(data['projects'])} entries):")
            for proj in data["projects"][:3]:  # Show first 3
                print(f"    - {proj.get('name')}: {proj.get('description', '')[:60]}...")
        
        if data.get("skills"):
            skills = data["skills"]
            total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
            print(f"\n  💡 Skills Breakdown ({total_skills} total):")
            for category, items in skills.items():
                if isinstance(items, list) and items:
                    print(f"    - {category.title()}: {len(items)} items")
        
        if data.get("certifications"):
            print(f"\n  🏆 Certifications ({len(data['certifications'])} entries):")
            for cert in data["certifications"]:
                print(f"    - {cert.get('name')} ({cert.get('year')})")
        
        if data.get("total_experience_years"):
            print(f"\n  ⏱️  Total Experience: {data['total_experience_years']} years")
        
    else:
        print("\n❌ No complete AI resume data found")
        print("\nPossible reasons:")
        print("  1. Resume text extraction failed")
        print("  2. AI service is not available")
        print("  3. AI parsing encountered an error")
        print("  4. Resume was not uploaded")
    
    print("\n" + "=" * 80)
    print("💾 RAW DATA")
    print("=" * 80)
    print(f"\nManual Skills: {maverick['skills']}")
    print(f"AI Extracted Skills: {maverick['ai_extracted_skills']}")
    print(f"Resume Data Keys: {list(maverick['ai_resume_data'].keys()) if maverick['ai_resume_data'] else 'None'}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_latest_maverick()
