#!/usr/bin/env python3
"""
WebRTC-Enabled Agent Example

Demonstrates an agent that serves both the AI agent endpoint
and a web UI for browser-based voice interaction.

Prerequisites:
- SignalWire account with credentials
- Public URL (ngrok for development)
- Guest token from SignalWire Fabric

Run with: python webrtc-enabled-agent.py
"""

from signalwire_agents import AgentBase, AgentServer
from signalwire_agents.core.function_result import SwaigFunctionResult
from pathlib import Path
import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3000"))


class WebRTCAgent(AgentBase):
    """Agent accessible via browser WebRTC."""

    def __init__(self):
        super().__init__(
            name="webrtc-agent",
            # Optional: require authentication
            basic_auth=(
                os.getenv("SWML_BASIC_AUTH_USER"),
                os.getenv("SWML_BASIC_AUTH_PASSWORD")
            ) if os.getenv("SWML_BASIC_AUTH_USER") else None
        )

        # Voice configuration
        self.add_language("English", "en-US", "rime.spore")

        # Prompt
        self.prompt_add_section(
            "Role",
            "You are a helpful AI assistant accessible via web browser."
        )
        self.prompt_add_section(
            "Context",
            "The user is calling from a web browser using WebRTC. "
            "They can hear you and speak to you in real-time."
        )
        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Be conversational and natural",
                "Keep responses concise - this is a voice conversation",
                "Use the get_time function when asked about the time",
                "Use end_call to end the conversation when the user wants to hang up"
            ]
        )

        # AI behavior tuned for WebRTC
        self.set_params({
            "end_of_speech_timeout": 1200,  # Slightly longer for browser latency
            "attention_timeout": 30000,      # 30 seconds before "are you there?"
            "inactivity_timeout": 300000     # 5 minutes max
        })

        # Debug webhook if configured
        debug_url = os.getenv("DEBUG_WEBHOOK_URL")
        if debug_url:
            self.set_params({
                "debug_webhook_url": debug_url,
                "debug_webhook_level": int(os.getenv("DEBUG_WEBHOOK_LEVEL", "1"))
            })

    @AgentBase.tool(
        name="get_time",
        description="Get the current date and time",
        parameters={}
    )
    def get_time(self, args, raw_data):
        from datetime import datetime
        now = datetime.now()
        return SwaigFunctionResult(
            f"The current time is {now.strftime('%I:%M %p')} "
            f"on {now.strftime('%A, %B %d, %Y')}."
        )

    @AgentBase.tool(
        name="end_call",
        description="End the call when the user wants to hang up",
        parameters={}
    )
    def end_call(self, args, raw_data):
        return SwaigFunctionResult(
            "Thanks for chatting! Have a great day. Goodbye!",
            post_process=True  # Let AI finish speaking before hangup
        ).add_action("hangup", {})


def create_web_ui(web_dir: Path, guest_token: str, agent_address: str):
    """Create a simple web UI for testing."""
    web_dir.mkdir(exist_ok=True)

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent - WebRTC Demo</title>
    <script src="https://cdn.signalwire.com/libs/swrtc/2.0.0/signalwire.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin-top: 0;
            color: #333;
        }}
        .status {{
            padding: 10px 15px;
            border-radius: 6px;
            margin: 20px 0;
            font-weight: 500;
        }}
        .status.disconnected {{ background: #fee; color: #c00; }}
        .status.connecting {{ background: #fef3cd; color: #856404; }}
        .status.connected {{ background: #d4edda; color: #155724; }}
        button {{
            padding: 15px 30px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-right: 10px;
            transition: all 0.2s;
        }}
        button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        #call-btn {{
            background: #28a745;
            color: white;
        }}
        #call-btn:hover:not(:disabled) {{
            background: #218838;
        }}
        #hangup-btn {{
            background: #dc3545;
            color: white;
        }}
        #hangup-btn:hover:not(:disabled) {{
            background: #c82333;
        }}
        .info {{
            margin-top: 20px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 6px;
            font-size: 14px;
        }}
        .info code {{
            background: #dee2e6;
            padding: 2px 6px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Agent Demo</h1>

        <div id="status" class="status disconnected">
            Status: Ready to call
        </div>

        <button id="call-btn">Call Agent</button>
        <button id="hangup-btn" disabled>Hang Up</button>

        <div class="info">
            <p><strong>How it works:</strong></p>
            <p>Click "Call Agent" to connect to the AI assistant via WebRTC.
            Speak naturally and the AI will respond in real-time.</p>
            <p>Agent address: <code>{agent_address}</code></p>
        </div>
    </div>

    <script>
        // Configuration - replace with your values
        const GUEST_TOKEN = '{guest_token}';
        const AGENT_ADDRESS = '{agent_address}';

        let client = null;
        let call = null;

        const statusEl = document.getElementById('status');
        const callBtn = document.getElementById('call-btn');
        const hangupBtn = document.getElementById('hangup-btn');

        function setStatus(text, state) {{
            statusEl.textContent = 'Status: ' + text;
            statusEl.className = 'status ' + state;
        }}

        callBtn.onclick = async () => {{
            try {{
                setStatus('Connecting...', 'connecting');
                callBtn.disabled = true;

                // Connect to SignalWire
                client = await SignalWire.SignalWire({{
                    token: GUEST_TOKEN
                }});

                // Dial the agent
                call = await client.dial({{
                    to: AGENT_ADDRESS,
                    nodeId: null
                }});

                setStatus('Connected - speak now!', 'connected');
                hangupBtn.disabled = false;

                // Handle call ending
                call.on('destroy', () => {{
                    setStatus('Call ended', 'disconnected');
                    callBtn.disabled = false;
                    hangupBtn.disabled = true;
                    call = null;
                }});

            }} catch (err) {{
                console.error('Call failed:', err);
                setStatus('Failed: ' + err.message, 'disconnected');
                callBtn.disabled = false;
            }}
        }};

        hangupBtn.onclick = () => {{
            if (call) {{
                call.hangup();
            }}
        }};
    </script>
</body>
</html>'''

    (web_dir / "index.html").write_text(html_content)
    print(f"Created web UI at {web_dir / 'index.html'}")


if __name__ == "__main__":
    # Check for required config
    guest_token = os.getenv("SIGNALWIRE_GUEST_TOKEN", "YOUR_GUEST_TOKEN_HERE")
    agent_address = os.getenv("SIGNALWIRE_AGENT_ADDRESS", "/public/your-agent")

    # Create web UI
    web_dir = Path(__file__).parent / "web"
    create_web_ui(web_dir, guest_token, agent_address)

    # Create server
    server = AgentServer(host=HOST, port=PORT)

    # Register agent
    server.register(WebRTCAgent(), "/agent")

    # Serve static files (web UI)
    server.serve_static_files(str(web_dir))

    print(f"\n{'='*50}")
    print("WebRTC Agent Running!")
    print(f"{'='*50}")
    print(f"Agent endpoint: http://{HOST}:{PORT}/agent")
    print(f"Web UI: http://{HOST}:{PORT}/")
    print(f"\nTo use WebRTC:")
    print("1. Set SIGNALWIRE_GUEST_TOKEN from Fabric API")
    print("2. Set SIGNALWIRE_AGENT_ADDRESS (your agent's address)")
    print("3. Open http://localhost:3000/ in your browser")
    print(f"{'='*50}\n")

    server.run()
