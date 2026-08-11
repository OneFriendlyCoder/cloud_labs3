import sqlite3
import psycopg2

SQLITE_DB = "./data/shopeasy.db"

PG_HOST = "database-1.c8hca82sidjj.us-east-1.rds.amazonaws.com"
PG_PORT = 5432
PG_DATABASE = "shopeasy"
PG_USER = "postgres"
PG_PASSWORD = "password"

# ---------------------------------------------------------
# Connect to SQLite
# ---------------------------------------------------------
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# ---------------------------------------------------------
# Connect to PostgreSQL
# ---------------------------------------------------------
pg_conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
)

pg_cursor = pg_conn.cursor()

# Use the schema created by the student
pg_cursor.execute("SET search_path TO shopeasy")

# ---------------------------------------------------------
# Migrate data in dependency order
# ---------------------------------------------------------
tables = [
    "products",
    "orders",
    "order_items",
]

for table in tables:
    print(f"Migrating table: {table}")

    # Get SQLite column names
    sqlite_cursor.execute(f'PRAGMA table_info("{table}")')
    columns = [row["name"] for row in sqlite_cursor.fetchall()]

    # Read all rows from SQLite
    sqlite_cursor.execute(f'SELECT * FROM "{table}"')
    rows = sqlite_cursor.fetchall()

    if not rows:
        print("  Imported 0 rows")
        continue

    column_names = ", ".join(
        f'"{column}"' for column in columns
    )

    placeholders = ", ".join(
        ["%s"] * len(columns)
    )

    insert_query = f"""
        INSERT INTO "{table}" ({column_names})
        VALUES ({placeholders})
    """

    for row in rows:
        pg_cursor.execute(
            insert_query,
            tuple(row)
        )

    print(f"  Imported {len(rows)} rows")


# ---------------------------------------------------------
# Reset identity sequences
#
# The migration explicitly inserts SQLite IDs.
# Therefore PostgreSQL identity sequences must be moved
# after the highest imported ID.
# ---------------------------------------------------------
print("Resetting PostgreSQL identity sequences...")

for table in ["products", "orders", "order_items"]:

    pg_cursor.execute(
        f"""
        SELECT setval(
            pg_get_serial_sequence(
                'shopeasy.{table}',
                'id'
            ),
            COALESCE(
                (SELECT MAX(id) FROM shopeasy."{table}"),
                1
            ),
            EXISTS (
                SELECT 1
                FROM shopeasy."{table}"
            )
        )
        """
    )


# ---------------------------------------------------------
# Commit migration
# ---------------------------------------------------------
pg_conn.commit()

print("Migration complete!")

# ---------------------------------------------------------
# Verify counts
# ---------------------------------------------------------
print("\nPostgreSQL row counts:")

for table in tables:
    pg_cursor.execute(
        f'SELECT COUNT(*) FROM shopeasy."{table}"'
    )

    count = pg_cursor.fetchone()[0]

    print(f"  {table}: {count}")


# ---------------------------------------------------------
# Close connections
# ---------------------------------------------------------
sqlite_cursor.close()
sqlite_conn.close()

pg_cursor.close()
pg_conn.close()