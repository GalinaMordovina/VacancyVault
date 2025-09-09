# from dotenv import load_dotenv
# import os
# import psycopg2
#
# load_dotenv()  # Проверка! Позже удалить!
#
# def main():
#     conn = psycopg2.connect(
#         host=os.getenv("DB_HOST", "localhost"),
#         port=os.getenv("DB_PORT", "5432"),
#         dbname=os.getenv("DB_NAME", "postgres"),
#         user=os.getenv("DB_USER", "postgres"),
#         password=os.getenv("DB_PASSWORD"),
#         connect_timeout=5,
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT version(), current_user, current_database()")
#     version, user, db = cur.fetchone()
#     print("Connected OK")
#     print("Version:", version)
#     print("User:", user, "| DB:", db)
#     cur.close()
#     conn.close()
#
# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#             print("Connection FAILED:", e)

from src.config import settings
print(settings.user_agent)      # должно вывести строку без кавычек
print(settings.db_password)     # пароль как есть
