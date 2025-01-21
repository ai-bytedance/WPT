import os
import subprocess
import shutil
from datetime import datetime

# 配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_HOST = "xx.xx.xx.xx"  # 目标服务器
MYSQL_PORT = "3306"
DATABASE_NAME = "wpt"
BACKUP_DIR = "/opt/wpt"
TARGET_STORAGE_DIR = "/app/storage"  # 目标存储目录

def restore_database(database_backup_path):
    """还原数据库"""
    if not os.path.exists(database_backup_path):
        print(f"错误：数据库备份文件不存在：{database_backup_path}")
        return False

    restore_command = [
        "mysql",
        "-u", MYSQL_USER,
        f"-p{MYSQL_PASSWORD}",
        "-h", MYSQL_HOST,
        "-P", MYSQL_PORT,
        "--databases", DATABASE_NAME
    ]

    print(f"正在还原数据库从 {database_backup_path}...")
    try:
        with open(database_backup_path, 'r') as f:
            subprocess.run(restore_command, stdin=f, check=True)
        print("数据库还原完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"数据库还原失败：{str(e)}")
        return False

def restore_storage(backup_folder):
    """还原存储文件"""
    if not os.path.exists(backup_folder):
        print(f"错误：存储备份目录不存在：{backup_folder}")
        return False

    print(f"正在还原存储文件从 {backup_folder} 到 {TARGET_STORAGE_DIR}...")
    try:
        # 确保目标目录存在
        os.makedirs(TARGET_STORAGE_DIR, exist_ok=True)
        
        # 复制所有文件和目录
        for item in os.listdir(backup_folder):
            src = os.path.join(backup_folder, item)
            dst = os.path.join(TARGET_STORAGE_DIR, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
                
        print("存储文件还原完成")
        return True
    except Exception as e:
        print(f"存储文件还原失败：{str(e)}")
        return False

def main():
    # 使用固定的备份文件路径
    database_backup_path = "/app/wpt/wpt_database_backup.sql"
    storage_backup_path = "/app/wpt/storage"
    
    # 检查备份文件是否存在
    if not os.path.exists(database_backup_path):
        print(f"错误：数据库备份文件不存在：{database_backup_path}")
        return
        
    if not os.path.exists(storage_backup_path):
        print(f"错误：存储备份目录不存在：{storage_backup_path}") 
        return
    
    # 执行还原操作
    if restore_database(database_backup_path):
        restore_storage(storage_backup_path)

if __name__ == "__main__":
    main()
