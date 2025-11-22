from fastapi import FastAPI, UploadFile ,File,Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from .scoring import load_rubric,score_transcript

App_Root = os.path.dirname(__file__)
RUBRIC_PATH = os.path.join(App_Root,"rubric.csv")

app = FastAPI(title="Speech Scorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rebric = load_rubric(RUBRIC_PATH)

class ScoreRequesr(BaseModel):
    transcript:str
    
@app.get("/")
def root():
    return {"msg": "Speech Scorer API. POST /score with JSON {transcript: '...'}"}

@app.post("/score")
async def score_api(req:ScoreRequesr):
    res = score_transcript(req.transcript,rebric)
    return res

@app.post("/score-file")
async def score_file(file:UploadFile = File(...)):
    content = (await file.read()).decode('utf-8')
    res = score_transcript(content,rebric)
    return res
