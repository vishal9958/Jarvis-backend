# Jarvis_youtube_player.py (Updated Code)
import pywhatkit
from livekit.agents import function_tool
import asyncio # asyncio ko import karein

@function_tool
async def play_on_youtube(video_title: str) -> str: # Yahan 'async' add kiya gaya hai
    """
    Searches for a video on YouTube and plays the first result.
    Use this to play songs, videos, or anything on YouTube.
    For example: "Play the latest song by Arijit Singh on YouTube"
    """
    try:
        # pywhatkit ek blocking function hai, isliye ise alag thread mein chalayenge
        # taaki Jarvis freeze na ho.
        await asyncio.to_thread(pywhatkit.playonyt, video_title)
        return f"Playing '{video_title}' on YouTube for you."
    except Exception as e:
        return f"Sorry, I could not play '{video_title}' on YouTube. Error: {e}"