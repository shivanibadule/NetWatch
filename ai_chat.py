"""
NetWatch AI Chat Module
Handles formatting context and querying the Google Gemini LLM API.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

# Configure the Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_key_here":
    genai.configure(api_key=api_key)

# Determine the best available model
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if "models/gemini-1.5-flash" in available_models:
        model_name = "gemini-1.5-flash"
    elif "models/gemini-1.5-flash-latest" in available_models:
        model_name = "gemini-1.5-flash-latest"
    elif "models/gemini-pro" in available_models:
        model_name = "gemini-pro"
    elif available_models:
        model_name = available_models[0].replace("models/", "")
    else:
        model_name = "gemini-1.5-flash" # Fallback

    model = genai.GenerativeModel(model_name)
except Exception as e:
    model = None
    print(f"[*] Could not initialize Gemini model dynamically: {e}")

def generate_chat_response(user_query: str, recent_packets: list, recent_alerts: list) -> str:
    """
    Generates an AI response based on the user's query and the recent network context.
    """
    if not api_key or api_key == "your_key_here":
        return "Error: GEMINI_API_KEY is not set or valid in `backend/.env`. Please configure it to use the AI Chat feature."

    if not model:
        return "Error: Gemini model failed to initialize."

    # Format the dynamic context cleanly to fit inside the prompt
    context_str = "--- NetWatch System Context ---\n\n"
    
    context_str += f"Recent Alerts (last {len(recent_alerts)}):\n"
    if not recent_alerts:
        context_str += "- No recent alerts found.\n"
    for alert in recent_alerts[:15]:  # Limit arbitrarily to prevent huge token usage
        desc = alert.get("description", "Unknown Event")
        sev = str(alert.get("severity", "info")).upper()
        src = alert.get("source_ip", "N/A")
        context_str += f"- [{sev}] {desc} (Src: {src})\n"

    context_str += f"\nRecent Packets (last {len(recent_packets)}):\n"
    if not recent_packets:
        context_str += "- No recent packets logged.\n"
    for pkt in recent_packets[:10]:
        proto = pkt.get("protocol", "TCP")
        context_str += f"- {proto} from {pkt.get('src_ip')}:{pkt.get('src_port')} -> {pkt.get('dst_ip')}:{pkt.get('dst_port')} (Size: {pkt.get('size')}b)\n"
        
    context_str += "\n-------------------------------\n"

    system_prompt_str = (
        "You are NetWatch AI, an expert cybersecurity and network monitoring assistant integrated directly "
        "into the NetWatch dashboard. Your primary job is to answer user questions using the provided system "
        "context (which contains their recent network packets and security alerts).\n\n"
        "Instructions:\n"
        "1. Be succinct, professional, and clear.\n"
        "2. Directly reference the provided IP addresses, ports, or alert descriptions if applicable.\n"
        "3. If the user's question cannot be answered by the context, answer generally using your cybersecurity knowledge but state that you don't see it in the immediate context.\n"
        "4. DO NOT hallucinate packet data or alerts that are not in the context.\n"
    )
    
    # Combine strictly for text model completion
    full_prompt = f"{system_prompt_str}\n\n{context_str}\n\nUser Question: {user_query}\n\nResponse:"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to generate response from Gemini API: {str(e)}"
