from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

from core.recommender import JobRecommender

processed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'jobs_processed.csv')
recommender = JobRecommender(data_path=processed_path)

app = FastAPI()

origins = ["http://localhost:5173", "http://localhost:3000"]
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the GapGuide API"}

@app.post("/recommend/")
def recommend_jobs(skill_input: SkillInput):
    return recommender.get_recommendations(skill_input.user_skills)

@app.post("/role-skill-gap/")
def role_skill_gap(role_input: RoleSkillInput):
    return recommender.analyze_role_skill_gap(role_input.user_skills, role_input.job_title)