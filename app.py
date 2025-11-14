import streamlit as st
import pandas as pd
import plotly.express as px
import time

# === CONFIG ===
SHEET_ID = "19KYixXl-ki1QOYuIRqe_DnWEauhrJyhh4BBTtcA-l0g"
SHEET_NAME = "Processed"
GID = "1767595696"          # Processed Data tab
GID_SUMMARY = "1697643033"  # AI_Summary tab

# CSV export URLs
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
SUMMARY_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_SUMMARY}"

# === PAGE CONFIG ===
st.set_page_config(page_title="Client Sentiment Radar", layout="wide")
st.title("Client Sentiment Radar")
st.caption("Live AI-Powered Churn Insights | Auto-Refresh: 30s")

# === AUTO-REFRESH LOOP ===
placeholder = st.empty()

for _ in range(100):
    try:
        # Load main feedback data
        df = pd.read_csv(CSV_URL)
        df = df.dropna(subset=['Sentiment'])
        df['Churn_risk'] = pd.to_numeric(df['Churn_risk'], errors='coerce').fillna(0)

        # Load AI summary (last 10 feedbacks)
        try:
            summary_df = pd.read_csv(SUMMARY_URL)
            latest_summary = summary_df.iloc[-1]
            has_summary = True
        except:
            latest_summary = None
            has_summary = False

        with placeholder.container():
            # === AI TRIPLE SUMMARY (Last 10 Feedbacks) ===
            if has_summary:
                st.success(f"**Positive:** {latest_summary['positive_summary']}")
                st.error(f"**Negative:** {latest_summary['negative_summary']}")
                st.warning(f"**Churn Risk:** {latest_summary['churn_risk_overview']}")
            else:
                st.info("**AI Summaries:** Waiting for 10+ feedbacks...")

            st.markdown("---")

            # === LATEST FEEDBACK SUMMARY (Single) ===
            latest_feedback = df.iloc[-1]
            st.info(f"**Latest Review:** {latest_feedback['Feedback'][:100]}... | "
                    f"**Sentiment:** {latest_feedback['Sentiment']} | "
                    f"**Churn Risk:** {int(latest_feedback['Churn_risk'])}%")

            st.markdown("---")

            # === 3-COLUMN CHARTS ===
            col1, col2, col3 = st.columns(3)

            # PIE: Sentiment
            sentiment_counts = df['Sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#F59E0B'},
                title="Sentiment Breakdown",
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            col1.plotly_chart(fig_pie, use_container_width=True)

            # BAR: Top Complaints
            complaints = df[df['Sentiment'] == 'Negative']['Top_Complaint'].value_counts().head(5)
            if not complaints.empty:
                fig_bar = px.bar(
                    x=complaints.values, y=complaints.index, orientation='h',
                    title="Top 5 Complaints",
                    color=complaints.values, color_continuous_scale='Reds'
                )
                fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
                col2.plotly_chart(fig_bar, use_container_width=True)
            else:
                col2.info("No negative feedback yet.")

            # GAUGE: Avg Churn Risk
            avg_risk = int(df['Churn_risk'].mean())
            fig_gauge = px.bar(
                x=[avg_risk], y=[""], orientation='h',
                title=f"Avg Churn Risk: {avg_risk}%",
                range_x=[0, 100], color=[avg_risk],
                color_continuous_scale=[(0, "green"), (0.7, "orange"), (1, "red")]
            )
            fig_gauge.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
            col3.plotly_chart(fig_gauge, use_container_width=True)

            # === LATEST REVIEWS TABLE ===
            st.subheader("Latest Reviews")
            display_cols = ['Name', 'Rating', 'Feedback', 'Sentiment', 'Churn_risk', 'Risk_level']
            available_cols = [col for col in display_cols if col in df.columns]
            st.dataframe(
                df[available_cols].tail(10).style.apply(
                    lambda x: ['background: #ffcccc' if v == 'Negative' else
                               'background: #ccffcc' if v == 'Positive' else ''
                               for v in x], subset=['Sentiment']
                ),
                use_container_width=True
            )

        time.sleep(30)

    except Exception as e:
        st.error(f"Connecting to data... ({type(e).__name__})")
        time.sleep(5)