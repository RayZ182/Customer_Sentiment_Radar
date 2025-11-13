import streamlit as st
import pandas as pd
import plotly.express as px
import time

# === CONFIG ===
SHEET_ID = "19KYixXl-ki1QOYuIRqe_DnWEauhrJyhh4BBTtcA-l0g"
SHEET_NAME = "Processed"
GID = "1767595696"  # <-- Get this from URL: gid=1767595696

# Correct CSV export URL (no edit link!)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

st.set_page_config(page_title="Client Sentiment Radar", layout="wide")
st.title("Client Sentiment Radar")
st.caption("Live AI-Powered Churn Insights | Auto-Refresh: 30s")

# === AUTO-REFRESH LOOP ===
placeholder = st.empty()

for _ in range(100):
    try:
        # Read live data
        df = pd.read_csv(CSV_URL)

        # Clean & standardize
        df = df.dropna(subset=['Sentiment'])  # lowercase
        df['Churn_risk'] = pd.to_numeric(df['Churn_risk'], errors='coerce').fillna(0)

        with placeholder.container():
            # === AI OVERALL SUMMARY (TOP BANNER) ===
            latest_summary = df['ai_summary'].iloc[
                -1] if 'ai_summary' in df.columns and not df.empty else "No summary yet."
            st.success(f"**AI Business Summary:** {latest_summary}")

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            # PIE: Sentiment
            sentiment_counts = df['Sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#F59E0B'},
                title="Sentiment Breakdown"
            )
            col1.plotly_chart(fig_pie, use_container_width=True)

            # BAR: Top Complaints
            complaints = df[df['Sentiment'] == 'Negative']['Top_Complaint'].value_counts().head(5)
            if not complaints.empty:
                fig_bar = px.bar(
                    x=complaints.values, y=complaints.index, orientation='h',
                    title="Top 5 Complaints", color=complaints.values, color_continuous_scale='Reds'
                )
                col2.plotly_chart(fig_bar, use_container_width=True)
            else:
                col2.info("No negative feedback yet.")

            # GAUGE: Avg Churn Risk
            avg_risk = int(df['Churn_risk'].mean())
            fig_gauge = px.bar(
                x=[avg_risk], y=[""], orientation='h',
                title=f"Avg Churn Risk: {avg_risk}%",
                range_x=[0, 100], color=[avg_risk], color_continuous_scale='RdYlGn_r'
            )
            col3.plotly_chart(fig_gauge, use_container_width=True)

            # TABLE: Latest Reviews
            st.subheader("Latest Reviews")
            display_cols = ['Name', 'Rating', 'Feedback', 'Sentiment', 'Churn_risk', 'Risk_level', 'ai_summary']
            available_cols = [col for col in display_cols if col in df.columns]
            st.dataframe(df[available_cols].tail(10), use_container_width=True)

        time.sleep(30)  # Refresh every 30s

    except Exception as e:
        st.error(f"Waiting for data... ({e})")
        time.sleep(5)