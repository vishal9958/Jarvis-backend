# --- Start of Final Updated Code ---

# Step 1: Standard Library Imports
import asyncio
import logging
import os
import datetime
import http.server
import socketserver
import threading
import os

# Step 2: Third-Party Library Imports
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation

# Step 3: Local Application/Module Imports
from Jarvis_prompts import behavior_prompts, Reply_prompts
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open, close, folder_file
from Jarvis_file_opner import Play_file
from Jarvis_youtube_player import play_on_youtube
from jarvis_email_tool import send_email
from Jarvis_spotify_player import play_on_spotify
from Jarvis_code_writer import write_code_to_file
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool, 
    type_text_tool, press_key_tool, swipe_gesture_tool, 
    press_hotkey_tool, control_volume_tool
)

# Load environment variables from .env file
load_dotenv()


class Assistant(Agent):
    def __init__(self, instructions) -> None:
        super().__init__(
            instructions=instructions,
            tools=[
                # Media Tools
                play_on_youtube,
                play_on_spotify,
                Play_file,
                # System & App Control Tools
                open,
                close,
                folder_file,
                control_volume_tool,

                # Information Tools
                google_search,
                get_current_datetime,
                get_weather,
                
                # Productivity Tools
                write_code_to_file,
                send_email,
                
                # Keyboard & Mouse Emulation Tools
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                press_hotkey_tool,
                swipe_gesture_tool,
            ]
        )

async def entrypoint(ctx: agents.JobContext):
    
    # --- YAHAN MAIN CHANGE KIYA GAYA HAI ---
    # Agent start hone se pehle hi time ki jaankari prompt mein daal dein
    current_hour = datetime.datetime.now().hour
    
    # Ek naya dynamic prompt banayein jismein time ki jaankari ho
    # Isse LLM ko shuru se hi pata hoga ki time kya hai
    dynamic_behavior_prompt = f"""
    Current context: The current hour is {current_hour} (on a 24-hour clock).
    Use this information to provide timely greetings or context-aware responses.
    
    ---
    
    {behavior_prompts}
    
    ---
    
    Follow these initial reply instructions precisely:
    {Reply_prompts}
    """
    # --- CHANGE KHATAM ---

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Charon"
        )
    )
    
    await session.start(
        room=ctx.room,
        agent=Assistant(instructions=dynamic_behavior_prompt), # Updated prompt yahan use karein
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True 
        ),
    )

    # Yeh line `session.start` ke baad nahi chalegi, isliye isko upar prompt mein daal diya gaya hai
    # await ctx.connect() # This is generally not needed for agent sessions

def run_dummy_server():
    # Render apna PORT khud deta hai, isliye os.environ use kar rahe hain
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Dummy server running on port {PORT}")
        httpd.serve_forever()
# --- DUMMY SERVER FOR RENDER (END) ---
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
# --- End of Final Updated Code ---