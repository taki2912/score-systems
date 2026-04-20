import psycopg2
import json
import os
from datetime import datetime
from psycopg2.extras import RealDictCursor
import time

# 数据库连接
DATABASE_URL = "postgresql://postgres:lVJcxjLgMmjSNRSdhUkQENLhpIpHRoXd@nozomi.proxy.rlwy.net:55480/railway"

# 备份目录
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database(retry=3):
    """备份数据库到 JSON"""
    for attempt in range(retry):
        try:
            print(f"🔄 开始备份... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            if attempt > 0:
                print(f"   重试 {attempt}/{retry-1}")

            # 添加连接超时和重试
            conn = psycopg2.connect(
                DATABASE_URL,
                connect_timeout=10,
                options='-c statement_timeout=30000'
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            backup_data = {}
            tables = ['users', 'clubs', 'members', 'score_changes', 'view_requests']

            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                backup_data[table] = [dict(row) for row in rows]
                print(f"  ✅ {table}: {len(rows)} 条")

            cursor.close()
            conn.close()

            # 保存文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backup_{timestamp}.json"
            filepath = os.path.join(BACKUP_DIR, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)

            print(f"✅ 备份完成: {filepath}\n")

            # 清理旧备份（保留最近20个）
            cleanup_old_backups(keep=20)

            return True

        except Exception as e:
            print(f"❌ 备份失败 (尝试 {attempt+1}/{retry}): {e}")
            if attempt < retry - 1:
                time.sleep(5)  # 等待5秒后重试
            else:
                print("❌ 所有重试均失败，可能是网络问题或数据库不可用\n")
                return False

def cleanup_old_backups(keep=20):
    """清理旧备份"""
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_') and f.endswith('.json')])
    if len(backups) > keep:
        for old_backup in backups[:-keep]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))
            print(f"🗑️  删除旧备份: {old_backup}")

if __name__ == "__main__":
    backup_database()
