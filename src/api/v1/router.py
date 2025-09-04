from fastapi import APIRouter
from src.api.v1.endpoints import vehicles

api_v1_router = APIRouter()


api_v1_router.include_router(vehicles.vehicles_router, prefix="/vehicles", tags=["Vehicles"])
