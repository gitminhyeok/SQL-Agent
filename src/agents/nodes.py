import os
from typing import List
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from agents.state import AgentState
from langchain.chat_models import init_chat_model
from core import database
from core.retriever import Retriever
from utils.config import BASE_LLM_MODEL, SQL_LLM_MODEL, DB_PATH

load_dotenv()
# model_id = "gpt-4.1-mini-2025-04-14"

llm = init_chat_model(BASE_LLM_MODEL, temperature=0)
sql_llm = init_chat_model(SQL_LLM_MODEL, temperature=0)
retriever = Retriever()
retriever.index_schemas(force_refresh=False)

def retrieve_context_node(state: AgentState):
    """Search related schema """
    print("\n--- [Node] Context Retrieval ---")
    question = state["messages"][-1].content

    # TODO: src.core.retriever 모듈 연동
    
    schemas = retriever.search_schemas(question, k=10)
    golden_sqls = retriever.search_golden_sqls(question)
    print(f"get schema:\n{schemas}")
    return {
        "relevant_schemas": schemas,
        "relevant_golden_sqls": golden_sqls
    }

def generate_sql_node(state: AgentState):
    """컨텍스트 기반 SQL"생성"""
    print("\n--- [Node] SQL Generation ---")

    question = state["messages"][-1].content
    # 왜 마지막 메시지로? (이건 대화니까)

    schemas = state.get("relevant_schemas", "")

    template = """
    You are a SQLite expert. Generate a SQL query to answer the user's question.
    Use the provided schema context.

    Schema:
    {schemas}

    Question: {question}
    Return ONLY the SQL query, without markdown backticks or any explanation.
    ** Write exact sql code only based on the Schema and Question**.
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | sql_llm | StrOutputParser()
    print(f"from schema:\n{schemas}")
    try:
        response = chain.invoke({"schemas": schemas, "question": question})
        clean_sql = response.replace("```sql", "").replace("\n"," ").strip()
        print(f"clean_sql: {clean_sql}")
    except Exception as e:
        return {"error": str(e)}
    
    return {"sql_query": clean_sql, "error": None}


def execute_sql_node(state: AgentState):
    """Executor: SQL 실행"""
    print("\n--- [Node] SQL Execution ---")
    sql = state.get("sql_query")

    if not sql:
        return {"query_result": None, "error": "No SQL query generated."}

    print(f"Executing: {sql}")
    result = database.run_query(sql_query=sql, db_path=DB_PATH)
    if not isinstance(result, List):
        return {"query_result": None, "error": f"{str(result)}"}
    else:
        return {"query_result": result}
    


def analyze_result_node(state: AgentState):
    """Analyzer: SQL 결과 기반 분석 수행"""
    # [TODO]
    print("\n--- [Node] Analyzer ---")
    question = state["messages"][-1]
    sql = state.get("sql_query")
    result = state.get("query_result")
    error = state.get("error")

    if error:
        content = f"쿼리 실행 중 에러가 발생했습니다.: {error}"
    else:
        template = """
        Analyze the data and answer the user's question in Korean.

        Question: {question}
        SQL Query: {sql}
        Data:
        {result}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        response = chain.invoke({"question": question, "sql": sql, "result": result})
        content = response.content

    return {"messages": [("assistant", content)], "analysis": content}  # 왜?