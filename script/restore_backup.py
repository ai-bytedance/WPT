import os
import subprocess
import shutil
from datetime import datetime

# 配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_HOST = "xx.xx.xx.xx"
MYSQL_PORT = "3306"
DATABASE_NAME = "wpt"  # 需要还原的数据库名称
BACKUP_DIR = "/opt/wpt"  # 数据库和文件备份的存放目录
TARGET_APP_DIR = "/opt/app"  # 目标应用路径，假设是 /opt/app
SOURCE_STORAGE_DIR = "/wpt/storage"  # 源存储路径，假设是 /wpt/storage
STORAGE_DIR = os.path.join(TARGET_APP_DIR, "storage")  # 目标 storage 目录
BACKUP_STORAGE_DIR = os.path.join(TARGET_APP_DIR, "storage-bak")  # 存储备份的目录
MYSQL_BACKUP_FILE = f"{BACKUP_DIR}/wpt_database_backup.sql"  # MySQL 备份文件路径
DATE_FORMAT = "%Y%m%d%H%M%S"  # 时间格式
STORAGE_BACKUP_TIMESTAMP = datetime.now().strftime(DATE_FORMAT)

# 生成备份文件名
def generate_backup_filename(prefix, extension="sql"):
    timestamp = datetime.now().strftime(DATE_FORMAT)
    return f"{BACKUP_DIR}/{prefix}_{timestamp}.{extension}"

# 还原 MySQL 数据库
def restore_database():
    if not os.path.exists(MYSQL_BACKUP_FILE):
        print(f"备份文件 {MYSQL_BACKUP_FILE} 不存在，无法还原数据库！")
        return
    
    print(f"正在还原数据库 {DATABASE_NAME}... 使用备份文件 {MYSQL_BACKUP_FILE}")
    restore_command = [
        "mysql",
        "-u", MYSQL_USER,
        f"-p{MYSQL_PASSWORD}",
        "-h", MYSQL_HOST,
        "-P", MYSQL_PORT,
        DATABASE_NAME,
        "<", MYSQL_BACKUP_FILE
    ]
    
    try:
        subprocess.run(' '.join(restore_command), shell=True, check=True)
        print(f"数据库 {DATABASE_NAME} 还原完成！")
    except subprocess.CalledProcessError as e:
        print(f"数据库还原失败: {e}")

# 备份 storage 文件夹
def backup_storage():
    # 确保备份目录存在
    if not os.path.exists(BACKUP_STORAGE_DIR):
        os.makedirs(BACKUP_STORAGE_DIR)

    print(f"正在备份 {STORAGE_DIR} 到 {BACKUP_STORAGE_DIR}...")
    
    # 使用 shutil 备份 storage 目录
    backup_folder = f"{BACKUP_STORAGE_DIR}/storage_backup_{STORAGE_BACKUP_TIMESTAMP}"
    try:
        shutil.copytree(STORAGE_DIR, backup_folder)
        print(f"storage 备份完成：{backup_folder}")
    except shutil.Error as e:
        print(f"存储目录备份失败: {e}")

# 覆盖目标 storage 文件夹
def overwrite_storage():
    if os.path.exists(STORAGE_DIR):
        print(f"将 {STORAGE_DIR} 重命名为 {STORAGE_DIR}_bak")
        os.rename(STORAGE_DIR, f"{STORAGE_DIR}_bak")  # 备份原有的 storage 文件夹
    
    print(f"正在将 {SOURCE_STORAGE_DIR} 复制到 {STORAGE_DIR}...")
    try:
        shutil.copytree(SOURCE_STORAGE_DIR, STORAGE_DIR)
        print(f"{SOURCE_STORAGE_DIR} 内容已成功复制到 {STORAGE_DIR}")
    except Exception as e:
        print(f"存储目录复制失败: {e}")

# 执行恢复操作
def restore_application():
    print(f"开始恢复应用程序：{TARGET_APP_DIR}")
    backup_storage()  # 备份当前 storage
    restore_database()  # 还原数据库
    overwrite_storage()  # 替换目标 storage 文件夹
    print(f"应用程序恢复完成！目标路径：{TARGET_APP_DIR}")

if __name__ == "__main__":
    restore_application()
