#!/usr/bin/env python3
"""初始化PostgreSQL数据库表结构"""
import sys
sys.path.insert(0, 'backend')

from database.user_database import UserDatabase

print("=" * 60)
print("Initializing PostgreSQL Schema...")
print("=" * 60)

try:
    db = UserDatabase()
    db.initialize()
    print("\n[Step 1] Database connection established")
    
    # 执行schema初始化
    db.execute_schema("user_schema.sql")
    print("[Step 2] Schema initialized successfully")
    
    db.close()
    print("\n" + "=" * 60)
    print("SUCCESS: PostgreSQL schema created!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)

