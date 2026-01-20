import os
import yaml
import shutil
from typing import List, Dict, Optional
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import snapshot_download
from utils.config import VECTOR_STORE_DIR, EMBEDDING_MODEL_NAME, METADATA_DIR, SCHEMA_PATH, GOLDEN_SQL_PATH

# 다운로드 후 로컬 로드

class Retriever:
    def __init__(self, persist_dir: str = VECTOR_STORE_DIR, model_name: str = EMBEDDING_MODEL_NAME, metadata_dir: str = METADATA_DIR):
        self.persist_dir = persist_dir
        self.metadata_dir = metadata_dir
        self.schema_path = SCHEMA_PATH
        self.golden_sql_path = GOLDEN_SQL_PATH

        self.embedding_model = self._load_embedding_model(model_name)
        self.vector_store = None
    
    def _load_embedding_model(self, model_name: str):
        # 특정 경로로 모델 전체 다운로드
        try:
            embedding_model_path = str(self.persist_dir / model_name.replace("/", "_"))
            model = SentenceTransformer(embedding_model_path, local_files_only=True)
        except Exception as e:
            print(f"Error: {e}, getting huggingface model snapshot at path: {embedding_model_path}")
            snapshot_download(
                repo_id="dragonkue/bge-m3-ko", 
                local_dir=embedding_model_path,
            )

            # raise FileNotFoundError
        # model = SentenceTransformer(embedding_model_path, local_files_only=True)
        
        model_kwargs = {'device': 'cpu'}  # 'cuda'
        encode_kwargs = {'normalize_embeddings': True}
        print(f"model_path: {embedding_model_path}")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        

    def _load_schema_documents(self) -> List[Document]:
        """YAML에서 데이터 로드 -> Document 변환"""
        if not os.path.exists(self.schema_path):
            print(f"WARNING: Schema file not found: {self.schema_path}")
            return []
        
        with open(self.schema_path, 'r', encoding='utf-8-sig') as f:
            schema_dict = yaml.safe_load(f) or {}

        documents = []
        for table_name, info in schema_dict.items():
            desc = info.get("description", "")
            columns = info.get("columns", [])

            col_strs = []
            for c in columns:
                col_info = f"- {c['name']} ({c['type']})"
                if c.get('description'):
                    col_info += f": {c['description']}"
                if c.get('foreign_key'):
                    col_info += f" [FK: {c['foreign_key']}]"
                if c.get('samples'):
                    col_info += f": (Ex: {', '.join(c['samples'])})"
                col_strs.append(col_info)

            # col_strs = [f"- {c['name']} ({c['type']}): {c.get('description', '')}" for c in cols]  #  변경 전
            content = f"Table: {table_name}\nDescription: {desc}\nColumns:\n" + "\n".join(col_strs)
            documents.append(Document(
                page_content=content,
                metadata={"table_name": table_name}
            ))
        return documents
    
    def index_schemas(self, force_refresh: bool = False):
        """벡터 DB 생성/갱신"""
        print("Connecting Chroma Vector DB...")
        if force_refresh and os.path.exists(self.persist_dir):
            print("Refresing Vector DB...")
            self.vector_store = None
            try:
                shutil.rmtree(self.persist_dir)
            except Exception as e:
                print("Failed to delete DB folder: {e}")

        docs = self._load_schema_documents()
        if not docs:
            print(f"WARNING: No documents to index.")
            return
        self.vector_store = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding_model,
            persist_directory=self.persist_dir
        )

    def search_schemas(self, query: str, k: int = 10) -> str:
        """
        [TODO] 질문과 관련된 테이블만 검색해서 리턴해야 함.
        현재는 전체 스키마를 리턴하는 단순 버전.
        """
        print("[search_schema]: implmenting schemas searching")
        
        if not self.vector_store:
            if os.path.exists(self.persist_dir):
                self.vector_store=Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embedding_model
                )
                
        
        results = self.vector_store.similarity_search(query, k=10)
        # schemas = "\n\n".join([doc.page_content for doc in results])

        # ASIS: 여러가지 검색 중 중복을 제거하여 반환
        # TOBE: metadata keyword를 통한 search - query 중 전체 table 명에 포함된 것들로 filter 해서 추가
        # TOBE: hybrid search
        # matadata_results = self.vector_store.similarity_search(query, k=3, filter=dict["table": query])
        
        # v2
        # results = self.vector_store.max_marginal_relevance_search(
        #     query=query,
        #     k=k,
        #     fetch_k=20,
        #     lambda_mult=.7,
        #     embedding_funci ## doesn't work because of this.
        # )
        seen_tables = set()
        unique_results = []

        for doc in results:
            t_name = doc.metadata.get("table_name")
            if t_name and t_name not in seen_tables:
                seen_tables.add(t_name)
                unique_results.append(doc.page_content)
        schemas = "\n\n".join(unique_results)

        return schemas
    
    def search_golden_sqls(self, query: str) -> List[Dict]:
        """
        [TODO] 복잡한 SQL의 정답을 제공
        """
        return []
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    retriever = Retriever()
    retriever.index_schemas(force_refresh=False)

    # print()
    print(retriever.search_schemas(input("\n Test Search:")))
