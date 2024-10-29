
from typing import Optional



async def get_poll_activity_uuid(poll_uuid) -> Optional[str]:
    api_url = f"https://www.mathmatize.com/api/mm/poll_sessions/{poll_uuid}/"
    requests.get(api_url)