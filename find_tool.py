try:
    from langchain.tools.retriever import create_retriever_tool
    print("Found in langchain.tools.retriever")
except ImportError:
    print("Not in langchain.tools.retriever")

try:
    from langchain.tools import create_retriever_tool
    print("Found in langchain.tools")
except ImportError:
    print("Not in langchain.tools")

try:
    from langchain_core.tools import create_retriever_tool
    print("Found in langchain_core.tools")
except ImportError:
    print("Not in langchain_core.tools")
