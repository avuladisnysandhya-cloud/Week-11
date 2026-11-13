
import pandas as pd
import psycopg2

# Read your Titanic CSV
df = pd.read_csv(
    r"C:\Users\SANDHYA\Downloads\Titanic-Dataset.csv"
)

# Supabase connection details
conn = psycopg2.connect(
    host="aws-0-ap-south-1.pooler.supabase.com",
    database="postgres",
    user="postgres.ofmdaoutzrpushyjeyap",
    password="YWJ3pPSgFAK82c18",
    port=5432,
    sslmode="require"
)

try:
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO titanic_project.passengers
                (passengerid, name, sex, age, sibsp, parch,
                 embarked, ticket, fare, cabin, pclass, survived)
                VALUES (%s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s)
                ON CONFLICT (passengerid) DO NOTHING
            """, (
                int(row["PassengerId"]),
                row["Name"],
                row["Sex"],
                row["Age"] if pd.notna(row["Age"]) else None,
                int(row["SibSp"]),
                int(row["Parch"]),
                row["Embarked"] if pd.notna(row["Embarked"]) else None,
                row["Ticket"],
                row["Fare"] if pd.notna(row["Fare"]) else None,
                row["Cabin"] if pd.notna(row["Cabin"]) else None,
                int(row["Pclass"]),
                int(row["Survived"])
            ))

    conn.commit()
    print("Titanic data uploaded successfully!")

finally:
    conn.close()
