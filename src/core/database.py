import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from utils.config import DB_PATH


def run_query(sql_query: str, db_path: Path = DB_PATH) -> List[Tuple]:
    # sql의 결과 List, 여러 값이 요구될 경우 tuple 리스트 형식, 추후 칼럼 명을 키로 갖는 dict형식으로 변경하면 좋을듯

    if not os.path.exists(db_path):
    # if not os.path.exists(db_path):
        print("Error: Database file not found.")
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # connection check
        cursor.execute("SELECT * FROM employees")
        tables = cursor.fetchall()

        print(f"Connection Successful. Found {len(tables)} tables:")

        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        
        print(f"executing successful. total {len(result)} row of data.")

        return result
    except Exception as e:
        print(f"executing failed. {e}")
        return e
    

if __name__ == "__main__":
    query = input("Input the test query.")
    result = run_query(sql_query=query)