from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

@router.get("/")
def home():
    return {"message":"API is working successfully! For My SmartCarX"}
