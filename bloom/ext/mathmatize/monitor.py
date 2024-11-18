import asyncio
import json
import logging
import random
from datetime import UTC, datetime

import httpx

HTTP_SUCCESS_CODE = 200
REQUEST_POLL_KEY = "active_poll"

# keyed by user id
running_instances = {}

logger = logging.getLogger("bloom.mathmatize")


def user_has_instance(user_id: int):
    return user_id in running_instances


def can_create_instance(max_instances: int):
    return len(running_instances) < max_instances


async def hit_endpoint(  # noqa: PLR0913
    session,
    user_id,
    activity_url,
    api_url,
    stop_event,
    end_date,
    on_poll_change,
    on_poll_end,
    frequency,
    frange=3,
    tzone=UTC,
):
    last_obtained_uuid = None

    # hasnt reached end of duration
    while end_date > datetime.now(tzone):
        # if stop has been triggered
        if stop_event.is_set():
            logger.info("Stopping instance for %s gracefully.", api_url)
            await on_poll_end(
                user_id=user_id,
                activity_url=activity_url,
                event_date=datetime.now(tzone),
                reason="Duration ended.",
            )
            break

        try:
            response = await session.get(api_url)
            if response.status_code != HTTP_SUCCESS_CODE:
                logger.debug("Failed url %s for %s due to status code %i!", api_url, user_id, response.status_code)
            else:
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    logger.warning("Monitor %s failed to decode response due to %s", api_url, e)
                else:
                    # if data is valid
                    if data and REQUEST_POLL_KEY in data:
                        result_uuid = data[REQUEST_POLL_KEY]
                        if last_obtained_uuid and last_obtained_uuid != result_uuid:
                            await on_poll_change(
                                user_id=user_id,
                                activity_url=activity_url,
                                event_date=datetime.now(tzone),
                            )

                        last_obtained_uuid = result_uuid
                    # otherwise, end poll
                    else:
                        logger.debug(
                            "Recieved inactive response, thus poll %s has ended, ending monitor for %s",
                            api_url,
                            user_id,
                        )
                        await on_poll_end(
                            user_id=user_id,
                            activity_url=activity_url,
                            event_date=datetime.now(tzone),
                            reason="Poll is inactive, or has ended",
                        )
                        break

        except httpx.RequestError as e:
            logger.debug("Failed to fetch poll %s for %i due to %s", api_url, user_id, e)
            break

        # wait for a random interval based on freq
        await asyncio.sleep(random.uniform(frequency - frange, frequency + frange))

    if datetime.now(tzone) >= end_date:
        await on_poll_end(
            user_id=user_id,
            activity_url=activity_url,
            event_date=datetime.now(tzone),
            reason="Monitor has reached end of duration.",
        )
        logger.debug("Instance by %s ended due to duration.", user_id)

    del running_instances[user_id]
    logger.info("Instance for %s by %i has completed or was stopped.", api_url, user_id)


async def create_monitor(  # noqa: PLR0913
    user_id,
    activity_url,
    api_url,
    end_date,
    on_poll_change,
    on_poll_end,
    frequency,
    proxy=None,
    frange=0,
    tzone=UTC,
):
    stop_event = asyncio.Event()

    logger.info(
        "Creating new monitor at %s for %s until %s.", api_url, user_id, end_date.strftime("%Y-%m-%d %H:%M:%S %Z"))
    async with httpx.AsyncClient(proxy=proxy["http"]) as session:
        task = asyncio.create_task(
            hit_endpoint(
                session=session,
                user_id=user_id,
                activity_url=activity_url,
                api_url=api_url,
                stop_event=stop_event,
                end_date=end_date,
                on_poll_change=on_poll_change,
                on_poll_end=on_poll_end,
                frequency=frequency,
                frange=frange,
                tzone=tzone,
            ),
        )

        running_instances[user_id] = (task, stop_event, activity_url)
        await task


async def stop_monitor(user_id, on_poll_end, graceful=True) -> bool:  # noqa: FBT002
    if user_id in running_instances:
        task, stop_event, activity_url = running_instances[user_id]

        if graceful:
            # run for one last cycle
            stop_event.set()
        else:
            # nasty kill
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.debug("Poll instance for %s was forcefully cancelled.", user_id)

        # Remove the instance from the dictionary
        del running_instances[user_id]
        logger.info("Instance for %s has been stopped.", user_id)

        await on_poll_end(
            user_id=user_id,
            activity_url=activity_url,
            reason="Monitor stopped by user.",
        )
        return True

    logger.debug("No running instance found for %s.", user_id)
    return False
