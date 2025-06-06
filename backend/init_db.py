from run import app, db
from models import User

def init_db():
    with app.app_context():
        # 创建所有表
        # db.create_all()
        
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
    init_db() 