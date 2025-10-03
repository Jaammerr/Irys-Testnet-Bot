from dataclasses import dataclass
from pydantic import BaseModel, PositiveInt, ConfigDict, Field, PositiveFloat

from core.onchain.wallet import Web3Wallet


class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)



class Account(BaseConfig):
    private_key: str
    wallet_address: str = ""

    def model_post_init(self, __context):
        if not self.wallet_address:
            self.wallet_address = Web3Wallet(self.private_key).wallet_address



@dataclass
class Range:
    min: int
    max: int


@dataclass
class PositiveFloatRange:
    min: PositiveFloat
    max: PositiveFloat


@dataclass
class PositiveIntRange:
    min: PositiveInt
    max: PositiveInt


@dataclass
class AttemptsAndDelaySettings:
    delay_before_start: Range
    delay_between_games: PositiveIntRange
    delay_for_game: Range
    delay_between_tasks: PositiveIntRange
    error_delay: PositiveInt

    max_faucet_attempts: PositiveInt
    max_captcha_attempts: PositiveInt
    max_games_attempts: PositiveInt
    max_nft_mint_attempts: PositiveInt
    max_tasks_attempts: PositiveInt




@dataclass
class ApplicationSettings:
    threads: PositiveInt
    database_url: str
    shuffle_accounts: bool
    check_uniqueness_of_proxies: bool
    disable_auto_proxy_change: bool



@dataclass
class CaptchaSettings:
    captcha_solver: str = "2captcha"
    solvium_captcha_api_key: str = ""
    two_captcha_api_key: str = ""
    anti_captcha_api_key: str = ""
    capsolver_api_key: str = ""
    capmonster_api_key: str = ""
    max_captcha_solving_time: PositiveInt = 60


@dataclass
class GamesSettings:
    top_up_amount: PositiveFloatRange
    games_to_play: list[str] = Field(default_factory=list)


@dataclass
class Web3Settings:
    irys_rpc_url: str
    verify_balance: bool


@dataclass
class AllInOneSettings:
    tasks_to_perform: list[str] = Field(default_factory=list)


class Config(BaseConfig):
    accounts_to_request_tokens: list[Account] = Field(default_factory=list)
    accounts_to_top_up_game_balance: list[Account] = Field(default_factory=list)
    accounts_to_play_games: list[Account] = Field(default_factory=list)
    accounts_to_mint_nft: list[Account] = Field(default_factory=list)
    accounts_for_all_in_one: list[Account] = Field(default_factory=list)
    proxies: list[str] = Field(default_factory=list)

    application_settings: ApplicationSettings
    attempts_and_delay_settings: AttemptsAndDelaySettings
    captcha_settings: CaptchaSettings
    games_settings: GamesSettings
    web3_settings: Web3Settings
    all_in_one_settings: AllInOneSettings

    module: str = ""
