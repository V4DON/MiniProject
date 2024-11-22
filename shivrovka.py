from sqlalchemy.orm import sessionmaker
from user_class import Polzovatels, Connect

session = Connect.create_connection()

users = session.query(Polzovatels).all()
for user in users:
    if not user.ppassword.startswith("$2b$"):  # Проверка, хеширован ли пароль
        user.ppassword = Polzovatels.hash_password(user.ppassword)
        session.commit()

print("Все пароли обновлены.")
