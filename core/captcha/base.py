import asyncio
from typing import Optional
import httpx


class CaptchaSolverBase:
    def __init__(
            self,
            api_key: str,
            max_attempts: int = 10,
            soft_id: int = None,
            base_url: str = "",
    ):
        self.api_key = api_key
        self.max_attempts = max_attempts
        self.soft_id = soft_id

        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30)

    async def solve_turnistale(self, site_key: str, page_url: str) -> tuple[bool, Optional[str]] | tuple[bool, str]:
        CAPTCHA_TYPE_MAP = {
            "https://api.capsolver.com": "AntiTurnstileTaskProxyLess",
            "https://api.capmonster.cloud": "TurnstileTask",
        }

        captcha_type = CAPTCHA_TYPE_MAP.get(self.base_url, "TurnstileTaskProxyless")

        captcha_data = {
            "clientKey": self.api_key,
            "task": {
                "type": captcha_type,
                "websiteURL": page_url,
                "websiteKey": site_key,
            }
        }

        if self.soft_id is not None:
            captcha_data["softId"] = self.soft_id

        try:
            resp = await self.client.post(f"{self.base_url}/createTask", json=captcha_data)
            resp.raise_for_status()
            data = resp.json()

            if data.get("errorId") == 0:
                task_id = data.get("taskId")
                return await self.get_captcha_result(task_id)
            return False, data.get("errorDescription", "Unknown error")

        except httpx.HTTPStatusError as err:
            return False, f"HTTP error: {err}"
        except httpx.TimeoutException:
            return False, "Request timed out"
        except Exception as err:
            return False, f"Unexpected error: {err}"


    async def solve_geetest(self, page_url: str, gt: str, challenge: str, init_params: dict, version: int = 4) -> tuple[bool, Optional[str]] | tuple[bool, str]:
        CAPTCHA_TYPE_MAP = {
            "https://api.capsolver.com": "AntiTurnstileTaskProxyLess",
            "https://api.capmonster.cloud": "GeeTestTask",
        }

        captcha_type = CAPTCHA_TYPE_MAP.get(self.base_url, "TurnstileTaskProxyless")

        captcha_data = {
            "clientKey": self.api_key,
            "task": {
                "type": captcha_type,
                "websiteURL": page_url,
                "gt": gt,
                "challenge": challenge,
                "version": version,
                "initParameters": init_params
            }
        }

        # challenge data not required for V4 Capmonster GeeTestTask - removed
        if captcha_type == "GeeTestTask": 
            captcha_data["task"].pop("challenge", None)

        if self.soft_id is not None:
            captcha_data["softId"] = self.soft_id

        try:
            resp = await self.client.post(f"{self.base_url}/createTask", json=captcha_data)
            resp.raise_for_status()
            data = resp.json()

            if data.get("errorId") == 0:
                task_id = data.get("taskId")
                return await self.get_captcha_result(task_id)
            return False, data.get("errorDescription", "Unknown error")

        except httpx.HTTPStatusError as err:
            return False, f"HTTP error: {err}"
        except httpx.TimeoutException:
            return False, "Request timed out"
        except Exception as err:
            return False, f"Unexpected error: {err}"

    async def get_captcha_result(self, task_id: int | str) -> tuple[bool, Optional[str]] | tuple[bool, str]:
        for _ in range(self.max_attempts):
            try:
                resp = await self.client.post(f"{self.base_url}/getTaskResult", json={"clientKey": self.api_key, "taskId": task_id})
                resp.raise_for_status()
                result = resp.json()

                if result.get("errorId") != 0:
                    return False, result.get("errorDescription", "Unknown error")

                if result.get("status") == "ready":
                    solution = result["solution"].get("token") or result["solution"].get("text") or result["solution"].get("gRecaptchaResponse")
                    return True, solution

                await asyncio.sleep(3)

            except httpx.HTTPStatusError as err:
                return False, f"HTTP error: {err}"
            except Exception as err:
                return False, f"Unexpected error: {err}"

        return False, "Max time for solving exhausted"


class AntiCaptchaSolver(CaptchaSolverBase):
    def __init__(self, api_key: str, max_attempts: int = 10):
        super().__init__(api_key, max_attempts, soft_id=1201, base_url="https://api.anti-captcha.com")


class TwoCaptchaSolver(CaptchaSolverBase):
    def __init__(self, api_key: str, max_attempts: int = 10):
        super().__init__(api_key, max_attempts, soft_id=4706, base_url="https://api.2captcha.com")


class CapmonsterSolver(CaptchaSolverBase):
    def __init__(self, api_key: str, max_attempts: int = 10):
        super().__init__(api_key, max_attempts, soft_id=None, base_url="https://api.capmonster.cloud")


class CapsolverSolver(CaptchaSolverBase):
    def __init__(self, api_key: str, max_attempts: int = 10):
        super().__init__(api_key, max_attempts, soft_id=None, base_url="https://api.capsolver.com")
