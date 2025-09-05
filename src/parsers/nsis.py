import asyncio
from datetime import datetime
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import Page
from loguru import logger

from src.core.exceptions import SoftBanError, SolidBanError
from src.core.config import nsis_parser
from src.schemas.vehicle import Vehicle, FindVehicle


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

    async def _insert_search_query(
            self,
            vehicle: Vehicle,
            search_query: FindVehicle,
            browser_tab: Page
    ) -> bool:
        try:
            if search_query.use_vin_number:
                vin_input = browser_tab.locator(nsis_parser.VIN_NUMBER_SELECTOR).first
                await vin_input.scroll_into_view_if_needed()
                await vin_input.fill(vehicle.vin_number)

            elif search_query.use_plate_number:
                plate_number_input = browser_tab.locator(nsis_parser.PLATE_NUMBER_SELECTOR).first
                await plate_number_input.scroll_into_view_if_needed()
                await plate_number_input.fill(vehicle.plate_number)

            else:
                logger.warning(f"No search method selected: {search_query}")
                return False

            date_str = vehicle.date.strftime("%Y-%m-%d")
            selector = "input[placeholder='Выберите дату']"
            await browser_tab.evaluate(
                """({selector, dateStr}) => {
                    const visibleInput = document.querySelector(selector);
                    if (!visibleInput) return;

                    const hiddenInput = visibleInput.closest('.staticContainer').querySelector('input[type="hidden"]');
                    if (!hiddenInput) return;

                    hiddenInput.value = dateStr;
                    hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
                    hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
                }""",
                {"selector": selector, "dateStr": date_str}
            )

        except Exception as e:
            logger.error(
                f"Error insert search query: {search_query} "
                f"for vehicle: {vehicle}. Error: {e}"
            )
            return False

        return True

    async def _send_form(self, browser_tab: Page) -> bool:
        try:
            await browser_tab.locator(nsis_parser.SEND_FORM_BTN_SELECTOR).first.click()
            return True
        except Exception as e:
            logger.error(f"Error send form: {e}")
            return False

    async def wait_for_one_of(self, selectors: list[str], timeout: float, browser_tab):
        tasks = {
            selector: asyncio.create_task(
                browser_tab.wait_for_selector(selector, state="visible", timeout=timeout * 1000)
            )
            for selector in selectors
        }

        done, pending = await asyncio.wait(tasks.values(), return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        for selector, task in tasks.items():
            if task in done:
                try:
                    element = await task
                    return element, selector
                except PlaywrightTimeoutError:
                    continue

        return None, None

    async def _get_vehicle_data(self, timeout: float, browser_tab: Page) -> dict | None:
        data = {}

        try:
            element, selector = await self.wait_for_one_of(
                [
                    nsis_parser.RESULT_DATA_MODAL_WINDOW_SELECTOR,
                    nsis_parser.ERROR_DATA_MODAL_WINDOW_SELECTOR
                ],
                timeout,
                browser_tab
            )

            if selector:
                if selector == nsis_parser.ERROR_DATA_MODAL_WINDOW_SELECTOR:
                    raise SoftBanError()
            else:
                raise SoftBanError()

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

        except SoftBanError:
            raise
        except Exception as e:
            logger.error(f"Error get vehicle data: {e}")
            return None

        return data

    async def parse(self, vehicle: Vehicle, search_query: FindVehicle, timeout: float, browser_tab: Page) -> dict | None:
        await browser_tab.goto(nsis_parser.SITE_URL, wait_until="load", timeout=timeout * 10 * 1000)
        if browser_tab.url == nsis_parser.BLOCK_PAGE_URL:
            raise SolidBanError()

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
