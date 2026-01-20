# 🤖 SQL Agent: Human-in-the-Loop Text-to-SQL

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**SQL Agent**는 자연어 질문을 SQL 쿼리로 변환하여 데이터를 조회하고 분석하는 AI 에이전트입니다.
단순한 자동화를 넘어, **검증된 메타데이터(Schema Curator)**와 **인간의 개입(Human-in-the-Loop)**을 통해 실무 수준의 정확도와 안전성을 보장합니다.

---

## ✨ Key Features

*   **🔍 RAG 기반 SQL 생성**: 벡터 DB(ChromaDB)를 활용해 질문과 관련된 테이블 스키마와 Golden SQL(예시)을 검색하여 정확도 높은 쿼리를 생성합니다.
*   **🛡️ Human-in-the-Loop (HITL)**: 생성된 SQL을 실행하기 전, 사용자가 확인하고 승인하는 절차를 두어 `DROP`이나 잘못된 조회를 방지합니다.
*   **📚 Schema Curator**: DB 스키마를 자동으로 스캔하고, 비즈니스 로직(설명, 관계 등)을 YAML로 관리하여 LLM의 이해도를 높입니다.
*   **⚡ Local Embeddings**: 로컬 임베딩 모델(`dragonkue/bge-m3-ko`)을 사용하여 보안성과 비용 효율성을 확보했습니다.
*   **🏗️ Modular Architecture**: LangGraph 기반의 모듈형 설계로 확장 및 유지보수가 용이합니다.

---

## 📂 Project Structure

```text
SQL_agent/
├── data/                 # SQLite Database (Chinook sample)
├── metadata/             # Schema Metadata (YAML) & Golden SQLs
├── models/               # Local Embedding Models (HuggingFace)
├── vector_store/         # ChromaDB Vector Index
├── src/                  # Source Code
│   ├── agents/           # LangGraph Nodes & Workflow
│   ├── core/             # DB, Retriever, Knowledge Modules
│   └── utils/            # Configuration & Helpers
├── requirements.txt      # Dependencies
└── main.py               # Entry Point
```

---

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.12+
*   [uv](https://github.com/astral-sh/uv) (Recommended) or pip
*   OpenAI API Key

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/gitminhyeok/SQL-Agent.git
cd SQL-Agent

# Create virtual environment & Install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:

```ini
OPENAI_API_KEY=sk-proj-...
```

### 4. Database Setup (Initial)
DB 스키마를 스캔하고 메타데이터를 생성합니다.

```bash
python -m src.core.knowledge
```

벡터 DB 인덱스를 생성합니다.

```bash
python -m src.core.retriever
```

### 5. Run Agent

```bash
python main.py
```

---

## 🛠️ Usage Example

```text
User (Q): Who are the top 5 customers by total spending?
🤖 Agent is thinking...

⏸️  [Confirmation Required]
Generated SQL: 
SELECT c.FirstName, c.LastName, SUM(i.Total) as TotalSpending
FROM customers c
JOIN invoices i ON c.CustomerId = i.CustomerId
GROUP BY c.CustomerId
ORDER BY TotalSpending DESC
LIMIT 5;

Run this SQL? (y/n): y

Running...
💡 Analysis:
가장 많은 지출을 한 상위 5명의 고객은 Helena Holy, Richard Cunningham... 입니다.
```

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
