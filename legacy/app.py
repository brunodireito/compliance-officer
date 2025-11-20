import os
import sys
import asyncio
import inspect

# --- 1. CONFIGURATION ---
# ⚠️ PASTE YOUR API KEY BELOW
os.environ["GEMINI_API_KEY"] = "AIzaSyAZkCxjRIAZkbFwoW9jgrSadkhawozgexo"
MODEL_NAME = "gemini-2.5-flash"

# --- 2. EMBEDDED MATURITY MODEL ---
MATURITY_MODEL_TEXT = """
TOPIC 1: Alinhamento Político e Legal A política institucional identifica o alinhamento com as diretrizes (p.e. Lei da Ciência (Decreto-Lei n.º 63/2019)) e com os requisitos das entidades financiadoras (como a Fundação para a Ciência e Tecnologia /FCT)CT e a Comissão Europeia/Horizon Europe). Conformidade com Padrões/princípios Internacionais A política institucional endossa e alinha-se com os princípios e valores centrais de CA estabelecidos em declarações internacionais relevantes (p.ex., Recomendação da UNESCO, Declaração de São Francisco (DORA) ou a Barcelona Declaration).

TOPIC 2: Publicações - Mandato e âmbito - A política define claramente o mandato de depósito (se é obrigatório ou recomendado) e o seu âmbito (a quem se aplica - ex: docentes, investigadores, alunos - e a que tipo de publicações - ex: artigos, livros, atas); Estratégia - A política específicaespecifica a estratégia de publicação (regras para a seleção de repositório, etc.); Prazos - A política define momentos para o depósito e publicação e/ou períodos de embargo; Licenciamento -  A política define o espaço de licenças de utilização e diretrizes de seleção.

Maturity Levels:

- Nível 0: Não Abordado: O requisito, dimensão ou componente não é mencionado nem implícito na política.
- Nível 1: Intencional: A política reconhece ou menciona o tópico, sem aprofundar o tema, de formamas de forma superficial, não-mandatória, ou apenas como uma declaração de princípios.
- Nível 2: Regulado: A política articula claramente o requisito, define o processo e atribui responsabilidades inequívocas.
Nível 3: Suportado: A política (ou os documentos para os quais remete diretamente) identifica os mecanismos de suporte, as infraestruturas e os serviços disponíveis para a sua execução.

"""

# --- 3. AGENT SETUP ---
print("--- Initializing Google ADK Components ---")
try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
except ImportError as e:
    print(f"❌ CRITICAL ERROR: {e}")
    sys.exit(1)

SYSTEM_PROMPT = f"""
You are an expert AI Compliance Officer.
Your goal is to evaluate a user's policy against the Maturity Model below.

Reference Data:
{MATURITY_MODEL_TEXT}

Your Task:
1. Identify the Topic.
2. Compare the input against the levels (0-3).
3. Output a Markdown report stating the Level Achieved and the Evidence.
"""

agent = Agent(
    model=MODEL_NAME,
    name="simple_compliance_agent",
    instruction=SYSTEM_PROMPT
)

# --- 4. MAIN EXECUTION ---
async def main():
    print(f"✅ Agent '{agent.name}' ready.")
    
    APP_NAME = "agents" 
    
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    
    # --- SESSION CREATION ---
    user_id = "user_test"
    session_obj = None
    
    try:
        session_obj = await session_service.create_session(user_id=user_id, app_name=APP_NAME)
    except TypeError:
        try:
            session_obj = await session_service.create_session(user_id=user_id)
        except Exception as e:
            print(f"❌ Fatal Session Creation Error: {e}")
            return

    if hasattr(session_obj, 'session_id'):
        session_id_str = session_obj.session_id
    elif hasattr(session_obj, 'id'):
        session_id_str = session_obj.id
    else:
        print(f"❌ Error: Created session object has unknown structure: {dir(session_obj)}")
        return

    # Get User Input
    print("\n" + "="*40)
    print(" Paste your policy below. Type 'GO' to finish.")
    print("="*40)
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "GO": break
        lines.append(line)
    doc_text = "\n".join(lines)

    if not doc_text.strip(): return

    print("\n[Analyzing]...")
    
    try:
        msg_content = types.Content(role="user", parts=[types.Part(text=doc_text)])

        sig = inspect.signature(runner.run_async)
        params = list(sig.parameters.keys())
        
        msg_arg = "new_message" if "new_message" in params else "input"
        if "message" in params: msg_arg = "message"
        
        run_kwargs = {
            "user_id": user_id,
            "session_id": session_id_str,
        }
        run_kwargs[msg_arg] = msg_content

        # --- FINAL FIX: CORRECT EVENT PARSING ---
        async for event in runner.run_async(**run_kwargs):
            
            # 1. Check for standard 'content' object (This is what your log showed!)
            if hasattr(event, 'content') and event.content:
                content = event.content
                # Content objects have a list of 'parts'
                if hasattr(content, 'parts'):
                    for part in content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(part.text)
            
            # 2. Fallback for other event types (Tool calls, etc)
            elif getattr(event, "type", "") == "final_response":
                 print("\n" + getattr(event, "text", ""))

    except Exception as e:
        print(f"\n❌ Runtime Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())