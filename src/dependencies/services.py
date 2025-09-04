from src.services.vehicles import VehiclesService


async def get_vehicles_service():
    return VehiclesService()
