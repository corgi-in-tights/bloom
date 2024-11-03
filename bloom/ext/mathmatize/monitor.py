import logging
import asyncio
import httpx
import random
from datetime import datetime, timedelta

# keyed by user id
running_instances = {}


def user_has_instance(user_id: int):
    return user_id in running_instances

def can_create_instance(max_instances: int):
    return len(running_instances) < max_instances

async def hit_endpoint(bot, user_id, session, url, duration, trigger_event, stop_event, fail_event=None, kill_event=None, freq=5, freq_range=3, logger=logging.getLogger('bloom.mathmatize')):
    last_result = None

    # hasnt reached end of duration
    end_time = datetime.now() + timedelta(minutes=duration)
    while datetime.now(bot.timezone) < end_time:
        # if stop has been triggered
        if stop_event.is_set():
            logger.info(f"Stopping instance for {url} gracefully.")
            break

        try:
            response = await session.get(url)
            if response.status_code != 200:
                logger.info(f'Failed for {user_id}!')
                if kill_event is not None:
                    await kill_event(bot, user_id, url, last_result, None)
                break

            data = response.json()
            if data and 'active_poll' in data:
                result = data['active_poll']
                if last_result and last_result != result:
                    await trigger_event(bot, user_id, url, last_result, result)
                elif fail_event is not None:
                    await fail_event(bot, user_id, url, last_result, result)

                last_result = result
            else:
                logger.info (f'Recieved response, no active poll, ending monitor for {user_id}')
                if kill_event is not None:
                    await kill_event(bot, user_id, url, last_result, result)
                break

        except Exception as e:
            print(f'Failed to fetch {url} for {user_id} due to {e}')
            break

        # wait for a random interval based on freq
        await asyncio.sleep(random.uniform(freq - freq_range, freq + freq_range))

    logger.info(f"Instance for {url} has completed or was stopped.")


async def create_monitor(bot, user_id, poll_uuid, duration, trigger_event, freq, freq_range, proxy=None, fail_event=None, kill_event=None, logger=logging.getLogger('bloom.mathmatize')):
    stop_event = asyncio.Event()
    api_url = f"https://www.mathmatize.com/api/mm/poll_sessions/{poll_uuid}/"

    logger.info(f"Creating new poll monitor for {poll_uuid} for {user_id} for {duration} minutes.")
    async with httpx.AsyncClient(proxy = proxy) as session:
        task = asyncio.create_task(hit_endpoint(
            bot, user_id, session, api_url, duration, trigger_event, stop_event, 
            freq=freq, freq_range=freq_range,
            fail_event=fail_event, kill_event=kill_event,
            logger=logger)
        )
        
        running_instances[user_id] = (task, stop_event)
        await task 


async def stop_monitor(user_id, graceful=True, logger=logging.getLogger('bloom.mathmatize')) -> bool:
    if user_id in running_instances:
        task, stop_event = running_instances[user_id]
        
        if graceful:
            # run for one last cycle
            stop_event.set()
        else:
            # nasty kill
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Poll instance for {user_id} was forcefully cancelled.")

        # Remove the instance from the dictionary
        del running_instances[user_id]
        logger.info(f"Instance for {user_id} has been stopped.")
        return True

    logger.info(f"No running instance found for {user_id}.")
    return False


async def check_user_restriction():
    pass

async def add_user_restriction():
    pass