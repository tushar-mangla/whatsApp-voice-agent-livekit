from dotenv import load_dotenv
import os
from datetime import datetime

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)

from mcp_client import MCPServerSse
from mcp_client.agent_tools import MCPToolsIntegration


load_dotenv()

def load_voice_prompt():
    """Load the voice agent prompt from markdown file"""
    try:
        with open('voice_agent_prompt.md', 'r', encoding='utf-8') as file:
            prompt_content = file.read()
        
        # Extract the actual prompt content (remove markdown headers and formatting)
        # You can customize this parsing based on how you want to structure the prompt
        lines = prompt_content.split('\n')
        prompt_lines = []
        
        for line in lines:
            # Skip markdown headers and empty lines
            if line.startswith('#') or line.strip() == '':
                continue
            # Skip code blocks
            if line.startswith('```'):
                continue
            prompt_lines.append(line)
        
        return '\n'.join(prompt_lines)
        
    except FileNotFoundError:
        # Fallback prompt if file doesn't exist
        return """You are Alex, a professional AI voice assistant representing Small Group, 
        an AI solutions company. You help business owners automate their tasks and focus on 
        growing their business through AI solutions. Speak naturally and conversationally."""

class Assistant(Agent):
    def __init__(self) -> None:
        # Load the comprehensive prompt from the markdown file
        voice_prompt = load_voice_prompt()
        
        # Add dynamic context
        current_date = datetime.now().strftime("%B %d, %Y")
        enhanced_prompt = f"""
        CURRENT DATE: {current_date}
        CURRENT YEAR: 2025 (Always use 2025 for calendar bookings)
        
        {voice_prompt}

        CRITICAL INSTRUCTION: 
        - ALWAYS answer the user's direct questions first, completely and helpfully
        - The conversation flow is GUIDANCE only - be flexible and responsive
        - Don't force stages if the user has specific questions or concerns
        - Be conversational, not robotic
        - Build rapport naturally rather than following a rigid script
        
        VOICE INTERACTION REMINDERS:
        - You are in a voice conversation via WhatsApp
        - Speak naturally and conversationally
        - Keep responses concise (15-30 seconds max)
        - Use natural pauses and verbal confirmations
        - Ask one question at a time and wait for responses
        - Always confirm important details by repeating them back
        """
        
        super().__init__(instructions=enhanced_prompt)

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Zephyr",
            temperature=0.7,
        )
    )

    mcp_server = MCPServerSse(
        params={"url": os.environ.get("N8N_MCP_SERVER_URL")},
        cache_tools_list=True,
        name="SSE MCP SERVER"
    )

    agent = await MCPToolsIntegration.create_agent_with_tools(
        agent_class=Assistant, 
        mcp_servers=[mcp_server],
    )

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Voice-optimized greeting
    await session.generate_reply(
        instructions=load_voice_prompt()
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))