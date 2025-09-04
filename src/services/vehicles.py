from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from src.core.config import generic_settings
from src.schemas.vehicle import Vehicle, FindVehicle, VehicleInfo
from src.services.browser_session_alocator import BrowserSessionLocator
from src.parsers.nsis import NsisParser


class VehiclesService:
    def __init__(self):
        self.browser_session_locator = None

    async def _find_vehicles_info(self, vehicles: list[Vehicle], search_query: FindVehicle) -> list[VehicleInfo]:
        results = []
        nsis_parser = NsisParser()

        for vehicle in vehicles:
            try:
                raw_vehicle_info = await self.browser_session_locator.allocate(
                    nsis_parser.parse,
                    vehicle,
                    search_query,
                    generic_settings.TIMEOUT
                )

                results.append(
                    VehicleInfo(
                        **raw_vehicle_info
                    )
                )
            except Exception as e:
                logger.warning(f"Error processing vehicle info for vehicle {vehicle}: {e}")

        return results

    async def search(self, vehicles: list[Vehicle], search_query: FindVehicle) -> list[VehicleInfo]:
        async with Stealth().use_async(async_playwright()) as session:

            logger.debug("Launching browser...")
            browser_session = await session.chromium.launch(
                headless=generic_settings.HEADLESS,
                args=[
                    '--enable-webgl',
                    '--use-gl=swiftshader',
                    '--enable-accelerated-2d-canvas'
                ]
            )
            self.browser_session_locator = BrowserSessionLocator(browser_session)
            logger.debug("Browser successfully launched!")

            return await self._find_vehicles_info(vehicles, search_query)
