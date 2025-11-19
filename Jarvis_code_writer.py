# Jarvis_code_writer.py (Updated with a more robust safety check)
import os
import google.generativeai as genai
from livekit.agents import function_tool
import logging

# Logger setup
logger = logging.getLogger(__name__)

# Configure the Gemini API client
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")

@function_tool
async def write_code_to_file(problem_description: str, filename: str) -> str:
    """
    Generates code based on a problem description and saves it to a specified file.
    Use this tool when a user asks to write, create, or generate a script or code.
    You must ask the user for both the problem description and the filename.
    Example: "Write a python script to add two numbers and save it in a file named 'adder.py'"
    """
    logger.info(f"Received request to write code for '{problem_description}' into file '{filename}'")

    if not filename.endswith(('.py', '.txt', '.html', '.css', '.js', '.json', '.c' , '.cpp', '.java', '.go', '.swift', '.ruby', '.php', '.perl', '.bash', '.sh', '.sql', '.powershell', '.vb', '.vba',)):
        return "Sorry, please provide a valid filename with an extension like .py, .txt, etc."

    try:
        generation_config = genai.GenerationConfig(temperature=0.4)
        model = genai.GenerativeModel('gemini-pro', generation_config=generation_config)

        prompt = (
            "You are a code generation assistant. Based on the following task description, "
            "write the complete, executable code. Provide only the raw code itself, "
            "without any explanation, comments, or markdown formatting like ```python ... ```."
            "\n\nTask: "
            f"{problem_description}"
        )

        logger.info("Sending prompt to Gemini API...")
        response = await model.generate_content_async(prompt)
        logger.info("Received response from Gemini API.")

        # --- YAHAN PAR BADLAV KIYA GAYA HAI (ROBUST SAFETY CHECK) ---
        try:
            # Check 1: Prompt safety feedback
            if response.prompt_feedback.block_reason:
                reason = response.prompt_feedback.block_reason.name
                logger.error(f"Prompt was blocked by API. Reason: {reason}")
                return f"Sorry, your request was blocked by the safety filter. Reason: {reason}"

            # Check 2: Generated content safety feedback (sabse zaroori)
            if response.candidates and response.candidates[0].finish_reason != 'STOP':
                reason = response.candidates[0].finish_reason.name
                logger.error(f"Code generation was stopped. Reason: {reason}")
                return f"Sorry, I couldn't generate the code because the process was stopped. Reason: {reason}"
            
            code = response.text

        except (ValueError, IndexError):
            # Agar response mein 'text' ya 'candidates' hai hi nahi, to yeh error aayega
            logger.error(f"Invalid or empty response received from API. Full response: {response}")
            return "Sorry, I received an invalid or empty response from the AI and could not write the code."
        # --- CHECK KHATAM ---

        logger.info(f"Writing generated code to {filename}...")
        with open(filename, "w", encoding='utf-8') as f:
            f.write(code)

        logger.info(f"Successfully wrote code to {filename}.")
        return f"Okay, I have created the file '{filename}' with the code for your problem."

    except Exception as e:
        logger.error(f"An exception occurred in write_code_to_file: {e}")
        return f"Sorry, I encountered an error while writing the code: {e}"