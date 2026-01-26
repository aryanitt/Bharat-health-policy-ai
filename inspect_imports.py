try:
    from langchain.agents import create_react_agent
    print("Found in langchain.agents")
except ImportError as e:
    print(f"Not in langchain.agents: {e}")

try:
    from langchain.agents.react.agent import create_react_agent
    print("Found in langchain.agents.react.agent")
except ImportError as e:
    print(f"Not in langchain.agents.react.agent: {e}")

try:
    from langchain.agents import initialize_agent
    print("Found initialize_agent")
except ImportError as e:
    print(f"Not in langchain.agents (initialize_agent): {e}")
