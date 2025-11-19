# --- Start of Updated Code ---

import os
import subprocess
import logging
import sys
import asyncio
from fuzzywuzzy import process
import webbrowser  # Yeh pehle se tha, ab iska istemal hoga

try:
    import pygetwindow as gw
except (ImportError, NotImplementedError, Exception):
    gw = None
    def function_tool(func):
        return func

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App command map (Local Applications)
APP_MAPPINGS = {
    "notepad": "notepad",
    "calculator": "calc",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "command prompt": "cmd",
    "control panel": "control",
    "settings": "start ms-settings:",
    "paint": "mspaint",
    "vs code": "C:\\Users\\user\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe", # Aapke user path ke hisab se change karein
    
}

# --- NAYA CHANGE YAHAN HAI ---
# Website command map
WEBSITE_MAPPINGS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com/",
    "gemini" : "https://gemini.google.com/",
    "netmirror": "https://net2025.cc/",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "reddit": "https://www.reddit.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    # Yahan aur bhi websites add kar sakte hain
}
# --- CHANGE KHATAM ---

# -------------------------
# Global focus utility (No changes here)
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow not installed, cannot focus window.")
        return False

    await asyncio.sleep(1.5)
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# Index files/folders (No changes here)
async def index_items(base_dirs):
    item_index = []
    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                item_index.append({"name": d, "path": os.path.join(root, d), "type": "folder"})
            for f in files:
                item_index.append({"name": f, "path": os.path.join(root, f), "type": "file"})
    logger.info(f"✅ Indexed {len(item_index)} items.")
    return item_index

async def search_item(query, index, item_type):
    filtered = [item for item in index if item["type"] == item_type]
    choices = [item["name"] for item in filtered]
    if not choices:
        return None
    best_match, score = process.extractOne(query, choices)
    logger.info(f"🔍 Matched '{query}' to '{best_match}' with score {score}")
    if score > 70:
        for item in filtered:
            if item["name"] == best_match:
                return item
    return None

# File/folder actions (No changes here)
async def open_folder(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया। {e}")

async def play_file(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया।: {e}")

async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder create हो गया।: {path}"
    except Exception as e:
        return f"❌ फ़ाइल create करने में error आया।: {e}"

async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return f"✅ नाम बदलकर {new_path} कर दिया गया।"
    except Exception as e:
        return f"❌ नाम बदलना fail हो गया: {e}"

async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path) # Note: rmdir only works on empty folders
        else:
            os.remove(path)
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete नहीं हुआ।: {e}"

# App control
# --- NAYA CHANGE YAHAN HAI ---
@function_tool
async def open(app_title: str) -> str:
    """Opens a local application or a website."""
    app_title = app_title.lower().strip()

    # Pehle check karein ki yeh ek website hai ya nahi
    if app_title in WEBSITE_MAPPINGS:
        url = WEBSITE_MAPPINGS[app_title]
        webbrowser.open(url)
        return f"🚀 {app_title.capitalize()} aapke browser mein khol diya hai."

    # Agar website nahi, toh local app kholne ki koshish karein
    app_command = APP_MAPPINGS.get(app_title, app_title)
    try:
        await asyncio.create_subprocess_shell(f'start "" "{app_command}"')
        focused = await focus_window(app_title)
        if focused:
            return f"🚀 App launch hua aur focus mein hai: {app_title}."
        else:
            return f"🚀 {app_title} Launch किया गया, lekin window par focus नहीं हो पाया।"
    except Exception as e:
        return f"❌ {app_title} Launch नहीं हो पाया।: {e}"
# --- CHANGE KHATAM ---

@function_tool
async def close(window_title: str) -> str:
    if not win32gui:
        return "❌ win32gui not installed, cannot close window."

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    win32gui.EnumWindows(enumHandler, None)
    return f"✅ Window band karne ka command bhej diya gaya hai: {window_title}"


# Jarvis command logic (No changes here)
@function_tool
async def folder_file(command: str) -> str:
    folders_to_index = ["C:/"]
    index = await index_items(folders_to_index)
    command_lower = command.lower()

    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        path = os.path.join("D:/", folder_name)
        return await create_folder(path)

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split("to")
        if len(parts) == 2:
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            item = await search_item(old_name, index, "folder")
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]), new_name)
                return await rename_item(item["path"], new_path)
        return "❌ rename command valid नहीं है।"

    if "delete" in command_lower:
        item_name_to_delete = command.replace("delete", "").strip()
        item = await search_item(item_name_to_delete, index, "folder") or await search_item(item_name_to_delete, index, "file")
        if item:
            return await delete_item(item["path"])
        return "❌ Delete करने के लिए item नहीं मिला।"

    if "folder" in command_lower or "open folder" in command_lower:
        folder_name_to_open = command.replace("open folder", "").replace("folder", "").strip()
        item = await search_item(folder_name_to_open, index, "folder")
        if item:
            await open_folder(item["path"])
            return f"✅ Folder opened: {item['name']}"
        return "❌ Folder नहीं मिला।."

    file_name_to_play = command.strip()
    item = await search_item(file_name_to_play, index, "file")
    if item:
        await play_file(item["path"])
        return f"✅ File opened: {item['name']}"

    return "⚠ कुछ भी match नहीं हुआ।"

# --- End of Updated Code ---