from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from groq import Groq
import base64
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import os, uuid, json
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

# Init FastAPI
app = FastAPI(title="Community Hero API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'community-hero-501009' 
})
db = firestore.client()
bucket = storage.bucket()

# Init Gemini
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─────────────────────────────────────────
# GEMINI VISION ANALYSIS
# ─────────────────────────────────────────

async def analyze_image_with_gemini(image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                },
                {
                    "type": "text",
                    "text": """Analyze this community issue image and return ONLY valid JSON:
{
    "category": "one of: Pothole, Broken Streetlight, Garbage Dump, Water Leakage, Damaged Road, Open Drain, Illegal Parking, Other",
    "severity": "one of: Low, Medium, High, Critical",
    "title": "short 5-7 word title",
    "description": "2-3 sentence description",
    "suggested_department": "one of: PWD, Municipal Corporation, Electricity Board, Water Department, Traffic Police, Other",
    "estimated_urgency": "Fix within 24 hours or Fix within 1 week etc",
    "confidence": 0.90
}"""
                }
            ]
        }],
        max_tokens=500
    )
    
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    print("GROQ RESPONSE:", text)
    return json.loads(text)


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Community Hero API is running"}


@app.post("/report")
async def report_issue(
    image: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...),
    citizen_name: str = Form(...),
    citizen_phone: str = Form(...),
    issue_type: str = Form(default="Auto Detect")
):
    try:
        # Read image
        image_bytes = await image.read()
        
        # Upload to Firebase Storage
        issue_id = str(uuid.uuid4())[:8].upper()
        blob = bucket.blob(f"issues/{issue_id}/{image.filename}")
        blob.upload_from_string(image_bytes, content_type=image.content_type)
        blob.make_public()
        image_url = blob.public_url
        
        # Analyze with Gemini Vision
        ai_analysis = await analyze_image_with_gemini(image_bytes)
        
        # Save to Firestore
        issue_data = {
            "issue_id": issue_id,
            "citizen_name": citizen_name,
            "citizen_phone": citizen_phone,
            "location": {
                "lat": lat,
                "lng": lng
            },
            "image_url": image_url,
            "ai_analysis": ai_analysis,
            "status": "Reported",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "upvotes": 0
        }
        
        db.collection("issues").document(issue_id).set(issue_data)
        
        return {
            "success": True,
            "issue_id": issue_id,
            "message": f"Issue #{issue_id} reported successfully",
            "ai_analysis": ai_analysis,
            "image_url": image_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/issues")
def get_all_issues(status: str = None, category: str = None):
    try:
        ref = db.collection("issues")
        docs = ref.stream()
        
        issues = []
        for doc in docs:
            data = doc.to_dict()
            # Filter by status if provided
            if status and data.get("status") != status:
                continue
            if category and data.get("ai_analysis", {}).get("category") != category:
                continue
            issues.append(data)
        
        # Sort by created_at descending
        issues.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return {"issues": issues, "total": len(issues)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/issues/{issue_id}")
def get_issue(issue_id: str):
    try:
        doc = db.collection("issues").document(issue_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Issue not found")
        return doc.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/issues/{issue_id}/status")
def update_status(issue_id: str, status: str = Form(...)):
    try:
        valid_statuses = ["Reported", "In Progress", "Resolved", "Rejected"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        db.collection("issues").document(issue_id).update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })
        return {"success": True, "issue_id": issue_id, "new_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/issues/{issue_id}/upvote")
def upvote_issue(issue_id: str):
    try:
        ref = db.collection("issues").document(issue_id)
        ref.update({"upvotes": firestore.Increment(1)})
        return {"success": True, "message": "Upvoted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    try:
        docs = list(db.collection("issues").stream())
        issues = [d.to_dict() for d in docs]
        
        stats = {
            "total": len(issues),
            "reported": sum(1 for i in issues if i.get("status") == "Reported"),
            "in_progress": sum(1 for i in issues if i.get("status") == "In Progress"),
            "resolved": sum(1 for i in issues if i.get("status") == "Resolved"),
            "by_category": {},
            "by_severity": {}
        }
        
        for issue in issues:
            cat = issue.get("ai_analysis", {}).get("category", "Other")
            sev = issue.get("ai_analysis", {}).get("severity", "Low")
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))