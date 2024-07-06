import os
import time
import requests


def clear_screen():
    # Clear command as function of OS
    command = "cls" if os.name == "nt" else "clear"
    # Execute command to clear the screen
    os.system(command)


def is_during_active_battle():
    url: str = "https://biggamesapi.io/api/activeClanBattle"
    response = requests.get(url)
    if not response.ok:
        return False

    res_data = response.json()
    if "status" in res_data and res_data["status"] == "ok":
        data = res_data["data"]
        if "configData" not in data:
            return False
        config_data = data["configData"]
        start_time: int = config_data["StartTime"]
        end_time: int = config_data["FinishTime"]
        current_time: int = int(time.time())
        is_during_active_battle = (current_time > start_time) and (
            current_time < end_time
        )
        print(f"Is during active battle: {is_during_active_battle}")
        return is_during_active_battle
    return False
