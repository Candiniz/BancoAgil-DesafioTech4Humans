import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

llm_gemini_35_flash_lite = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.0,
    max_retries=4
)

llm_open_ai_54_mini = LLM(
    model="gpt-5.4-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    max_retries=4
)