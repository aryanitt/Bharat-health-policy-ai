import os
from typing import List, Optional
from api.config import GROQ_API_KEY, LLM_MODEL, TEMPERATURE
from api.services.rag_service import RAGService
from api.models.chat import ChatMessage

class AgentService:
    @staticmethod
    def get_tools():
        from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
        from langchain_core.tools import create_retriever_tool
        
        tools = []
        
        # Wikipedia Tool
        wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                top_k_results=1,
                doc_content_chars_max=400
            )
        )
        tools.append(wiki)

        # Arxiv Tool
        arxiv = ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(
                top_k_results=1,
                doc_content_chars_max=300
            )
        )
        tools.append(arxiv)

        # RAG Tool
        retriever = RAGService.get_retriever()
        if retriever:
            retriever_tool = create_retriever_tool(
                retriever,
                "health_policy_scheme_search",
                "Search official Indian health policy PDFs like PM-JAY, NHM"
            )
            tools.append(retriever_tool)
        
        return tools

    @classmethod
    async def chat(cls, message: str, history: List[ChatMessage]) -> str:
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        from langchain_groq import ChatGroq
        
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not set")

        tools = cls.get_tools()
        
        llm = ChatGroq(
            model=LLM_MODEL,
            api_key=GROQ_API_KEY,
            temperature=TEMPERATURE
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI Health Policy Assistant for India. Always use the PDF retriever first. Explain in simple language. If information is not found, say you are unsure."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Prepare chat history
        chat_history = []
        for msg in history:
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                chat_history.append(AIMessage(content=msg.content))

        # Invoke agent
        result = agent_executor.invoke({
            "input": message,
            "chat_history": chat_history
        })
        
        return result["output"]
