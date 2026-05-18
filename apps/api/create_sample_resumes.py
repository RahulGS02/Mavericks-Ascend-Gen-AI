"""
Create realistic sample resume PDFs for testing
Requires: pip install reportlab
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path

def create_resume_1():
    """Create Resume 1: Full Stack Developer"""
    
    output_dir = Path("test_resumes")
    output_dir.mkdir(exist_ok=True)
    
    filename = output_dir / "rahul_kumar_fullstack.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Name
    story.append(Paragraph("RAHUL KUMAR", title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Contact
    contact = Paragraph(
        "Email: rahul.kumar@email.com | Phone: +91-9876543210 | Bangalore, India<br/>"
        "GitHub: github.com/rahulkumar | LinkedIn: linkedin.com/in/rahulkumar",
        styles['Normal']
    )
    story.append(contact)
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    summary_text = """
    Full Stack Developer with 3+ years of experience building scalable web applications.
    Proficient in React, Node.js, Python, and cloud technologies. Strong problem-solving skills
    with expertise in microservices architecture and DevOps practices.
    """
    story.append(Paragraph(summary_text, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    # Education
    story.append(Paragraph("EDUCATION", heading_style))
    education_text = """
    <b>Bachelor of Technology in Computer Science Engineering</b><br/>
    XYZ Institute of Technology, Bangalore<br/>
    CGPA: 8.5/10 | Graduated: May 2021
    """
    story.append(Paragraph(education_text, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    # Experience
    story.append(Paragraph("WORK EXPERIENCE", heading_style))
    
    exp1 = """
    <b>Senior Software Engineer | ABC Tech Solutions</b><br/>
    <i>January 2022 - Present (2 years)</i><br/>
    • Developed microservices architecture using Node.js and Express, improving scalability by 40%<br/>
    • Built responsive frontends with React and TypeScript, serving 100K+ daily active users<br/>
    • Implemented CI/CD pipelines using Docker, Kubernetes, and Jenkins<br/>
    • Technologies: React, Node.js, MongoDB, AWS, Docker, Kubernetes, Redis
    """
    story.append(Paragraph(exp1, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    exp2 = """
    <b>Junior Developer | StartupCo</b><br/>
    <i>July 2021 - December 2021 (6 months)</i><br/>
    • Created REST APIs for mobile applications using Python Flask<br/>
    • Optimized database queries, improving performance by 40%<br/>
    • Technologies: Python, Flask, PostgreSQL, Git
    """
    story.append(Paragraph(exp2, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    # Skills
    story.append(Paragraph("TECHNICAL SKILLS", heading_style))
    skills_text = """
    <b>Languages:</b> JavaScript, Python, TypeScript, Java, SQL<br/>
    <b>Frameworks:</b> React, Node.js, Express, Flask, Spring Boot, Next.js<br/>
    <b>Tools:</b> Git, Docker, Kubernetes, Jenkins, AWS, MongoDB, PostgreSQL<br/>
    <b>Databases:</b> MongoDB, PostgreSQL, MySQL, Redis<br/>
    <b>Soft Skills:</b> Problem Solving, Team Leadership, Agile Development, Communication
    """
    story.append(Paragraph(skills_text, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    # Projects
    story.append(Paragraph("PROJECTS", heading_style))
    
    proj1 = """
    <b>E-Commerce Platform</b><br/>
    Built full-stack e-commerce application with React and Node.js. Integrated payment gateways
    (Stripe, Razorpay). Deployed on AWS with auto-scaling.<br/>
    Technologies: React, Node.js, MongoDB, Redis, AWS<br/>
    URL: github.com/rahul/ecommerce
    """
    story.append(Paragraph(proj1, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    proj2 = """
    <b>AI Chatbot</b><br/>
    Developed chatbot using OpenAI API and Python. Deployed on AWS Lambda with DynamoDB.<br/>
    Technologies: Python, OpenAI, AWS Lambda, DynamoDB
    """
    story.append(Paragraph(proj2, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    # Certifications
    story.append(Paragraph("CERTIFICATIONS", heading_style))
    certs = """
    • AWS Certified Solutions Architect - Associate (2023)<br/>
    • MongoDB Developer Certification (2022)<br/>
    • Google Cloud Professional Developer (2023)
    """
    story.append(Paragraph(certs, styles['BodyText']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {filename}")
    return filename


def create_resume_2():
    """Create Resume 2: Data Scientist"""
    
    output_dir = Path("test_resumes")
    output_dir.mkdir(exist_ok=True)
    
    filename = output_dir / "priya_sharma_datascientist.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Similar structure for second resume...
    # (Abbreviated for brevity - you can expand this)
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER)
    
    story.append(Paragraph("PRIYA SHARMA", title_style))
    story.append(Paragraph("Data Scientist", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {filename}")
    return filename


if __name__ == "__main__":
    print("📄 Creating sample resume PDFs...")
    print("="*70)
    
    try:
        resume1 = create_resume_1()
        # resume2 = create_resume_2()
        
        print("\n" + "="*70)
        print("✅ Sample resumes created successfully!")
        print("\nNow run: python test_resume_parser_real.py")
        print("="*70)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure reportlab is installed: pip install reportlab")
