#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL配置验证脚本
快速检查PostgreSQL编码和连接配置是否正确
"""

import os
import sys
import locale
from pathlib import Path

# Windows控制台UTF-8支持
if sys.platform == 'win32':
    try:
        # 尝试设置控制台为UTF-8模式
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
        # 重新配置stdout和stderr使用UTF-8
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 设置PostgreSQL客户端编码环境变量
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PGOPTIONS'] = '--client-encoding=UTF8'

# Windows环境下设置locale
if sys.platform == 'win32':
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

import psycopg2
from datetime import datetime


def safe_print(text):
    """安全打印，处理编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果UTF-8失败，使用ASCII并替换不支持的字符
        print(text.encode('ascii', errors='replace').decode('ascii'))


def print_header(title):
    """打印标题"""
    safe_print(f"\n{'='*60}")
    safe_print(f"  {title}")
    safe_print(f"{'='*60}")


def print_result(check_name, status, message=""):
    """打印检查结果"""
    # 使用ASCII符号，更好的兼容性
    status_symbol = "[OK]" if status else "[FAIL]"
    safe_print(f"{status_symbol} {check_name}")
    if message:
        safe_print(f"   {message}")


def check_postgres_connection():
    """检查PostgreSQL连接"""
    print_header("PostgreSQL配置验证")
    safe_print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_checks_passed = True
    conn = None
    
    try:
        # 1. 检查连接
        safe_print("[*] 正在连接PostgreSQL...")
        conn_string = (
            "host=127.0.0.1 "
            "port=5432 "
            "dbname=fire_emergency "
            "user=postgres "
            "password=password "
            "sslmode=disable "
            "connect_timeout=10 "
            "client_encoding=UTF8"
        )
        
        conn = psycopg2.connect(conn_string)
        conn.set_client_encoding('UTF8')
        print_result("PostgreSQL连接", True, "成功连接到数据库")
        
        cur = conn.cursor()
        
        # 2. 检查服务器编码
        cur.execute("SHOW SERVER_ENCODING")
        server_encoding = cur.fetchone()[0]
        is_utf8 = server_encoding == 'UTF8'
        print_result("服务器编码", is_utf8, f"当前编码: {server_encoding}")
        all_checks_passed = all_checks_passed and is_utf8
        
        # 3. 检查客户端编码
        cur.execute("SHOW CLIENT_ENCODING")
        client_encoding = cur.fetchone()[0]
        is_utf8 = client_encoding == 'UTF8'
        print_result("客户端编码", is_utf8, f"当前编码: {client_encoding}")
        all_checks_passed = all_checks_passed and is_utf8
        
        # 4. 检查数据库编码
        cur.execute("""
            SELECT 
                pg_encoding_to_char(encoding) as encoding,
                datcollate,
                datctype
            FROM pg_database 
            WHERE datname='fire_emergency'
        """)
        db_info = cur.fetchone()
        db_encoding = db_info[0]
        is_utf8 = db_encoding == 'UTF8'
        print_result("数据库编码", is_utf8, f"编码: {db_encoding}, Collate: {db_info[1]}, Ctype: {db_info[2]}")
        all_checks_passed = all_checks_passed and is_utf8
        
        # 5. 测试中文存储和读取
        safe_print("\n[*] 测试中文数据...")
        test_string = "测试中文字符：消防应急救援系统"
        cur.execute("SELECT %s::text", (test_string,))
        result = cur.fetchone()[0]
        chinese_ok = result == test_string
        print_result("中文数据测试", chinese_ok, f"测试字符串: {test_string}")
        if chinese_ok:
            safe_print(f"   返回结果: {result}")
        else:
            safe_print(f"   [!] 期望: {test_string}")
            safe_print(f"   [!] 实际: {result}")
        all_checks_passed = all_checks_passed and chinese_ok
        
        # 6. 检查PostgreSQL版本
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print_result("PostgreSQL版本", True, version[:80])
        
        # 7. 检查连接数
        cur.execute("""
            SELECT count(*) as connections 
            FROM pg_stat_activity 
            WHERE datname='fire_emergency'
        """)
        connections = cur.fetchone()[0]
        print_result("当前连接数", True, f"{connections} 个活动连接")
        
        # 8. 检查数据库大小
        cur.execute("SELECT pg_size_pretty(pg_database_size('fire_emergency'))")
        db_size = cur.fetchone()[0]
        print_result("数据库大小", True, db_size)
        
        # 9. 检查必需的扩展
        safe_print("\n[*] 检查扩展...")
        cur.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname IN ('pgcrypto', 'uuid-ossp')
        """)
        extensions = cur.fetchall()
        for ext_name, ext_version in extensions:
            print_result(f"扩展 {ext_name}", True, f"版本 {ext_version}")
        
        # 10. 检查关键表
        safe_print("\n[*] 检查数据表...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_type='BASE TABLE'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        print_result("数据表", len(tables) > 0, f"找到 {len(tables)} 个表")
        if tables:
            for (table_name,) in tables:
                safe_print(f"   - {table_name}")
        
        cur.close()
        
    except psycopg2.OperationalError as e:
        print_result("PostgreSQL连接", False, f"连接失败: {str(e)}")
        safe_print("\n[!] 建议:")
        safe_print("   1. 检查PostgreSQL是否运行: docker ps | grep postgres")
        safe_print("   2. 检查端口是否可访问: netstat -ano | findstr :5432")
        safe_print("   3. 验证密码是否正确")
        safe_print("   4. 查看容器日志: docker logs fire_emergency_postgres")
        all_checks_passed = False
        
    except UnicodeDecodeError as e:
        print_result("编码测试", False, f"编码错误: {str(e)}")
        safe_print("\n[!] 建议:")
        safe_print("   1. 重建PostgreSQL容器以确保UTF-8编码")
        safe_print("   2. 查看文档: docs/postgresql_best_practices.md")
        all_checks_passed = False
        
    except Exception as e:
        print_result("验证过程", False, f"发生错误: {type(e).__name__}: {str(e)}")
        all_checks_passed = False
        
    finally:
        if conn:
            conn.close()
    
    # 总结
    print_header("验证结果")
    if all_checks_passed:
        safe_print("[OK] 所有检查通过！PostgreSQL配置正确。")
        safe_print("\n[INFO] 相关文档:")
        safe_print("   - 最佳实践: docs/postgresql_best_practices.md")
        safe_print("   - 启动指南: docs/startup_guide.md")
        return 0
    else:
        safe_print("[FAIL] 部分检查未通过，请查看上述错误信息。")
        safe_print("\n[INFO] 故障排除:")
        safe_print("   - 查看文档: docs/postgresql_best_practices.md")
        safe_print("   - 检查Docker容器: docker-compose ps")
        safe_print("   - 查看容器日志: docker logs fire_emergency_postgres")
        return 1


if __name__ == "__main__":
    try:
        exit_code = check_postgres_connection()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        safe_print("\n\n[!] 用户中断验证")
        sys.exit(130)

