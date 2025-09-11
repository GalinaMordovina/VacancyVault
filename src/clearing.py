# очистка таблиц
from src.db import _connect


con = _connect()
cur = con.cursor()
cur.execute("TRUNCATE vacancies, companies RESTART IDENTITY CASCADE;")
con.commit()
cur.close()
con.close()
