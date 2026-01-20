# SQL Extraction & Analysis Agent (with Human-in-the-Loop)

## 🚀 프로젝트 개요: Collaborative AI Data Agent
**목표**: 사용자의 자연어 질문을 SQL로 변환하고 분석하는 과정에서, **인간의 검수(Human-in-the-Loop)**와 **AI의 자동화**를 결합하여 실무에서 사용 가능한 수준의 정확도와 신뢰성을 확보하는 에이전트.

### 핵심 철학
> "완벽한 자동화는 없다. **AI가 초안을 잡고, 인간이 컨텍스트를 주입(Context Injection)하며, 실행 전 확인(Check)하는 협업 모델**을 지향한다."

---

## 🏗️ 1. 시스템 아키텍처 (LangGraph State Machine)
LangGraph의 **Cyclic Graph**와 **Persistence(Checkpoint)** 기능을 활용하여 인간이 언제든 개입할 수 있는 구조를 만듭니다.

### 주요 노드 (Nodes)
1.  **Router (분류기)**
    *   사용자의 입력이 '단순 인사', '데이터 요청', '에이전트 설정 변경'인지 분류.
2.  **Retriever (맥락 검색)**
    *   질문과 관련된 테이블 스키마, **검증된 SQL 예시(Golden SQL)**, 비즈니스 용어 정의를 Vector DB에서 검색.
3.  **Generator (SQL 작성)**
    *   검색된 맥락을 바탕으로 SQL 작성.
    *   *Self-Correction*: 문법적으로 틀린 SQL 생성 시 스스로 수정 시도.
4.  **Human Feedback (개입/승인 - HITL)**
    *   **모호성 해결**: 질문이 불명확할 경우 역질문 생성.
    *   **실행 승인**: `DROP`, `UPDATE` 등 위험 키워드가 있거나, AI의 확신(Confidence)이 낮을 경우 사용자 승인 요청.
5.  **Executor (실행)**
    *   승인된 SQL을 `sqlite3` (Read-Only 모드 권장)로 실행.
    *   에러 발생 시 에러 로그와 함께 Generator로 회귀.
6.  **Analyst (분석)**
    *   실행 결과(DataFrame)를 바탕으로 자연어 요약 또는 Python 코드를 생성하여 시각화.

---

## 📚 2. 데이터 전략: 반자동 지식 구축 (Semi-Auto Knowledge Builder)
에이전트 성능의 80%는 **"잘 정리된 메타데이터"**에서 나옵니다.

### A. Schema Curator (준비 단계)
DB를 스캔하여 **사람이 편집하기 쉬운 형태(YAML/Markdown)**의 "데이터 사전 초안"을 생성합니다.

1.  **Auto-Scan**: 테이블명, 컬럼명, 타입, Primary/Foreign Key 추출.
2.  **Sample Profiling**: 각 컬럼의 상위 5개 값, Null 비율, Distinct Count 등을 조회하여 주석에 추가.
3.  **Human Review (핵심)**: 생성된 파일에 개발자가 **비즈니스 로직**을 추가.
    *   *예: `status` 컬럼의 '1'은 '활성', '0'은 '탈퇴'라고 명시.*
    *   *예: `amount`는 '세금 포함 금액'이라고 명시.*

### B. Golden SQL Injection (Few-Shot Learning)
복잡한 통계나 조인이 필요한 질문은 스키마만으로 해결하기 어렵습니다.
*   **Golden SQL**: 자주 묻는 질문(FAQ)과 그에 대한 정답 SQL 쌍을 등록.
*   Retriever가 질문과 유사한 Golden SQL을 찾아 프롬프트에 같이 넣어주면 정확도가 비약적으로 상승.

---

## 🛠️ 3. 기술 스택 (Modern Stack)
*   **Orchestration**: LangChain v0.2+, **LangGraph** (State management & Human interrupt)
*   **LLM**: GPT-4o (Main Logic), gpt-3.5-turbo (Simple Routing)
*   **Database**: SQLite (Chinook Sample) -> 추후 PostgreSQL
*   **Vector DB**: ChromaDB (Schema & Golden SQL 저장)
*   **Validation**: Pydantic (Output Parsing)

---

## 📝 4. 개발 로드맵 (Action Plan)

### Step 1: Baseline & Environment
*   Chinook DB(SQLite) 설치.
*   LangGraph 기본 구조(State, Node) 셋업.
*   `sqlite3` Read-Only 연결 테스트.

### Step 2: Human-Centric Knowledge Builder
*   DB 정보를 읽어 **`schema_metadata.yaml`** 파일을 생성하는 스크립트 작성.
*   YAML 파일에 사람이 설명을 덧붙이면, 이를 파싱하여 ChromaDB에 저장하는 로더(Loader) 구현.

### Step 3: RAG & SQL Generation Loop
*   사용자 질문 -> 관련 테이블/Golden SQL 검색 -> SQL 생성 프롬프트 엔지니어링.
*   SQL 실행 후 에러 발생 시 재시도(Retry) 로직 구현.

### Step 4: Analyst & Interface
*   결과 데이터를 Pandas로 변환하여 요약.
*   CLI 환경에서 색깔/표를 활용한 가독성 높은 출력 구현.

---

## 📂 5. 프로젝트 폴더 구조 (Project Structure)
에이전트의 확장성과 모듈화를 위해 다음과 같은 구조로 개발을 진행한다.

```text
SQL_agent/
├── DB/                   # 원본 DB 파일 (SQLite 등)
├── metadata/             # AI 지식 베이스 (Schema Metadata, Golden SQLs)
│   ├── schema_metadata.yaml
│   └── golden_sqls.json
├── src/
│   ├── agents/           # LangGraph State Machine (Graph, Nodes, State)
│   ├── core/             # Core Logic (Database, Retriever, Knowledge Loader)
│   ├── utils/            # Utilities (Config, LLM Client)
│   └── main.py           # Entry point (CLI Interface)
├── tests/                # Unit & Integration Tests
├── .env                  # Environment Variables (API Keys)
└── requirements.txt      # Dependencies
```