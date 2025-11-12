import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# === CONFIG ===
SHEET_ID = "19KYixXl-ki1QOYuIRqe_DnWEauhrJyhh4BBTtcA-l0g"
SHEET_NAME = "Dashboard Data"
URL = "https://docs.google.com/spreadsheets/d/19KYixXl-ki1QOYuIRqe_DnWEauhrJyhh4BBTtcA-l0g/edit?gid=1767595696#gid=1767595696"
csv_export_url = URL.replace("/edit?gid=", "/export?format=csv&gid=")
st.set_page_config(page_title="Client Sentiment Radar", layout="wide")
st.title("Client Sentiment Radar")
st.caption("Live AI-Powered Churn Insights | Auto-Refresh: 30s")

# === AUTO-REFRESH ===
placeholder = st.empty()
for _ in range(100):
    try:
        df = pd.read_csv(csv_export_url)
        df = df.dropna(subset=['Sentiment'])
        df['Churn_risk'] = pd.to_numeric(df['Churn_risk'], errors='coerce').fillna(0)

        with placeholder.container():
            col1, col2, col3 = st.columns(3)

            # PIE: Sentiment
            sentiment_counts = df['Sentiment'].value_counts()
            fig_pie = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                             color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#F59E0B'},
                             title="Sentiment Breakdown")
            col1.plotly_chart(fig_pie, use_container_width=True)

            # BAR: Top Complaints
            complaints = df[df['Sentiment'] == 'Negative']['Top_Complaint'].value_counts().head(5)
            fig_bar = px.bar(x=complaints.values, y=complaints.index, orientation='h',
                             title="Top 5 Complaints", color=complaints.values, color_continuous_scale='Reds')
            col2.plotly_chart(fig_bar, use_container_width=True)

            # GAUGE: Avg Churn Risk
            avg_risk = int(df['Churn_risk'].mean())
            fig_gauge = px.bar(x=[avg_risk], y=[""], orientation='h',
                               title=f"Avg Churn Risk: {avg_risk}%",
                               range_x=[0, 100], color=[avg_risk], color_continuous_scale='RdYlGn_r')
            col3.plotly_chart(fig_gauge, use_container_width=True)

            # TABLE
            st.subheader("Latest Reviews")
            st.dataframe(df[['Name', 'Rating', 'Feedback', 'Sentiment', 'Churn_risk', 'Risk_level']].tail(10),
                         use_container_width=True)

        time.sleep(30)
    except:
        st.error("Waiting for first data...")
        time.sleep(5)