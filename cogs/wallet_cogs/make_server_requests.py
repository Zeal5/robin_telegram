import requests
from typing import Awaitable, Dict, Union
from pydantic import BaseModel


async def get_token_balance_server_request(
    url: str, tg_id: int, _token_address: str = None
) -> Awaitable[Dict[str, Union[str, float] | str]]:
    """Takes in bakend url for FastAPI endpoint, user tg_id and token address \n
    and returns the dict with token symbol and balance or error string"""
    print(f"requesting... user id {tg_id} ({type(tg_id)})")
    headers = {"Content-Type": "application/json"}
    data = {"tg_id": tg_id, "token_address": _token_address}
    if _token_address is None:
        response = requests.get(url, json=data, headers=headers)
        print(f"res eth -> {response.status_code} => {response.text}")
    else:
        response = requests.get(url, json=data, headers=headers)
        print(f"res token -> {response.status_code} => {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        return response.json()["detail"]


async def get_user_settings(
    url: str, tg_id: int
) -> Awaitable[Dict[str, Union[str, float | int]] | str]:
    pass


class User(BaseModel):
    tg_id: int


class UserSettings(User):
    slippage: float
    is_premium: bool
    is_banned: bool
    enable_notifications: bool


async def get_user_settings_server_request(url: str, tg_id: int) -> UserSettings:
    # headers = {"Content-Type": "application/json"}
    data = {'tg_id' : tg_id}
    res = requests.post(url,json=data)

    if res.status_code == 200:
        print(f"X {res.status_code = }")
        return res.json()
    else:
        print(f"{res.status_code = }")

    