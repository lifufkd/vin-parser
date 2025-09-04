from playwright.async_api import Page
from src.schemas.vehicle import Vehicle, FindVehicle
from loguru import logger

from src.core.config import nsis_parser


class NsisParser:
    LABEL_MAP = {
        "Серия полиса": "policy_series",
        "Номер полиса": "policy_number",
        "Статус договора ОСАГО": "osago_status",
        "Период использования": "usage_period",
        "Марка и модель ТС": "vehicle_model",
        "Идентификационный номер транспортного средства": "vin",
        "Государственный регистрационный знак": "license_plate",
        "Страховая компания": "insurance_company",
        "Расширение на территорию Республики Беларусь": "belarus_extension",
        "Дата запроса": "data_date"
    }

    async def _insert_search_query(self, vehicle: Vehicle, search_query: FindVehicle, browser_tab: Page) -> bool:
        try:
            if search_query.use_vin_number:
                vin_input = browser_tab.locator(nsis_parser.VIN_NUMBER_SELECTOR)
                await vin_input.fill(vehicle.vin_number)
            elif search_query.use_plate_number:
                plate_number_input = browser_tab.locator(nsis_parser.PLATE_NUMBER_SELECTOR)
                await plate_number_input.fill(vehicle.plate_number)
            else:
                logger.warning(f"No search method selected: {search_query}")
                return False
        except Exception as e:
            logger.error(f"Error insert search query: {search_query} for vehicle: {vehicle}. Error: {e}")
            return False

        return True

    async def _send_form(self, browser_tab: Page) -> bool:
        try:
            await browser_tab.locator(nsis_parser.SEND_FORM_BTN_SELECTOR).click()
            return True
        except Exception as e:
            logger.error(f"Error send form: {e}")
            return False

    async def _get_vehicle_data(self, timeout: float, browser_tab: Page) -> dict | None:
        data = {}

        try:
            await browser_tab.wait_for_selector(nsis_parser.RESULT_DATA_MODAL_WINDOW_SELECTOR,
                                                state="visible",
                                                timeout=timeout * 10 * 1000)

            date_el = await browser_tab.locator("#resp .policyDataModal__dateSlot span").inner_text()
            data["data_date"] = date_el.strip().replace("на ", "")

            items = browser_tab.locator("#resp .dataList__item")
            count = await items.count()

            for i in range(count):
                label_el = items.nth(i).locator(".dataList__labelText")
                value_el = items.nth(i).locator(".dataList__value")

                label_raw = (await label_el.inner_text()).strip().rstrip(":")
                value = (await value_el.inner_text()).strip()

                key = self.LABEL_MAP.get(label_raw)
                if key:
                    data[key] = value
                else:
                    logger.warning(f"Unknown label found: {label_raw}")

        except Exception as e:
            logger.error(f"Error get vehicle data: {e}")
            return None

        return data

    async def parse(self, vehicle: Vehicle, search_query: FindVehicle, timeout: float, browser_tab: Page) -> dict | None:
        await browser_tab.goto(nsis_parser.SITE_URL, wait_until="networkidle", timeout=timeout * 10 * 1000)

        status = await self._insert_search_query(vehicle, search_query, browser_tab)
        if not status:
            return None

        status = await self._send_form(browser_tab)
        if not status:
            return None

        results = await self._get_vehicle_data(timeout, browser_tab)
        if not results:
            return None

        return results
