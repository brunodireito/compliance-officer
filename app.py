import sys
import os
import asyncio
import inspect

# Path Fix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src import config
    from src.compliance_agent import compliance_agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
except ImportError as e:
    print(f"❌ Setup Error: {e}")
    sys.exit(1)

async def main():
    print("\n========================================")
    print("   🛡️  AI COMPLIANCE MATURITY ASSESSOR")
    print("   (Debug Mode)")
    print("========================================")
    
    APP_NAME = "agents"
    session_service = InMemorySessionService()
    runner = Runner(
        agent=compliance_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Session Setup
    user_id = "user_debug"
    session_id_str = None
    
    print("[Init] Creating session...")
    try:
        if hasattr(session_service, 'create_session'):
            session_obj = await session_service.create_session(user_id=user_id, app_name=APP_NAME)
        else:
            session_obj = await session_service.create(user_id=user_id, app_name=APP_NAME)
            
        if hasattr(session_obj, 'session_id'):
            session_id_str = session_obj.session_id
        elif hasattr(session_obj, 'id'):
            session_id_str = session_obj.id
        else:
            print(f"❌ Error: Unknown session structure: {dir(session_obj)}")
            return
            
        print(f"✅ Session active: {session_id_str}")

    except Exception as e:
        print(f"❌ Fatal Session Error: {e}")
        return

    # Input Handling
    if not os.path.exists(config.INPUT_FILENAME):
        print(f"⚠️ File '{config.INPUT_FILENAME}' not found. Creating dummy file.")
        with open(config.INPUT_FILENAME, "w") as f:
            f.write("Paste policy here...")
        return

    with open(config.INPUT_FILENAME, "r") as f:
        doc_text = f.read().strip()
    
    print(f"[Input] Loaded {len(doc_text)} chars from file.")
    print("\n[Analyzing] Agent is thinking (Trace below)...")

    # Execution
    final_output = ""
    
    try:
        msg = types.Content(role="user", parts=[types.Part(text=doc_text)])
        
        # Auto-detect argument name
        sig = inspect.signature(runner.run_async)
        arg_name = "new_message" if "new_message" in sig.parameters else "input"
        if "message" in sig.parameters: arg_name = "message"

        kwargs = {"user_id": user_id, "session_id": session_id_str}
        kwargs[arg_name] = msg

        # --- EVENT LOOP ---
        async for event in runner.run_async(**kwargs):
            # DEBUG: Print the raw event type to see what's happening
            event_type = getattr(event, "type", "unknown")
            # print(f"[DEBUG EVENT] {event_type}") # Uncomment for extreme detail

            # 1. Handle Tool Calls
            if event_type == "tool_call":
                tool_name = getattr(event, "name", "unknown")
                print(f"   ⚙️  [Tool Call] Agent is consulting: {tool_name}")

            # 2. Handle Final Response
            elif event_type == "final_response":
                text = getattr(event, "text", "")
                print(f"\n{text}")
                final_output = text

            # 3. Handle Streaming Chunks (Fallback)
            # Sometimes the model streams text in 'content' chunks instead of one final block
            elif hasattr(event, 'content') and event.content:
                content = event.content
                if hasattr(content, 'parts'):
                    for part in content.parts:
                        # Only print if it's actual text, avoiding the 'function_call' warning
                        if hasattr(part, 'text') and part.text:
                            print(part.text, end="", flush=True)
                            final_output += part.text

    except Exception as e:
        print(f"\n❌ Runtime Error: {e}")

    # Save
    if final_output:
        # Clean up output (sometimes streaming leaves artifacts)
        final_output = final_output.strip()
        with open(config.OUTPUT_FILENAME, "w") as f:
            f.write(final_output)
        print(f"\n\n✅ Saved report to: {config.OUTPUT_FILENAME}")
    else:
        print("\n⚠️ Analysis finished, but no text output was captured.")
        print("Possible cause: The agent called a tool but didn't receive a response to generate the final answer.")

if __name__ == "__main__":
    asyncio.run(main())