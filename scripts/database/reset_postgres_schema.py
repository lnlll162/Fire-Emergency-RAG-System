#!/usr/bin/env python3
"""重置PostgreSQL数据库表结构"""
import sys
sys.path.insert(0, 'backend')

from database.user_database import UserDatabase
import psycopg2

print("=" * 60)
print("Resetting PostgreSQL Schema...")
print("=" * 60)

try:
    db = UserDatabase()
    db.initialize()
    print("\n[Step 1] Database connection established")
    
    # 删除所有表
    conn = db.pool.getconn()
    try:
        conn.set_client_encoding('UTF8')
        with conn.cursor() as cur:
            # 删除表（按依赖顺序）
            tables = ['user_login_history', 'user_sessions', 'user_permissions', 'permission_groups', 'users']
            for table in tables:
                print(f"  Dropping table: {table}")
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            # 删除函数
            cur.execute("DROP FUNCTION IF EXISTS update_updated_at() CASCADE;")
        conn.commit()
        print("[Step 2] Old tables dropped successfully")
    finally:
        db.pool.putconn(conn)
    
    # 重新创建schema
    db.execute_schema("user_schema.sql")
    print("[Step 3] Schema recreated successfully")
    
    db.close()
    print("\n" + "=" * 60)
    print("SUCCESS: PostgreSQL schema reset complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)

