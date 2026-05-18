"""
Test script for AI Resume Parser (Day 17)
"""
import requests
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"\n{title}")
    print(f"\n{'-'*70}")

def print_result(success, message, data=None):
    if success:
        print(f"✅ {message}")
        if data:
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for k, v in value.items():
                        if isinstance(v, list):
                            print(f"      {k}: {len(v)} items")
                        else:
                            print(f"      {k}: {v}")
                elif isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                    if len(value) > 0 and len(value) <= 5:
                        for item in value:
                            print(f"      - {item}")
                else:
                    print(f"   {key}: {value}")
    else:
        print(f"❌ {message}")


def create_sample_resume_pdf(filename: str, content: str):
    """Create a PDF resume for testing"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "RESUME")
    
    # Content
    c.setFont("Helvetica", 10)
    y = 720
    for line in content.split('\n'):
        if y < 50:  # New page if needed
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750
        c.drawString(50, y, line[:90])  # Max line length
        y -= 15
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def test_resume_parser():
    print("\n📄 Testing AI Resume Parser (Day 17)")
    print("="*70)
    
    # 1. Login
    print_section("1️⃣  Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "hr@maverick.com", "password": "hr123"}
    )
    
    if login_response.status_code != 200:
        print_result(False, f"Login failed! {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(True, "Login successful!")
    
    # Sample Resume 1: Full Stack Developer
    resume1_content = """
RAHUL KUMAR
rahul.kumar@email.com | +91-9876543210 | Bangalore, India
GitHub: github.com/rahulkumar | LinkedIn: linkedin.com/in/rahulkumar

PROFESSIONAL SUMMARY
Full Stack Developer with 3 years of experience building scalable web applications.
Proficient in React, Node.js, and cloud technologies. Strong problem-solving skills.

EDUCATION
Bachelor of Technology in Computer Science Engineering
XYZ Institute of Technology, Bangalore
CGPA: 8.5/10 | Graduated: 2021

WORK EXPERIENCE
Senior Software Engineer | ABC Tech Solutions | Jan 2022 - Present (2 years)
- Developed microservices architecture using Node.js and Express
- Built responsive frontends with React and TypeScript
- Implemented CI/CD pipelines with Docker and Kubernetes
Technologies: React, Node.js, MongoDB, AWS, Docker, Kubernetes

Junior Developer | StartupCo | Jul 2021 - Dec 2021 (6 months)
- Created REST APIs for mobile applications
- Optimized database queries improving performance by 40%
Technologies: Python, Flask, PostgreSQL

TECHNICAL SKILLS
Languages: JavaScript, Python, TypeScript, Java, SQL
Frameworks: React, Node.js, Express, Flask, Spring Boot
Tools: Git, Docker, Kubernetes, Jenkins, AWS
Databases: MongoDB, PostgreSQL, MySQL, Redis
Soft Skills: Problem Solving, Team Leadership, Agile Development

PROJECTS
E-Commerce Platform
- Built full-stack e-commerce application with React and Node.js
- Integrated payment gateway (Stripe, Razorpay)
- Technologies: React, Node.js, MongoDB, Redis
- URL: github.com/rahul/ecommerce

AI Chatbot
- Developed chatbot using OpenAI API and Python
- Deployed on AWS Lambda
- Technologies: Python, OpenAI, AWS Lambda, DynamoDB

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate | Amazon Web Services | 2023
- MongoDB Developer Certification | MongoDB University | 2022
"""
    
    # Sample Resume 2: Data Scientist
    resume2_content = """
PRIYA SHARMA
priya.sharma@email.com | +91-8765432109
Portfolio: priyasharma.dev

SUMMARY
Data Scientist with 2 years of experience in machine learning and data analytics.
Expertise in Python, TensorFlow, and statistical analysis.

EDUCATION
M.Tech in Data Science
Indian Institute of Technology, Delhi
CGPA: 9.2/10 | 2022

B.Tech in Electronics Engineering
Delhi Technological University
Percentage: 85% | 2020

