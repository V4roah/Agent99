from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.classify import load_seed_csv, train_and_save, predict

router = APIRouter(prefix="/classification", tags=["classification"])

class TrainBody(BaseModel):
    csv_path: str = "data/seed.csv"

class PredictBody(BaseModel):
    texts: List[str]

@router.post("/train")
def train(body: TrainBody):
    """Entrena el modelo de clasificación"""
    try:
        data = load_seed_csv(body.csv_path)
        model_path = train_and_save(data)
        return {"model_path": model_path, "samples": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@router.post("/classify")
def classify(body: PredictBody):
    """Clasifica textos usando el modelo entrenado"""
    try:
        labels = predict(body.texts)
        return {"labels": labels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying texts: {str(e)}")
