import oracledb

# ---------- Conexión a Oracle ----------
class OracleDB:
    def __init__(self, user="cine", password="CinePass2024!", host="localhost", port=1521, service="FREEPDB1"):
        self.dsn = f"{host}:{port}/{service}"
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        if self.conn:
            return
        try:
            self.conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
            self.conn.autocommit = False

            cursor = self.conn.cursor()
            cursor.execute("ALTER SESSION SET TIME_ZONE = 'America/Mexico_City'")
            cursor.close()

        except Exception as e:
            raise

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def cursor(self):
        if not self.conn:
            raise RuntimeError("No hay conexión activa a la base de datos.")
        return self.conn.cursor()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def nextval(self, seqname):
        cur = self.cursor()
        cur.execute(f"SELECT {seqname}.NEXTVAL FROM dual")
        val = cur.fetchone()[0]
        cur.close()
        return val