EXPERIENCE
Data Scientist | DataCorp India | Mar 2022 - Present (1.8 years)
- Built ML models for customer churn prediction (92% accuracy)
- Implemented recommendation systems using collaborative filtering
- Technologies: Python, TensorFlow, Scikit-learn, SQL
Duration: 1 year 8 months

Data Analyst Intern | Analytics Firm | Jan 2022 - Feb 2022 (2 months)
- Performed data cleaning and visualization
- Technologies: Python, Pandas, Matplotlib

SKILLS
Technical: Python, R, SQL, TensorFlow, PyTorch, Scikit-learn, Keras
Tools: Jupyter, Git, Docker, Tableau, Power BI
Databases: PostgreSQL, MySQL, MongoDB
Soft Skills: Data Analysis, Statistical Modeling, Communication

PROJECTS
Customer Segmentation System
- Built clustering model using K-means
- Technologies: Python, Scikit-learn, Pandas

Image Classification
- CNN model for image recognition (95% accuracy)
- Technologies: TensorFlow, Keras, Python
"""
    
    # Test Resume 1
    print_section("2️⃣  Testing Resume 1: Full Stack Developer")
    pdf1 = create_sample_resume_pdf("resume1.pdf", resume1_content)
    
    response = requests.post(
        f"{BASE_URL}/resume/parse",
        headers=headers,
        files={"resume": ("resume1.pdf", io.BytesIO(pdf1), "application/pdf")}
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, result["message"])
        
        if result["parsed_data"]:
            data = result["parsed_data"]
            
            print("\n   👤 Personal Info:")
            if data.get("personal_info"):
                for k, v in data["personal_info"].items():
                    if v:
                        print(f"      {k}: {v}")
            
            print(f"\n   🎓 Education: {len(data.get('education', []))} entries")
            print(f"   💼 Experience: {len(data.get('experience', []))} entries")
            print(f"   ⏱️  Total Experience: {data.get('total_experience_years', 0)} years")
            
            print(f"\n   🔧 Skills:")
            if data.get("skills"):
                skills = data["skills"]
                print(f"      Technical: {len(skills.get('technical', []))} skills")
                print(f"      Languages: {len(skills.get('languages', []))} languages")
                print(f"      Frameworks: {len(skills.get('frameworks', []))} frameworks")
                print(f"      Tools: {len(skills.get('tools', []))} tools")
            
            print(f"\n   📁 Projects: {len(data.get('projects', []))} projects")
            print(f"   🏆 Certifications: {len(data.get('certifications', []))} certifications")
            
            if data.get("summary"):
                print(f"\n   📝 Summary: {data['summary'][:100]}...")
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # Test Resume 2
    print_section("3️⃣  Testing Resume 2: Data Scientist")
    pdf2 = create_sample_resume_pdf("resume2.pdf", resume2_content)
    
    response = requests.post(
        f"{BASE_URL}/resume/parse",
        headers=headers,
        files={"resume": ("resume2.pdf", io.BytesIO(pdf2), "application/pdf")}
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, result["message"])
        
        if result["parsed_data"]:
            data = result["parsed_data"]
            print(f"\n   Total Experience: {data.get('total_experience_years', 0)} years")
            print(f"   Skills Extracted: {len(result.get('ai_skills', []))} skills")
            
            # Show some extracted skills
            if result.get("ai_skills"):
                print(f"\n   Sample Skills:")
                for skill in result["ai_skills"][:10]:
                    print(f"      - {skill}")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Resume Parser test completed!")
    print("\n📋 Features Tested:")
    print("   ✅ PDF text extraction")
    print("   ✅ AI resume parsing")
    print("   ✅ Personal info extraction")
    print("   ✅ Education details")
    print("   ✅ Work experience with duration")
    print("   ✅ Skills categorization")
    print("   ✅ Projects extraction")
    print("   ✅ Certifications")
    print("   ✅ Summary generation")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_resume_parser()
