"""Fix the elsewhere issue and unban an account"""
import json
import os
from typing import Any


from ... import helper, adb_handler, server_handler, tracker


def edit_cache(password: str, token: str, save_stats: dict[str, Any]) -> bool:
    """Edit the cache file in /data/data/jp.co.ponos.battlecats/files/cache/ to add the token and password"""

    data = {"password": password, "token": token}
    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")
    inquiry_code = save_stats["inquiry_code"]
    local_path = os.path.abspath(inquiry_code + ".json")

    helper.write_file_string(local_path, data_s)
    game_v = save_stats["version"]
    if game_v == "jp":
        game_v = ""
    try:
        success = adb_handler.run_adb_command(
            f'shell mv "{local_path}" "/data/data/jp.co.ponos.battlecats{game_v}/cache/{inquiry_code}.json"'
        )
    except adb_handler.ADBException:
        success = False
    os.remove(local_path)
    return success


def fix_elsewhere(save_stats: dict[str, Any], force_mi: bool = False, text: bool = True) -> dict[str, Any]:
    """Handler for fixing the elsewhere issue and unban an account"""

    helper.colored_text("Getting account password...", helper.GREEN)
    original_iq = save_stats["inquiry_code"]
    data = server_handler.check_gen_token(save_stats)
    token = data["token"]
    inquiry_code = data["inquiry_code"]
    password_refresh_data = data["password_refresh_data"]
    if token is None:
        helper.colored_text("Failed to get auth token", helper.RED)
        return save_stats
    edit_cache(password_refresh_data["password"], token, save_stats)
    if original_iq != inquiry_code or force_mi:
        item_tracker = tracker.Tracker()
        item_tracker.reset_tracker()
        server_handler.update_managed_items(
            save_stats["inquiry_code"], token, save_stats
        )
    if text:
        helper.colored_text(
            "완료!\n재생을 누르면 금지 메시지가 표시될 수 있습니다. 그럴 경우 재생을 다시 누르면 사라집니다.\n계속하려면 Enter를 누르십시오...(변경 사항을 저장해야 합니다.)",
            helper.DARK_YELLOW,
        )
        input()
    return save_stats
