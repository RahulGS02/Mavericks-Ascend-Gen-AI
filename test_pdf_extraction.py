"""
Test PDF extraction directly from Supabase URL
"""
import os
from dotenv import load_dotenv
import requests
import sys

# Add apps/api to path
sys.path.insert(0, 'apps/api')

# Load environment
load_dotenv('apps/api/.env')

from app.services.document_parser import DocumentParser

# The resume URL from your output
RESUME_URL = "https://aeogndsqjkbfshofudpk.supabase.co/storage/v1/object/public/resumes/20260428_110038_Rahul.G.S-Resume.pdf"

def test_pdf_extraction():
    print("=" * 80)
    print("🔍 Testing PDF Text Extraction")
    print("=" * 80)
    
    print(f"\n📄 Resume URL: {RESUME_URL}")
    
    # Download PDF (bypass SSL verification)
    print("\n1️⃣ Downloading PDF...")
    try:
        # Disable SSL verification warning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.get(RESUME_URL, timeout=30, verify=False)
        response.raise_for_status()
        pdf_content = response.content
        print(f"   ✅ Downloaded {len(pdf_content)} bytes")
    except Exception as e:
        print(f"   ❌ Download failed: {str(e)}")
        return
    
    # Try to extract text
    print("\n2️⃣ Extracting text with DocumentParser...")
    parser = DocumentParser()
    
    try:
        # Try PDF extraction
        text = parser.extract_text(pdf_content, "application/pdf")
        
        if text:
            print(f"   ✅ Extracted {len(text)} characters")
            print(f"\n📝 First 500 characters:")
            print("   " + "-" * 76)
            print("   " + text[:500].replace("\n", "\n   "))
            print("   " + "-" * 76)
            
            # Count words
            words = len(text.split())
            print(f"\n📊 Statistics:")
            print(f"   - Total characters: {len(text)}")
            print(f"   - Total words: {words}")
            print(f"   - Total lines: {text.count(chr(10))}")
            
            # Check for common resume keywords
            keywords = ["experience", "education", "skills", "projects", "work", "python", "java"]
            found_keywords = [kw for kw in keywords if kw.lower() in text.lower()]
            print(f"\n🔍 Found keywords: {', '.join(found_keywords) if found_keywords else 'None'}")
            
            return True
        else:
            print(f"   ❌ Extracted text is empty!")
            
            # Try to debug
            print("\n🔧 Debugging:")
            
            # Check if it's a valid PDF
            if pdf_content[:4] == b'%PDF':
                print("   ✅ File starts with PDF header")
            else:
                print(f"   ❌ File doesn't start with PDF header. Starts with: {pdf_content[:20]}")
            
            # Try alternative method
            print("\n3️⃣ Trying PyPDF2 directly...")
            try:
                import PyPDF2
                from io import BytesIO
                
                pdf_file = BytesIO(pdf_content)
                reader = PyPDF2.PdfReader(pdf_file)
                
                print(f"   📄 PDF has {len(reader.pages)} pages")
                
                all_text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    all_text += page_text
                    print(f"   Page {i+1}: {len(page_text)} chars")
                
                if all_text:
                    print(f"\n   ✅ PyPDF2 extracted {len(all_text)} characters!")
                    print(f"\n   First 300 chars:\n   {all_text[:300]}")
                else:
                    print(f"   ❌ PyPDF2 also got empty text - PDF might be image-based")
                    
            except Exception as e:
                print(f"   ❌ PyPDF2 failed: {str(e)}")
            
            # Try pdfplumber
            print("\n4️⃣ Trying pdfplumber...")
            try:
                import pdfplumber
                from io import BytesIO
                
                pdf_file = BytesIO(pdf_content)
                with pdfplumber.open(pdf_file) as pdf:
                    print(f"   📄 PDF has {len(pdf.pages)} pages")
                    
                    all_text = ""
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            all_text += page_text
                            print(f"   Page {i+1}: {len(page_text)} chars")
                    
                    if all_text:
                        print(f"\n   ✅ pdfplumber extracted {len(all_text)} characters!")
                        print(f"\n   First 300 chars:\n   {all_text[:300]}")
                    else:
                        print(f"   ❌ pdfplumber also got empty text")
                        print(f"   🔍 This PDF is likely image-based (scanned) and needs OCR")
                        
            except Exception as e:
                print(f"   ❌ pdfplumber failed: {str(e)}")
            
            return False
            
    except Exception as e:
        print(f"   ❌ Extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_extraction()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ PDF EXTRACTION SUCCESSFUL - AI parsing should work!")
    else:
        print("❌ PDF EXTRACTION FAILED - This is why AI parsing didn't work")
        print("\nPossible solutions:")
        print("  1. If PDF is image-based (scanned), implement OCR with pytesseract")
        print("  2. Check if PDF is password-protected")
        print("  3. Try a different PDF that has selectable text")
    print("=" * 80)
