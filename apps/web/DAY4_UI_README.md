# Day 4 UI: Maverick Onboarding

## ✅ What's Been Built

### Components Created:
1. **`ResumeUpload.tsx`** - Drag-and-drop resume upload with AI parsing
2. **`MaverickRegistrationForm.tsx`** - Complete registration form
3. **`ProfileStatusBadge.tsx`** - Status indicator component
4. **`mavericks.ts`** - API client for all maverick operations

### Pages Created:
1. **`/mavericks/register`** - Two-step registration process
   - Step 1: Personal & education details
   - Step 2: Resume upload with AI extraction
   
2. **`/mavericks/profile`** - View complete profile with all details

## 🚀 How to Run

### 1. Start the Backend API (Terminal 1)
```bash
cd apps/api
uvicorn app.main:app --reload
```
Backend will run on: http://localhost:8000

### 2. Install Frontend Dependencies
```bash
cd apps/web
npm install
```

### 3. Configure Environment
Create `apps/web/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Start the Frontend (Terminal 2)
```bash
cd apps/web
npm run dev
```
Frontend will run on: http://localhost:3000

## 📋 Testing the Flow

### As a Maverick:

1. **Register** 
   - Go to http://localhost:3000/mavericks/register
   - Fill in personal details (name, email, phone)
   - Add education (college, degree, branch, CGPA)
   - Add social links (GitHub, LinkedIn)
   - Add skills manually
   - Click "Save Profile"

2. **Upload Resume**
   - Drag & drop your resume (PDF/DOC)
   - AI will extract:
     - Skills
     - Education
     - Experience
     - Summary
   - Review extracted data
   - Click "Submit for Review"

3. **View Profile**
   - Go to http://localhost:3000/mavericks/profile
   - See complete profile with status badge
   - Edit profile if needed

### Profile Status Flow:
```
DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED/REJECTED
 📝        📤            🔍             ✅/❌
```

## 🎨 Features Implemented

✅ **Multi-step registration**
✅ **Drag-and-drop file upload**
✅ **AI resume parsing**
✅ **Skills management** (add/remove)
✅ **Profile status indicators**
✅ **Responsive design** (mobile-friendly)
✅ **Form validation**
✅ **Error handling**
✅ **Loading states**
✅ **Real-time AI extraction display**

## 📸 UI Screenshots

### Registration Form
- Clean, modern design
- Step-by-step process
- Progress indicator
- Validation on all fields

### Resume Upload
- Drag & drop area
- File preview
- Upload progress
- AI parsing animation

### Profile View
- Status badge at top
- Contact info cards
- Education details
- Skills tags
- AI-generated summary
- Review notes (if rejected)

## 🔧 Next Steps

To complete Day 4-5 fully, you can also build:
- Profile edit page (`/mavericks/edit/[id]`)
- List of all mavericks (`/mavericks`)
- Search & filter functionality

But the core MVP is ready to use! 🎉

## 🐛 Troubleshooting

**Issue**: "Failed to fetch profile"
- **Fix**: Make sure backend is running on port 8000
- Check `.env.local` has correct API_URL

**Issue**: "Resume upload fails"
- **Fix**: Check file size (max 5MB)
- Ensure file is PDF/DOC/DOCX format

**Issue**: "CORS error"
- **Fix**: Backend CORS is configured for localhost:3000
- Make sure you're accessing from correct URL

## 📦 File Structure

```
apps/web/src/
├── app/
│   └── mavericks/
│       ├── register/
│       │   └── page.tsx          # Registration page
│       └── profile/
│           └── page.tsx           # Profile view page
├── components/
│   └── mavericks/
│       ├── MaverickRegistrationForm.tsx
│       ├── ResumeUpload.tsx
│       └── ProfileStatusBadge.tsx
└── lib/
    └── api/
        ├── client.ts              # Axios base config
        └── mavericks.ts           # Maverick API client
```

Ready to test! 🚀
