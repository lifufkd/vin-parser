import asyncio
from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from src.core.config import generic_settings
from src.schemas.vehicle import Vehicle, FindVehicle, VehicleInfo
from src.services.browser_session_alocator import BrowserSessionLocator
from src.parsers.nsis import NsisParser
from src.core.exceptions import AllProxiesBanedError


class VehiclesService:
    def __init__(self):
        self.browser_session_locator = None

    async def _find_vehicles_info(
            self, vehicles: list[Vehicle], search_query: FindVehicle
    ) -> list[VehicleInfo]:
        nsis_parser = NsisParser()
        semaphore = asyncio.Semaphore(generic_settings.THREADS)

        def collect_result(task: asyncio.Task):
            if not task.cancelled() and not task.exception():
                result = task.result()
                if result:
                    results.append(result)

        async def process_vehicle(vehicle: Vehicle):
            async with semaphore:
                raw_vehicle_info = await self.browser_session_locator.allocate(
                    nsis_parser.parse,
                    vehicle,
                    search_query,
                    generic_settings.TIMEOUT,
                )
                await asyncio.sleep(generic_settings.REQUESTS_DELAY)

                if not raw_vehicle_info:
                    return None
                try:
                    vehicle_info = VehicleInfo(**raw_vehicle_info)
                    return vehicle_info
                except Exception as e:
                    logger.warning(f"Error converting vehicle info: {e}")

        results: list[VehicleInfo] = []

        try:
            async with asyncio.TaskGroup() as tg:
                for vehicle in vehicles:
                    tg.create_task(process_vehicle(vehicle)).add_done_callback(collect_result)
        except AllProxiesBanedError:
            logger.critical("All proxies are banned. Stopping all tasks.")
            raise

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
