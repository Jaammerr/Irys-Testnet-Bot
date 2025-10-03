import asyncio

from utils import load_config, FileOperations, ProxyManager
from core.captcha import *

config = load_config()
file_operations = FileOperations()

semaphore = asyncio.Semaphore(config.application_settings.threads)
proxy_manager = ProxyManager(check_uniqueness=config.application_settings.check_uniqueness_of_proxies)

captcha_solver = SolviumCaptchaSolver(
    api_key=config.captcha_settings.solvium_captcha_api_key,
    max_attempts=config.captcha_settings.max_captcha_solving_time // 3
) if config.captcha_settings.captcha_solver == "solvium" else TwoCaptchaSolver(
    api_key=config.captcha_settings.two_captcha_api_key,
    max_attempts=config.captcha_settings.max_captcha_solving_time // 3
) if config.captcha_settings.captcha_solver == "2captcha" else AntiCaptchaSolver(
    api_key=config.captcha_settings.anti_captcha_api_key,
    max_attempts=config.captcha_settings.max_captcha_solving_time // 3
) if config.captcha_settings.captcha_solver == "anti_captcha" else CapsolverSolver(
    api_key=config.captcha_settings.capsolver_api_key,
    max_attempts=config.captcha_settings.max_captcha_solving_time // 3
) if config.captcha_settings.captcha_solver == "capsolver" else CapmonsterSolver(
    api_key=config.captcha_settings.capmonster_api_key,
    max_attempts=config.captcha_settings.max_captcha_solving_time // 3
) if config.captcha_settings.captcha_solver == "capmonster" else None
