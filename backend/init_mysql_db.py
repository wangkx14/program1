import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

DB_NAME = 'warehouse'

def create_database():
    """创建数据库"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        print(f"数据库 '{DB_NAME}' 创建成功或已存在")
    except Exception as e:
        print(f"创建数据库时出错: {e}")
    finally:
        conn.close()

def create_tables():
    """创建数据表"""
    # 连接到数据库
    db_uri = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_NAME}"
    engine = create_engine(db_uri)
    
    # 使用with语句创建连接并执行SQL
    with engine.connect() as conn:
        # 创建用户表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("用户表创建成功")
        
        # 创建充电站表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS charging_stations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            location VARCHAR(200),
            status VARCHAR(20) DEFAULT 'idle',
            power_output FLOAT DEFAULT 0.0,
            efficiency FLOAT DEFAULT 100.0,
            power_rating FLOAT DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("充电站表创建成功")
        
        # 创建机器人表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS robots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            battery_level FLOAT DEFAULT 100.0,
            status VARCHAR(20) DEFAULT 'idle',
            last_charging DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("机器人表创建成功")
        
        # 创建充电订单表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS charging_orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            robot_id INT NOT NULL,
            station_id INT NOT NULL,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            status VARCHAR(20) DEFAULT 'charging',
            charge_amount FLOAT DEFAULT 0.0,
            charging_efficiency FLOAT DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (robot_id) REFERENCES robots(id),
            FOREIGN KEY (station_id) REFERENCES charging_stations(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("充电订单表创建成功")
        
        # 创建系统告警表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS system_alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time DATETIME DEFAULT CURRENT_TIMESTAMP,
            type VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("系统告警表创建成功")
        
        # 创建效率日志表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS efficiency_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            station_id INT NOT NULL,
            efficiency FLOAT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (station_id) REFERENCES charging_stations(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("效率日志表创建成功")
        
        # 创建系统设置表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS system_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("系统设置表创建成功")
        
        # 创建系统日志表
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(100) NOT NULL,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        print("系统日志表创建成功")
        
        # 提交事务
        conn.commit()

def import_data_from_excel():
    """从Excel导入数据"""
    excel_file = os.path.join('data', 'charging_system_data.xlsx')
    if not os.path.exists(excel_file):
        print(f"文件不存在: {excel_file}")
        return
    
    # 连接到数据库
    db_uri = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_NAME}"
    engine = create_engine(db_uri)
    
    # 使用原始连接来禁用外键约束
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_NAME
    )
    
    try:
        with conn.cursor() as cursor:
            # 禁用外键约束
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            conn.commit()
            print("已禁用外键约束，开始导入数据...")
            
            # 导入数据
            # 读取并导入用户数据
            try:
                df_users = pd.read_excel(excel_file, sheet_name='users')
                # 处理可能的NaN值
                df_users = df_users.where(pd.notnull(df_users), None)
                # 删除password列，因为数据库表中没有这个字段
                if 'password' in df_users.columns:
                    df_users = df_users.drop(columns=['password'])
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE users;"))
                    db_conn.commit()
                # 导入数据
                df_users.to_sql('users', engine, if_exists='append', index=False)
                print("用户数据导入成功")
            except Exception as e:
                print(f"导入用户数据时出错: {e}")
            
            # 读取并导入充电站数据
            try:
                df_stations = pd.read_excel(excel_file, sheet_name='charging_stations')
                df_stations = df_stations.where(pd.notnull(df_stations), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE charging_stations;"))
                    db_conn.commit()
                # 导入数据
                df_stations.to_sql('charging_stations', engine, if_exists='append', index=False)
                print("充电站数据导入成功")
            except Exception as e:
                print(f"导入充电站数据时出错: {e}")
            
            # 读取并导入机器人数据
            try:
                df_robots = pd.read_excel(excel_file, sheet_name='robots')
                df_robots = df_robots.where(pd.notnull(df_robots), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE robots;"))
                    db_conn.commit()
                # 导入数据
                df_robots.to_sql('robots', engine, if_exists='append', index=False)
                print("机器人数据导入成功")
            except Exception as e:
                print(f"导入机器人数据时出错: {e}")
            
            # 读取并导入充电订单数据
            try:
                df_orders = pd.read_excel(excel_file, sheet_name='charging_orders')
                df_orders = df_orders.where(pd.notnull(df_orders), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE charging_orders;"))
                    db_conn.commit()
                # 导入数据
                df_orders.to_sql('charging_orders', engine, if_exists='append', index=False)
                print("充电订单数据导入成功")
            except Exception as e:
                print(f"导入充电订单数据时出错: {e}")
            
            # 读取并导入系统告警数据
            try:
                df_alerts = pd.read_excel(excel_file, sheet_name='system_alerts')
                df_alerts = df_alerts.where(pd.notnull(df_alerts), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE system_alerts;"))
                    db_conn.commit()
                # 导入数据
                df_alerts.to_sql('system_alerts', engine, if_exists='append', index=False)
                print("系统告警数据导入成功")
            except Exception as e:
                print(f"导入系统告警数据时出错: {e}")
            
            # 读取并导入效率日志数据
            try:
                df_efficiency = pd.read_excel(excel_file, sheet_name='efficiency_logs')
                df_efficiency = df_efficiency.where(pd.notnull(df_efficiency), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE efficiency_logs;"))
                    db_conn.commit()
                # 导入数据
                df_efficiency.to_sql('efficiency_logs', engine, if_exists='append', index=False)
                print("效率日志数据导入成功")
            except Exception as e:
                print(f"导入效率日志数据时出错: {e}")
            
            # 读取并导入系统设置数据
            try:
                df_settings = pd.read_excel(excel_file, sheet_name='system_settings')
                df_settings = df_settings.where(pd.notnull(df_settings), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE system_settings;"))
                    db_conn.commit()
                # 导入数据
                df_settings.to_sql('system_settings', engine, if_exists='append', index=False)
                print("系统设置数据导入成功")
            except Exception as e:
                print(f"导入系统设置数据时出错: {e}")
            
            # 读取并导入系统日志数据
            try:
                df_logs = pd.read_excel(excel_file, sheet_name='system_logs')
                df_logs = df_logs.where(pd.notnull(df_logs), None)
                # 先删除表中的所有数据
                with engine.connect() as db_conn:
                    db_conn.execute(text("TRUNCATE TABLE system_logs;"))
                    db_conn.commit()
                # 导入数据
                df_logs.to_sql('system_logs', engine, if_exists='append', index=False)
                print("系统日志数据导入成功")
            except Exception as e:
                print(f"导入系统日志数据时出错: {e}")
            
            # 启用外键约束
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print("已启用外键约束，数据导入完成")
    except Exception as e:
        print(f"导入数据时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始初始化MySQL数据库...")
    create_database()
    create_tables()
    import_data_from_excel()
    print("MySQL数据库初始化完成！") 