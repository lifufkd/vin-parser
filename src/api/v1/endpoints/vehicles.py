from io import BytesIO
from fastapi import APIRouter, status, UploadFile, File, Query, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from src.dependencies.services import get_vehicles_service
from src.services.vehicles import VehiclesService
from src.core.excel import ExcelLoader
from src.schemas.vehicle import FindVehicle, Vehicle


vehicles_router = APIRouter()


@vehicles_router.post("/search", status_code=status.HTTP_200_OK)
async def find_vehicles(
    search_query: FindVehicle = Query(),
    file: UploadFile = File(),
    vehicles_service: VehiclesService = Depends(get_vehicles_service),
):
    ALLOWED_CONTENT_TYPES = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ]

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have .xlsx or .xls extension"
        )

    excel_loader = ExcelLoader()

    file_content: bytes = await file.read()
    vehicles = await excel_loader.load(file_content, model=Vehicle)
    if not vehicles:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Excel file empty or unprocessable")

    vehicles_info = await vehicles_service.search(vehicles, search_query)
    if not vehicles_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No vehicles found")

    excel_stream = await excel_loader.save(vehicles_info)
    if not excel_stream:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating excel file")

    return StreamingResponse(
        BytesIO(excel_stream),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=export.xlsx"}
    )

