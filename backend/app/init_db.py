from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import User, db
import os

def init_db():
    app = Flask(__name__)
    
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://whale:20020608@localhost/charging_station'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建管理员用户
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员用户创建成功！')
        else:
            print('管理员用户已存在！')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 