
import streamlit as st 
from db import run_query 
st.set_page_config(page_title="Titanic Explorer", layout="wide") 
st.title("Titanic Dataset Explorer") 
page = st.sidebar.radio( 
"Navigation", 
["Dashboard", "Data Explorer", "SQL Practice", "Test"], 
)


if page == "Dashboard":
    st.header("Dashboard")

    totals = run_query("""
        SELECT COUNT(*) AS total,
               SUM(survived) AS survivors,
               ROUND(AVG(age)::numeric, 1) AS avg_age,
               ROUND(AVG(fare)::numeric, 2) AS avg_fare
        FROM passengers
    """).iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Passengers", int(totals["total"]))
    c2.metric("Survivors", int(totals["survivors"]))
    c3.metric("Average age", float(totals["avg_age"]))
    c4.metric("Average fare", float(totals["avg_fare"]))

    left, right = st.columns(2)

    with left:
        st.subheader("Passengers by class")

        by_class = run_query("""
            SELECT pclass::text AS class, COUNT(*) AS passengers
            FROM passengers
            GROUP BY pclass
            ORDER BY pclass
        """)

        st.bar_chart(by_class.set_index("class"))

    with right:
        st.subheader("Survival rate by sex (%)")

        by_sex = run_query("""
            SELECT sex,
                   ROUND(100.0 * SUM(survived) / COUNT(*), 2)
                   AS survival_percentage
            FROM passengers
            GROUP BY sex
            ORDER BY sex
        """)

        st.bar_chart(by_sex.set_index("sex"))

    st.subheader("Missing values")

    missing = run_query("""
        SELECT COUNT(*) - COUNT(age) AS missing_age,
               COUNT(*) - COUNT(embarked) AS missing_embarked,
               COUNT(*) - COUNT(cabin) AS missing_cabin
        FROM passengers
    """)

    st.dataframe(missing, hide_index=True)



elif page == "Data Explorer":
    st.header("Data Explorer")

    col1, col2, col3 = st.columns(3)

    classes = col1.multiselect(
        "Class", [1, 2, 3], default=[1, 2, 3]
    )

    sexes = col2.multiselect(
        "Sex", ["male", "female"], default=["male", "female"]
    )

    outcome = col3.selectbox(
        "Outcome", ["All", "Survived", "Did not survive"]
    )

    if not classes or not sexes:
        st.warning("Select at least one class and one sex.")

    else:
        sql = """
            SELECT passengerid, name, sex, age, pclass,
                   fare, embarked, cabin, survived
            FROM passengers
            WHERE pclass = ANY(%s) AND sex = ANY(%s)
        """

        params = [classes, sexes]

        if outcome == "Survived":
            sql += " AND survived = 1"

        elif outcome == "Did not survive":
            sql += " AND survived = 0"

        sql += " ORDER BY passengerid"

        df = run_query(sql, params)

        st.write(f"{len(df)} passengers found.")

        st.dataframe(df, hide_index=True)

        st.download_button(
            "Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="titanic_filtered.csv",
            mime="text/csv",
        )

elif page == "SQL Practice":
    st.header("SQL Practice")

    st.caption(
        "Only read-only SELECT queries are allowed. "
        "Tables: passengers, titanic_staging."
    )

    default_sql = (
        "SELECT pclass, COUNT(*) AS passengers\n"
        "FROM passengers\n"
        "GROUP BY pclass\n"
        "ORDER BY pclass;"
    )

    user_sql = st.text_area("Your query", default_sql, height=180)

    if st.button("Run query"):
        cleaned = user_sql.strip().rstrip(";").strip()

        if not cleaned.lower().startswith(("select", "with")):
            st.error("Only SELECT queries are permitted.")

        elif ";" in cleaned:
            st.error("Run one statement at a time.")

        else:
            try:
                result = run_query(cleaned)

                st.success(f"{len(result)} rows returned.")

                st.dataframe(result, hide_index=True)

            except Exception as exc:
                st.error(f"Query failed: {exc}")

import streamlit as st
import plotly.express as px
from db import run_query

# Page configuration
st.set_page_config(
    page_title="Titanic Dashboard",
    page_icon="🚢",
    layout="wide"
)

st.title("🚢 Titanic Survival Analysis Dashboard")
st.write("Explore passenger details and survival patterns.")

# Fetch data from PostgreSQL
try:
    df = run_query("""
        SELECT passengerid, name, sex, age, sibsp, parch,
               embarked, fare, pclass, survived
        FROM passengers
    """)
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

gender = st.sidebar.selectbox(
    "Select Gender",
    ["All", "male", "female"]
)

pclass = st.sidebar.selectbox(
    "Select Passenger Class",
    ["All", 1, 2, 3]
)

filtered_df = df.copy()

if gender != "All":
    filtered_df = filtered_df[filtered_df["sex"] == gender]

if pclass != "All":
    filtered_df = filtered_df[filtered_df["pclass"] == pclass]

# KPI calculations
total = len(filtered_df)
survived = int(filtered_df["survived"].sum())
not_survived = total - survived
survival_rate = (survived / total * 100) if total else 0

# KPI cards
st.subheader("Passenger Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Passengers", total)
c2.metric("Survived", survived)
c3.metric("Not Survived", not_survived)
c4.metric("Survival Rate", f"{survival_rate:.2f}%")

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Survival by Gender")
    gender_data = (
        filtered_df.groupby("sex")["survived"]
        .sum().reset_index()
    )
    fig1 = px.bar(
        gender_data,
        x="sex",
        y="survived",
        color="sex",
        title="Number of Survivors by Gender"
    )
    st.plotly_chart(fig1, width="stretch")

with right:
    st.subheader("Survival by Passenger Class")
    class_data = (
        filtered_df.groupby("pclass")["survived"]
        .sum().reset_index()
    )
    fig2 = px.bar(
        class_data,
        x="pclass",
        y="survived",
        color="pclass",
        title="Number of Survivors by Class"
    )
    st.plotly_chart(fig2, width="stretch")

left2, right2 = st.columns(2)

with left2:
    st.subheader("Passenger Age Distribution")
    age_data = filtered_df.dropna(subset=["age"])
    fig3 = px.histogram(
        age_data,
        x="age",
        nbins=20,
        title="Age Distribution"
    )
    st.plotly_chart(fig3, width="stretch")

with right2:
    st.subheader("Survival Distribution")
    survival_data = (
        filtered_df["survived"]
        .value_counts()
        .reset_index()
    )
    survival_data.columns = ["Status", "Count"]
    survival_data["Status"] = survival_data["Status"].map(
        {0: "Not Survived", 1: "Survived"}
    )
    fig4 = px.pie(
        survival_data,
        names="Status",
        values="Count",
        title="Survived vs Not Survived",
        hole=0.4
    )
    st.plotly_chart(fig4, width="stretch")

# Passenger details
st.divider()
st.subheader("Passenger Details")
st.dataframe(filtered_df, width="stretch")
