from typing import TypedDict, List, Any, Dict, Optional
from langgraph.graph.message import add_messages
from langchain.agents import middleware
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """
    LangGraph 상태 관리
    - messages: 대화 히스토리
    - relevant_schemas: 검색된 테이블 스키마 (YAML/Text)
    - relevant_golden_sqls: 검색된 Few-shot 예제
    - sql_query: 생성된 SQL
    - query_result: SQL 실행 결과
    - analysis: 최종 분석 결과
    - error: 에러 메시지
    - retry_count: 재시도 횟수
    """
    relevant_schemas: Optional[str]
    relevant_golden_sqls: Optional[List[Dict]]

    question: str
    sql_query: str
    query_result: Dict[str, Any]
    analysis: str
    error: str
    retry_count: int




