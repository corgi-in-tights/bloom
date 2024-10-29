import discord
import uuid
import aiohttp
import asyncio


async def user_dms_open(user) -> bool:
    try:
        await user.send()
    except discord.HTTPException as e:
        if e.code == 50006:  # cannot send an empty message
            return True
        elif e.code == 50007:  # cannot send messages to this user
            return False
        else:
            raise


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


async def fetch_json(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                return data
            
        except aiohttp.ClientError as e:
            print(f"Request error: {e}")

        except asyncio.TimeoutError:
            print("Request timed out")

        except ValueError:
            print("Failed to parse JSON")

    return None