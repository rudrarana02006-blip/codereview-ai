from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List

import models
import database
import ollama_service

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Local Code Review API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/review", response_model=models.ReviewResponse)
async def create_review(review_request: models.ReviewCreate, db: Session = Depends(get_db)):
    try:
        review_data = await ollama_service.generate_code_review(review_request.raw_input)
        
        db_review = models.Review(
            raw_input=review_request.raw_input,
            summary=review_data.get("summary", "No summary provided."),
            overall_rating=review_data.get("overall_rating", "Needs Minor Changes - Unable to determine rating.")
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        
        for risk in review_data.get("risks", []):
            db_risk = models.Risk(
                review_id=db_review.id,
                description=risk.get("description", ""),
                severity=risk.get("severity", "medium")
            )
            db.add(db_risk)
            
        for suggestion in review_data.get("suggestions", []):
            db_suggestion = models.Suggestion(
                review_id=db_review.id,
                description=suggestion.get("description", ""),
                line_reference=suggestion.get("line_reference", None)
            )
            db.add(db_suggestion)
            
        db.commit()
        db.refresh(db_review)
        return db_review

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reviews", response_model=List[models.ReviewResponse])
def get_reviews(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).order_by(models.Review.created_at.desc()).offset(skip).limit(limit).all()
    return reviews


@app.get("/api/reviews/{review_id}", response_model=models.ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
