import sys
import os
import sqlite3
import shutil
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), 'lost_found.db')
SQL_EXPORT_FILE = os.path.join(os.path.dirname(__file__), 'database.sql')
SCHEMA_EXPORT_FILE = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_connection():
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        sys.exit(1)
    return sqlite3.connect(DB_FILE)

def show_status():
    print("===============================================================")
    print("  CampusConnect - SQLite Database Health & Status Report")
    print("  VSIT (Vidyalankar School of Information Technology)")
    print("===============================================================")
    if not os.path.exists(DB_FILE):
        print(f"Database file does not exist: {DB_FILE}")
        return
    
    size_kb = os.path.getsize(DB_FILE) / 1024
    print(f"Database File:     {os.path.abspath(DB_FILE)}")
    print(f"File Size:         {size_kb:.2f} KB")
    print(f"SQLite Version:    {sqlite3.sqlite_version}")
    print(f"Last Modified:     {datetime.fromtimestamp(os.path.getmtime(DB_FILE))}")
    print("---------------------------------------------------------------")
    
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("PRAGMA integrity_check;")
    integrity = cur.fetchone()[0]
    print(f"Integrity Status:  {integrity.upper()}")
    print("---------------------------------------------------------------")
    print("Table Record Summary:")
    print(f"  {'Table Name':<20} | {'Row Count':<10}")
    print("  " + "-" * 33)
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall()]
    
    total_records = 0
    for tbl in tables:
        cur.execute(f"SELECT COUNT(*) FROM '{tbl}';")
        count = cur.fetchone()[0]
        total_records += count
        print(f"  {tbl:<20} | {count:<10}")
    
    print("  " + "-" * 33)
    print(f"  {'TOTAL RECORDS':<20} | {total_records:<10}")
    print("===============================================================")
    con.close()

def export_sql():
    con = get_connection()
    dump_lines = list(con.iterdump())
    header = f"""-- ===============================================================
-- CampusConnect - Smart Lost and Found Management System
-- Institution: VSIT (Vidyalankar School of Information Technology)
-- Database: SQLite3 Relational Database Schema & Demo Seed Data
-- Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ===============================================================

PRAGMA foreign_keys = ON;

"""
    full_dump = header + '\n'.join(dump_lines)
    with open(SQL_EXPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_dump)
    with open(SCHEMA_EXPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_dump)
    con.close()
    print("Database exported successfully to:")
    print(f"  - {SQL_EXPORT_FILE} ({os.path.getsize(SQL_EXPORT_FILE)} bytes)")
    print(f"  - {SCHEMA_EXPORT_FILE}")

def execute_query(sql):
    con = get_connection()
    cur = con.cursor()
    print(f"Executing Query: {sql}\n")
    try:
        cur.execute(sql)
        if cur.description is None:
            con.commit()
            print(f"Query executed. Rows affected: {cur.rowcount}")
        else:
            headers = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            if not rows:
                print("No records found.")
                return
            col_widths = [max(len(h), max((len(str(r[i])) for r in rows), default=0)) for i, h in enumerate(headers)]
            header_str = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
            sep_str = "-+-".join("-" * w for w in col_widths)
            print(header_str)
            print(sep_str)
            for r in rows:
                print(" | ".join(f"{str(v):<{w}}" for v, w in zip(r, col_widths)))
            print(f"\nTotal rows returned: {len(rows)}")
    except Exception as e:
        print(f"SQL Error: {e}")
    finally:
        con.close()

def backup_db():
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    target = os.path.join(backup_dir, f"lost_found_{timestamp}.db")
    shutil.copy2(DB_FILE, target)
    print(f"Database backed up successfully to: {target}")

def main():
    if len(sys.argv) < 2:
        print("CampusConnect Database Management Tool")
        print("Usage:")
        print("  python db_manager.py status")
        print("  python db_manager.py export")
        print("  python db_manager.py backup")
        print("  python db_manager.py query \"SELECT ...\"")
        return

    cmd = sys.argv[1].lower()
    if cmd == 'status':
        show_status()
    elif cmd == 'export':
        export_sql()
    elif cmd == 'backup':
        backup_db()
    elif cmd == 'query':
        if len(sys.argv) < 3:
            print("Please provide an SQL query in quotes.")
            sys.exit(1)
        execute_query(' '.join(sys.argv[2:]))
    else:
        print(f"Unknown command: {cmd}")

if __name__ == '__main__':
    main()
