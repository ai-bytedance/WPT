import os
import subprocess
import shutil
from datetime import datetime

# 配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_HOST = "xx.xx.xx.xx"
MYSQL_PORT = "3306"
DATABASE_NAME = "wpt"
BACKUP_DIR = "/opt/wpt"
STORAGE_DIR = "/opt/wpt/storage"
DATE_FORMAT = "%Y%m%d%H%M%S"  # 定义时间格式

# 生成备份文件名
def generate_backup_filename(prefix, extension="sql"):
    timestamp = datetime.now().strftime(DATE_FORMAT)
    return f"{BACKUP_DIR}/{prefix}_{timestamp}.{extension}"

# 备份数据库
def backup_database():
    backup_file = generate_backup_filename("wpt_database", "sql")
    dump_command = [
        "mysqldump", 
        "-u", MYSQL_USER, 
        f"-p{MYSQL_PASSWORD}", 
        "-h", MYSQL_HOST, 
        "-P", MYSQL_PORT, 
        "--databases", DATABASE_NAME, 
        "--replace", 
        "--single-transaction", 
        "--skip-lock-tables", 
        "--routines", 
        "--triggers"
    ]
    
    print(f"正在备份数据库到 {backup_file}...")
    with open(backup_file, "w") as f:
        subprocess.run(dump_command, stdout=f)
    print(f"数据库备份完成：{backup_file}")

# 手动备份文件夹，排除 .sock 文件
def backup_directory():
    timestamp = datetime.now().strftime(DATE_FORMAT)
    backup_folder = f"{BACKUP_DIR}/storage_backup_{timestamp}"

    print(f"正在备份文件夹 {STORAGE_DIR} 到 {backup_folder}...")

    # 创建目标文件夹
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    for root, dirs, files in os.walk(STORAGE_DIR):
        # 过滤掉 .sock 文件
        files = [f for f in files if not f.endswith('.sock')]

        # 创建子目录
        for file in files:
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, STORAGE_DIR)
            dst_file = os.path.join(backup_folder, relative_path)

            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            # 复制文件
            shutil.copy2(src_file, dst_file)

    print(f"文件夹备份完成：{backup_folder}")

# 执行备份操作
def main():
    backup_database()         # 备份数据库
    backup_directory()        # 备份文件夹

if __name__ == "__main__":
    main()
