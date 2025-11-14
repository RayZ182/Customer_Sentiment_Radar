import streamlit as st
import pandas as pd
import plotly.express as px
import time

# === CONFIG ===
SHEET_ID = "19KYixXl-ki1QOYuIRqe_DnWEauhrJyhh4BBTtcA-l0g"
GID = "1767595696"          # Processed / Dashboard Data
GID_SUMMARY = "1697643033"  # AI_Summary tab

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
SUMMARY_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_SUMMARY}"

st.set_page_config(page_title="Client Sentiment Radar", layout="wide")
st.title("Client Sentiment Radar")
st.caption("Live AI-Powered Churn Insights | Auto-Refresh: 5 Minutes")

placeholder = st.empty()

for _ in range(100):
    try:
        # === LOAD MAIN DATA ===
        df = pd.read_csv(CSV_URL)

        # === FORCE COLUMN NAMES (EXACT MATCH FROM DEBUG) ===
        expected_cols = ['Name', 'Rating', 'Feedback', 'Sentiment', 'Confidence',
                        'Top_Complaint', 'Churn_risk', 'Risk_level', 'Timestamp', 'ai_summary', 'location']
        df.columns = expected_cols[:len(df.columns)]  # Safety

        # Required columns check
        required = ['Sentiment', 'Churn_risk', 'Feedback', 'Name', 'location']
        if not all(col in df.columns for col in required):
            raise ValueError("Missing required columns")

        df = df.dropna(subset=['Sentiment'])
        df['Churn_risk'] = pd.to_numeric(df['Churn_risk'], errors='coerce').fillna(0)

        # === LOAD AI SUMMARY (Last 10) ===
        try:
            summary_df = pd.read_csv(SUMMARY_URL)
            summary_df.columns = ['positive_summary', 'negative_summary', 'churn_risk_overview']
            latest_summary = summary_df.iloc[-1]
            has_summary = True
        except:
            latest_summary = None
            has_summary = False

        with placeholder.container():
            # === AI TRIPLE SUMMARY ===
            if has_summary:
                st.success(f"**Positive:** {latest_summary['positive_summary']}")
                st.error(f"**Negative:** {latest_summary['negative_summary']}")
                st.warning(f"**Churn Risk:** {latest_summary['churn_risk_overview']}")
            else:
                st.info("**AI Summaries:** Waiting for 10+ feedbacks...")

            st.markdown("---")

            # === LATEST REVIEW ===
            latest = df.iloc[-1]
            st.info(f"**Latest:** {latest['Feedback'][:100]}... | "
                    f"**Sentiment:** {latest['Sentiment']} | "
                    f"**Risk:** {int(latest['Churn_risk'])}%")

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            # === PIE CHART ===
            sentiment_counts = df['Sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values, names=sentiment_counts.index,
                color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#F59E0B'},
                title="Sentiment", hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            col1.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

            # === BAR CHART ===
            if 'Top_Complaint' in df.columns:
                complaints = df[df['Sentiment'] == 'Negative']['Top_Complaint'].value_counts().head(5)
                if not complaints.empty:
                    fig_bar = px.bar(x=complaints.values, y=complaints.index, orientation='h',
                                     title="Top Complaints", color=complaints.values,
                                     color_continuous_scale='Reds')
                    col2.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")
                else:
                    col2.info("No complaints.", key="no_complaints")
            else:
                col2.info("No complaint data.", key="no_complaint_col")

            # === GAUGE ===
            avg_risk = int(df['Churn_risk'].mean())
            fig_gauge = px.bar(x=[avg_risk], y=[""], orientation='h',
                               title=f"Avg Risk: {avg_risk}%", range_x=[0, 100],
                               color=[avg_risk], color_continuous_scale='RdYlGn_r')
            col3.plotly_chart(fig_gauge, use_container_width=True, key="gauge_chart")

            # === TABLE ===
            st.subheader("Latest Reviews")
            cols = ['Name', 'Rating', 'Feedback', 'Sentiment', 'Churn_risk', 'Risk_level', 'location']
            styled = df[cols].tail(10).style.apply(
                lambda x: ['background: #ffcccc' if v == 'Negative' else
                           'background: #ccffcc' if v == 'Positive' else ''
                           for v in x], subset=['Sentiment']
            )
            st.dataframe(styled, use_container_width=True, key="review_table")

        time.sleep(300)

    except Exception as e:
        st.error(f"Error: {str(e)[:100]}")
        time.sleep(5)