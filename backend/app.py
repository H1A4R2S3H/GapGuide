import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import fitz  # PyMuPDF for PDF processing
from core.recommender import JobRecommender
from core.skill_extractor import SkillExtractor 


processed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'jobs_processed.csv')
recommender = JobRecommender(data_path=processed_path)

skills_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'master_skills.json')
skill_extractor = SkillExtractor(skills_file_path=skills_path)

app = FastAPI()

origins = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class SkillInput(BaseModel):
    user_skills: List[str]
class RoleSkillInput(BaseModel):
    user_skills: List[str]
    job_title: str
class TextInput(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the GapGuide API"}

@app.post("/recommend/")
def recommend_jobs(skill_input: SkillInput):
    return recommender.get_recommendations(skill_input.user_skills)

@app.post("/role-skill-gap/")
def role_skill_gap(role_input: RoleSkillInput):
    return recommender.analyze_role_skill_gap(role_input.user_skills, role_input.job_title)

@app.post("/extract-skills/")
def extract_skills_from_text(text_input: TextInput):
    skills = skill_extractor.extract_skills(text_input.text)
    return {"extracted_skills": skills}

@app.post("/extract-text-from-pdf/")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF file, extracts all text content, and returns it.
    """
    if file.content_type != 'application/pdf':
        return {"error": "Invalid file type. Please upload a PDF."}

    try:
        # Read the uploaded file into memory
        pdf_bytes = await file.read()
        
        # Open the PDF from the in-memory bytes
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            full_text = ""
            # Iterate through each page and extract text
            for page in doc:
                full_text += page.get_text()
        
        return {"extracted_text": full_text}
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return {"error": "Failed to process the PDF file."}