import os
import psycopg2

class PostgresPingService:
    """Service to ping PostgreSQL database"""

    def __init__(self):
        self.host = os.environ.get('PSQL_HOST')
        self.port = os.environ.get('PSQL_PORT', 5432)
        self.database = os.environ.get('PSQL_DATABASE')
        self.user = os.environ.get('PSQL_USER')
        self.password = os.environ.get('PSQL_PASSWORD')

        if not all([self.host, self.database, self.user, self.password]):
            raise EnvironmentError(
                "PostgreSQL credentials are not set in environment variables.")

    def run(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            tables = cur.fetchall()
            print("Tables in the public schema:")
            for table in tables:
                print(table[0])

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
