import sqlite3
import yaml
import os
from typing import Dict, Any, List, Optional


def get_table_schema(cursor, table_name: str) -> Dict[str, Any]:
    """DB 내 단일 테이블의 스키마 추출"""
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns_info = cursor.fetchall()

    cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
    fks = cursor.fetchall()
    fk_map = {row[3]: f"{row[2]}.{row[4]}" for row in fks} # from_col -> to_table.to_col

    columns_data = []

    for col in columns_info:
        col_name = col[1]
        col_type = col[2]
        is_pk = bool(col[5])

        samples = []
        
        col_meta = {
            "name": col_name,
            "type": col_type,
            "description": "",
            "is_primary_key": is_pk,
        }

        if col_name in fk_map:
            col_meta["foreign_key"] = fk_map[col_name]
        
        columns_data.append(col_meta)
    print(f"get_table_schema processing..")


    return {
        "description": "",
        "columns": columns_data
    }



def get_full_schema(db_path: str) -> Dict[str, Any]:
    """전체 DB의 스키마를 추출"""

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    uri_path = f"file:{os.path.abspath(db_path)}?mode=ro"  # Read-Only 모드
    try:
        conn = sqlite3.connect(uri_path, uri=True)
    except sqlite3.OperationalError:
        conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    schema = {}


    #  table 들의 name 추출, sqlite 자동 생성 테이블은 제외
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            schema[table] = get_table_schema(cursor, table)
    
    finally:
        conn.close()

    return schema


def merge_schema_data(existing_tables: dict[str, Any], new_tables: dict[str, Any]) -> dict[str, Any]:
    """새로 추출한 스키마에 기존 주석을 보존하며 병합한다."""
    merged_schema = {}

    for table_name, new_info in new_tables.items():
        existing_info = existing_tables.get(table_name, {})

        if existing_info.get('description'):
            new_info["description"] = existing_info.get('description')
        
        if isinstance(existing_info, Dict):
            existing_cols = {c['name']: c for c in existing_info.get("columns", [])}
        else:
            print("Error: schema data 'existing_info' is not a dictionary")

        for new_col in new_info["columns"]:
            c_name = new_col["name"]
            if c_name in existing_cols:
                saved_desc = existing_cols[c_name.get("description")]
                if saved_desc:
                    new_col["description"] = saved_desc
    
    merged_schema[table_name] = new_info

    return merged_schema


def generate_schema_yaml(db_path: str, output_path: str):
    print(f"Scanning database: {db_path}...")
    new_schema = get_full_schema(db_path)

    final_schema_dict = new_schema
    
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8-sig') as f:
                existing_schema = yaml.safe_load(f) or {}
            final_schema_dict = merge_schema_data(existing_schema, new_schema)
        except Exception as e:
            print(f"Warning: Merge failed ({e}). Overwriting.")

    with open(output_path, "w", encoding="utf-8-sig") as f:
        yaml.dump(final_schema_dict, f, allow_unicode=True, sort_keys=False, indent=2)

    print(f"✅ Schema metadata saved to: {output_path}")

def main():
    DB_FILE = os.path.join("DB", "chinook.db")
    OUTPUT_FILE = os.path.join("metadata", "schema_metadata.yaml")
    print(os.getcwd())
    generate_schema_yaml(db_path=DB_FILE, output_path=OUTPUT_FILE)

if __name__ == "__main__":
    main()