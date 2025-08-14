from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.scraping import fetch_html, extract_products

router = APIRouter(prefix="/scraping", tags=["scraping"])

class ScrapeBody(BaseModel):
    url: str
    wait_selector: Optional[str] = None

@router.post("/scrape")
def scrape(body: ScrapeBody):
    """Hace scraping de una URL y extrae productos"""
    try:
        html = fetch_html(body.url, body.wait_selector)
        items = extract_products(html)
        return {"count": len(items), "items": items[:50]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping URL: {str(e)}")
