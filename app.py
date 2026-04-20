# ==========================================
# IMPORTS
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="CognitiveCeiling AI", layout="wide")

from dotenv import load_dotenv
import os
from groq import Groq   # 👈 import client

# Load .env
load_dotenv()

# Get API key
api_key = os.getenv("API_KEY")

# Create client using API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test print
print(api_key)

# Make request
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)

print(response.choices[0].message.content)

# ==========================================
# PAGE CONFIG (ONLY ONCE)
# ==========================================
st.set_page_config(
    page_title="CognitiveCeiling AI",
    page_icon="🧠",
    layout="wide"
)
# ==========================================
# GLOBAL FUNCTIONS
# ==========================================
def clean(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

def find_date(df):
    for col in df.columns:
        if "date" in col:
            return col
    return None

@st.cache_data
def load_default():
    s = clean(pd.read_csv("FactSessions.csv"))
    a = clean(pd.read_csv("FactAssessments.csv"))
    m = clean(pd.read_csv("methods.csv"))
    r = clean(pd.read_csv("resources.csv"))
    d = clean(pd.read_csv("date.csv"))
    return s, a, m, r, d

def identify_file(df):
    cols = df.columns
    if "sessionid" in cols and "duration_minutes" in cols:
        return "sessions"
    elif "sessionid" in cols and "questions_correct" in cols:
        return "assessments"
    elif "methodid" in cols:
        return "methods"
    elif "resourceid" in cols:
        return "resources"
    elif any("date" in c for c in cols):
        return "date"
    return "unknown"

def load_uploaded(files):
    data = {"sessions": None, "assessments": None, "methods": None, "resources": None, "date": None}
    for f in files:
        try:
            df = clean(pd.read_csv(f))
            t = identify_file(df)
            if t != "unknown":
                data[t] = df
        except:
            pass
    return data

# ==========================================
# SIDEBAR UPLOAD
# ==========================================
st.sidebar.title("🧠 CognitiveCeiling")

uploaded_files = st.sidebar.file_uploader(
    "Upload CSV Files",
    type=["csv"],
    accept_multiple_files=True
)

# ==========================================
# LOAD DATA
# ==========================================
if uploaded_files:
    up = load_uploaded(uploaded_files)
    s, a, m, r, d = up["sessions"], up["assessments"], up["methods"], up["resources"], up["date"]

    s_def, a_def, m_def, r_def, d_def = load_default()

    s = s if s is not None else s_def
    a = a if a is not None else a_def
    m = m if m is not None else m_def
    r = r if r is not None else r_def
    d = d if d is not None else d_def

    st.sidebar.success("✅ Using Uploaded Data")

else:
    s, a, m, r, d = load_default()
    st.sidebar.info("📊 Using Default Dataset")

# ==========================================
# DATE CLEANING + MERGE + FEATURES
# ==========================================
for df_ in [s, a, d]:
    col = find_date(df_)
    if col:
        df_[col] = pd.to_datetime(df_[col], errors="coerce")

df = s.merge(m, on="methodid", how="left") \
      .merge(r, on="resourceid", how="left") \
      .merge(a, on="sessionid", how="left")

date_col = find_date(df)
date_dim = find_date(d)

if date_col and date_dim:
    df = df.merge(d, left_on=date_col, right_on=date_dim, how="left")

df["study_hours"] = df.get("duration_minutes", 0) / 60
df["retention"] = df.get("questions_correct", 0) / df.get("questions_total", 1)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🧠 CognitiveCeiling")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 About Application", "📊 Dashboard"]
)

# ==========================================
# PAGE 1: ABOUT APPLICATION
# ==========================================
if page == "🏠 About Application":

    st.markdown("""
    <style>
    .hero {
        text-align:center;
        padding:40px;
    }
    .hero h1 {
        font-size:48px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <h1>🧠 CognitiveCeiling</h1>
        <p>Intelligent Learning Analytics System</p>
    </div>
    """, unsafe_allow_html=True)

    st.image(
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
        use_container_width=True
    )

    st.markdown("## 📌 About Application")

    st.markdown("""
    CognitiveCeiling is an advanced learning analytics dashboard designed to solve one critical problem:

    ### 🚨 Problem
    Students spend hours studying but retain very little — leading to the **illusion of competence**.

    ### 💡 Solution
    - Track **Retention vs Study Time**  
    - Detect **Passive Learning traps**  
    - Identify **Cognitive Burnout**  
    - Measure **Efficiency (Retention per Hour - RPH)**  

    ### 🎯 Goal
    Help students learn smarter, not harder.
    """)

    col1, col2, col3 = st.columns(3)

    col1.info("📉 Detect Cognitive Ceiling")
    col2.info("⚖️ Active vs Passive Learning")
    col3.info("🔥 Burnout Detection")

    col4, col5, col6 = st.columns(3)

    col4.info("📊 Smart Insights")
    col5.info("⚡ Efficiency Tracking")
    col6.info("📈 Learning Trends")

# ==========================================
# PAGE 2: DASHBOARD
# ==========================================
elif page == "📊 Dashboard":


    # ==========================================
    # CSS
    # ==========================================
    st.markdown("""
    <style>
    .stApp { background-color: #0a0d14; color: #e2e8f0; }

    .metric-card {
        background: linear-gradient(135deg, #0f1a2e, #111827);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #1e3a5f;
    }

    .metric-label { font-size: 0.7rem; color: #94a3b8; }
    .metric-value { font-size: 1.8rem; font-weight: bold; }
    .metric-sub { font-size: 0.7rem; color: #64748b; }

    .chart-box {
        background: #0f1623;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    .dashboard-title {
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(135deg,#0f1a2e,#0a0d14);
        border: 1px solid #1e3a5f;
    }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # TITLE
    # ==========================================
    st.markdown("""
    <div class='dashboard-title'>
    <h1>🧠 CognitiveCeiling AI Dashboard</h1>
    <p>Learning Intelligence • Efficiency • Burnout Detection</p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # HELPERS
    # ==========================================
    def plot(fig, key):
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, key=key)
        st.markdown("</div>", unsafe_allow_html=True)

    def kpi(label, value, sub=""):
        return f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
            <div class='metric-sub'>{sub}</div>
        </div>
        """

    def clean(df):
        df.columns = df.columns.str.strip().str.lower()
        return df

    def find_date(df):
        for col in df.columns:
            if "date" in col:
                return col
        return None

    # ==========================================
    # LOAD DATA
    # ==========================================
    @st.cache_data
    def load():
        s = clean(pd.read_csv("FactSessions.csv"))
        a = clean(pd.read_csv("FactAssessments.csv"))
        m = clean(pd.read_csv("methods.csv"))
        r = clean(pd.read_csv("resources.csv"))
        d = clean(pd.read_csv("date.csv"))

        for df_ in [s, a, d]:
            col = find_date(df_)
            if col:
                df_[col] = pd.to_datetime(df_[col], errors="coerce")

        return s, a, m, r, d

    s, a, m, r, d = load()

    # ==========================================
    # MERGE
    # ==========================================
    df = s.merge(m, on="methodid", how="left") \
        .merge(r, on="resourceid", how="left") \
        .merge(a, on="sessionid", how="left")

    date_col = find_date(df)
    date_dim = find_date(d)

    if date_col and date_dim:
        df = df.merge(d, left_on=date_col, right_on=date_dim, how="left")

    # ==========================================
    # FEATURES
    # ==========================================
    df["study_hours"] = df.get("duration_minutes", 0) / 60
    df["retention"] = df.get("questions_correct", 0) / df.get("questions_total", 1)

    # ==========================================
    # ML MODEL
    # ==========================================
    def train_model(df):
        df_model = df.copy()

        if "strategytype" in df_model.columns:
            le = LabelEncoder()
            df_model["strategy_encoded"] = le.fit_transform(df_model["strategytype"].astype(str))
        else:
            le = None
            df_model["strategy_encoded"] = 0

        X = df_model[["study_hours", "strategy_encoded"]]
        y = df_model["retention"]

        model = LinearRegression()
        model.fit(X, y)

        return model, le

    model, le = train_model(df)

    # ==========================================
    # 🔥 DYNAMIC BURNOUT SCORE
    # ==========================================
    def burnout_score_dynamic(hours, retention):
        score = 0

        if hours > 6:
            score += 50
        elif hours > 3:
            score += 30
        else:
            score += 10

        if retention < 50:
            score += 40
        elif retention < 70:
            score += 25
        else:
            score += 10

        return min(score, 100)

    # ==========================================
    # 🎯 STUDY PLAN
    # ==========================================
    def study_plan(df):
        plan = []
        avg_hours = df["study_hours"].mean()
        avg_ret = df["retention"].mean() * 100

        if avg_hours > 3:
            plan.append("⏳ Reduce session length to 1–2 hours")

        if avg_ret < 60:
            plan.append("📘 Use Active Recall & Practice Tests")

        if "strategytype" in df.columns:
            passive = df[df["strategytype"]=="Passive"]["retention"].mean()
            active = df[df["strategytype"]=="Active"]["retention"].mean()
            if passive > active:
                plan.append("🧠 Avoid passive learning")

        if avg_ret > 75:
            plan.append("🚀 Maintain current strategy")

        plan.append("🔁 Use spaced repetition (24–48 hrs)")
        return plan

    # ==========================================
    # SIDEBAR
    # ==========================================
    with st.sidebar:
        st.header("Filters")

        # SUBJECT FILTER
        if "subject" in df.columns:
            subject = st.selectbox("Subject", df["subject"].dropna().unique())
            df = df[df["subject"] == subject]

        # YEAR FILTER
        if date_col in df.columns:
            df["year"] = df[date_col].dt.year

            years = sorted(df["year"].dropna().unique())

            selected_year = st.selectbox("Select Year", years)

            df = df[df["year"] == selected_year]

    # ==========================================
    # KPI
    # ==========================================
    ret = df["retention"].mean() * 100
    hours = df["study_hours"].sum()
    rph = ret / hours if hours else 0

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi("Retention", f"{ret:.1f}%", "Learning"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Study Hours", f"{hours:.1f}", "Effort"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("RPH", f"{rph:.2f}", "Efficiency"), unsafe_allow_html=True)

    # ==========================================
    # TABS
    # ==========================================
    tabs = st.tabs([
        "📊 Summary",
        "🧠 Efficiency",
        "⚖️ Behavior",
        "🔥 Burnout",
        "🧩 Deep Dive",
        "🤖 AI Insights"
    ])
    # ==========================================
    # TAB 1 (📊 SMART SUMMARY — INSIGHT FIRST UI)
    # ==========================================
    with tabs[0]:

        st.title("📊 CognitiveCeiling Overview")
        
        # --------------------------------------
        # KPIs
        # --------------------------------------
        ret = df["retention"].mean() * 100
        hours = df["study_hours"].sum()
        rph = ret / hours if hours else 0

        if "strategytype" in df.columns:
            active_hours = df[df["strategytype"]=="Active"]["study_hours"].sum()
            passive_hours = df[df["strategytype"]=="Passive"]["study_hours"].sum()
            active_ratio = (active_hours / hours) * 100 if hours else 0
        else:
            active_ratio = 0
            passive_hours = 0

        df["rph"] = df["retention"] / df["study_hours"].replace(0, 1)

        # --------------------------------------
        # SMART INSIGHTS ENGINE
        # --------------------------------------
        st.markdown("## 🧠 Smart Learning Insights")

        def insight_box(text, color):
            st.markdown(f"""
            <div style="
                background:{color};
                padding:12px;
                border-radius:10px;
                margin-bottom:10px;
                border-left:5px solid #000;">
            {text}
            </div>
            """, unsafe_allow_html=True)

        # 1
        if ret < 60:
            insight_box("🚨 Low retention detected — your study method is ineffective.", "#7f1d1d")
        else:
            insight_box("✅ Good retention — learning is happening effectively.", "#064e3b")

        # 2
        if active_ratio < 50:
            insight_box("⚠️ Passive learning dominates — shift to active recall.", "#78350f")

        # 3
        if rph < 10:
            insight_box("⚠️ Low efficiency — you are spending time but not gaining output.", "#78350f")

        # 4
        if hours > 6 and ret < 65:
            insight_box("🔥 Burnout pattern — long hours but decreasing performance.", "#7f1d1d")

        # 5
        if df["study_hours"].mean() > 2:
            insight_box("📉 Sessions are too long — shorter sessions improve retention.", "#1e3a8a")

        # 6
        if df["rph"].std() > 5:
            insight_box("📊 Inconsistent performance — unstable focus across sessions.", "#1e3a8a")

        # 7
        if passive_hours > active_hours:
            insight_box("🎥 Too much passive input (videos/reading) vs practice.", "#78350f")

        # 8
        peak_hour = None
        if date_col in df.columns:
            df["hour"] = df[date_col].dt.hour
            peak_hour = df.groupby("hour")["retention"].mean().idxmax()
            insight_box(f"⏰ Peak performance hour: {peak_hour}:00 — study core topics here.", "#064e3b")

        # 9
        if df["retention"].max() - df["retention"].min() > 0.5:
            insight_box("📉 High performance fluctuation — consistency needs improvement.", "#1e3a8a")

        # 10
        if rph > 15:
            insight_box("🚀 High efficiency detected — you're learning smart, not hard.", "#064e3b")

        # --------------------------------------
        # VISUALS
        # --------------------------------------
        st.markdown("---")

        col1, col2 = st.columns(2)

        # 📉 Diminishing Returns
        with col1:
            st.markdown("### 📉 Diminishing Returns Curve")

            fig = px.scatter(
                df,
                x="study_hours",
                y="retention",
                color="strategytype" if "strategytype" in df else None,
                trendline="ols"
            )
            st.plotly_chart(fig, use_container_width=True, key="smart_scatter")

        # 🍩 Strategy Split
        with col2:
            st.markdown("### 🍩 Learning Strategy Split")

            if "strategytype" in df.columns:
                fig = px.pie(df, names="strategytype", hole=0.6)
                st.plotly_chart(fig, use_container_width=True, key="smart_donut")

        col3, col4 = st.columns(2)

        # 🔥 Heatmap
        with col3:
            st.markdown("### 🔥 Focus Heatmap")

            if date_col in df.columns:
                heat = df.pivot_table(
                    index=df["hour"],
                    columns="strategytype" if "strategytype" in df else None,
                    values="retention",
                    aggfunc="mean"
                )

                fig = px.imshow(heat, color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True, key="smart_heatmap")

        # ⚡ RPH Trend
        with col4:
            st.markdown("### ⚡ RPH Trend")

            fig = px.area(df, x=date_col, y="rph")
            st.plotly_chart(fig, use_container_width=True, key="smart_rph")

        # --------------------------------------
        # FINAL LINE
        # --------------------------------------
        st.markdown("---")
        st.info("💡 Smart learning beats hard learning. Optimize how you study, not just how long.")

    # ==========================================
    # TAB 2
    # ==========================================
    with tabs[1]:
            st.markdown("## 📊 Learning Efficiency ")

            col1, col2 = st.columns(2)

            # ==============================
            # RETENTION TREND (ADVANCED LINE)
            # ==============================
            with col1:
                fig1 = px.line(
                    df,
                    x=date_col,
                    y="retention",
                    markers=True,
                    title="📈 Retention Trend Over Time",
                )

                fig1.update_traces(
                    line=dict(width=3, shape="spline"),
                    marker=dict(size=8)
                )

                fig1.update_layout(
                    template="plotly_dark",
                    hovermode="x unified",
                    xaxis_title="Date",
                    yaxis_title="Retention %",
                    title_x=0.5,
                    height=400,
                )

                st.plotly_chart(fig1, use_container_width=True)

            # ==============================
            # STUDY HOURS (ADVANCED AREA)
            # ==============================
            with col2:
                fig2 = px.area(
                    df,
                    x=date_col,
                    y="study_hours",
                    title="⏳ Study Hours Distribution",
                )

                fig2.update_traces(
                    line=dict(width=2),
                )

                fig2.update_layout(
                    template="plotly_dark",
                    hovermode="x unified",
                    xaxis_title="Date",
                    yaxis_title="Hours",
                    title_x=0.5,
                    height=400,
                )

                st.plotly_chart(fig2, use_container_width=True)


            # ==============================
            # BONUS: INTERACTIVE FILTER
            # ==============================
            st.markdown("### 🎯 Filter Data")

            selected_range = st.slider(
                "Select Retention Range",
                float(df["retention"].min()),
                float(df["retention"].max()),
                (float(df["retention"].min()), float(df["retention"].max()))
            )

            filtered_df = df[
                (df["retention"] >= selected_range[0]) &
                (df["retention"] <= selected_range[1])
            ]

            fig3 = px.scatter(
                filtered_df,
                x="study_hours",
                y="retention",
                size="retention",
                color="retention",
                title="🎯 Retention vs Study Hours"
            )

            fig3.update_layout(template="plotly_dark", height=500)

            st.plotly_chart(fig3, use_container_width=True)
            st.success("""
            🧠 **Smart Insight: Effort vs Learning**

            - Studying more does NOT always mean learning more  
            - Compare both graphs:
            • If study hours ↑ but retention ↓ → 🚨 Inefficient learning  
            • If both ↑ → 🚀 Optimal learning  
            • If hours ↑ but retention flat → ⚠️ Passive learning issue  

            💡 Focus on improving retention, not just increasing study time.
            """)
    # ==========================================
    # TAB 3
    # ==========================================
    with tabs[2]:
    
            st.markdown("## 🧠 Learning Behavior Analysis")

            col1, col2 = st.columns(2)

            # ==============================
            # ADVANCED PIE (DONUT STYLE)
            # ==============================
            with col1:
                fig1 = px.pie(
                    df,
                    names="strategytype",
                    title="🎯 Strategy Distribution"
                )

                fig1.update_traces(
                    textinfo="percent+label",
                    pull=[0.05]*len(df["strategytype"].unique()),  # slight pop-out
                    hole=0.5  # makes it donut
                )

                fig1.update_layout(
                    template="plotly_dark",
                    title_x=0.5,
                    showlegend=True,
                    height=400
                )

                st.plotly_chart(fig1, use_container_width=True)

            # ==============================
            # ADVANCED BOX PLOT
            # ==============================
            with col2:
                fig2 = px.box(
                    df,
                    x="strategytype",
                    y="retention",
                    color="strategytype",
                    title="📊 Retention Spread by Strategy",
                    points="all"  # show all data points
                )

                fig2.update_traces(
                    jitter=0.4,
                    marker=dict(size=6, opacity=0.6)
                )

                fig2.update_layout(
                    template="plotly_dark",
                    title_x=0.5,
                    xaxis_title="Strategy Type",
                    yaxis_title="Retention %",
                    height=400,
                    showlegend=False
                )

                st.plotly_chart(fig2, use_container_width=True)

            # ==============================
            # KPI INSIGHTS
            # ==============================
            st.markdown("### 📌 Behavioral Insights")

            top_strategy = df.groupby("strategytype")["retention"].mean().idxmax()
            worst_strategy = df.groupby("strategytype")["retention"].mean().idxmin()

            k1, k2, k3 = st.columns(3)

            k1.metric("🏆 Best Strategy", top_strategy)
            k2.metric("⚠️ Needs Improvement", worst_strategy)
            k3.metric("📊 Avg Retention", f"{df['retention'].mean():.2f}%")

            # ==============================
            # INTERACTIVE FILTER
            # ==============================
            st.markdown("### 🎛️ Filter by Strategy")

            selected_strategy = st.multiselect(
                "Choose Strategy Type",
                options=df["strategytype"].unique(),
                default=list(df["strategytype"].unique())
            )

            filtered_df = df[df["strategytype"].isin(selected_strategy)]

            fig3 = px.violin(
                filtered_df,
                x="strategytype",
                y="retention",
                color="strategytype",
                box=True,
                points="all",
                title="🎻 Retention Distribution (Detailed View)"
            )

            fig3.update_layout(
                template="plotly_dark",
                height=500,
                title_x=0.5,
                showlegend=False
            )

            st.plotly_chart(fig3, use_container_width=True)
            st.success("""
            🧠 **Smart Insight: Learning Behavior Analysis**

            - If Passive dominates + low retention → 🚨 Ineffective study pattern  
            - If Active dominates + high retention → 🚀 Strong learning strategy  
            - If both similar but retention low → ⚠️ Need better techniques  

            💡 Learning is not about consuming content — it's about engaging with it.
            """)
    # ==========================================
    # TAB 4 (🔥 BURNOUT ENGINE — FULL SUMMARY)
    # ==========================================
    with tabs[3]:

        st.title("🔥 Burnout Intelligence Dashboard")

        # --------------------------------------
        # CALCULATE BURNOUT
        # --------------------------------------
        df["burnout_score"] = (
            (df["study_hours"] * 10) +
            ((1 - df["retention"]) * 50)
        ).clip(0, 100)

        current_score = df["burnout_score"].mean()
        avg_hours = df["study_hours"].mean()
        avg_ret = df["retention"].mean() * 100

        # --------------------------------------
        # KPI ROW
        # --------------------------------------
        c1, c2, c3 = st.columns(3)

        with c1:
            if current_score > 70:
                st.error(f"🔥 Burnout Score\n{current_score:.1f}")
            elif current_score > 40:
                st.warning(f"⚠️ Burnout Score\n{current_score:.1f}")
            else:
                st.success(f"✅ Burnout Score\n{current_score:.1f}")

        with c2:
            st.info(f"⏳ Avg Study Hours\n{avg_hours:.2f}")

        with c3:
            st.info(f"📊 Avg Retention\n{avg_ret:.1f}%")

        # --------------------------------------
        # ROW 1 — TREND + DISTRIBUTION
        # --------------------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📉 Burnout Trend")

            daily = df.groupby(date_col).agg({
                "burnout_score": "mean"
            }).reset_index()

            fig = px.line(daily, x=date_col, y="burnout_score")
            st.plotly_chart(fig, use_container_width=True, key="burnout_trend")

        with col2:
            st.markdown("### 📊 Burnout Distribution")

            fig = px.histogram(df, x="burnout_score", nbins=30)
            st.plotly_chart(fig, use_container_width=True, key="burnout_hist")

        # --------------------------------------
        # ROW 2 — ROOT CAUSE ANALYSIS
        # --------------------------------------
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### 🧠 Burnout vs Study Hours")

            fig = px.scatter(df, x="study_hours", y="burnout_score",
                            color="burnout_score")
            st.plotly_chart(fig, use_container_width=True, key="burnout_hours")

        with col4:
            st.markdown("### 📉 Burnout vs Retention")

            fig = px.scatter(df, x="retention", y="burnout_score",
                            color="burnout_score")
            st.plotly_chart(fig, use_container_width=True, key="burnout_ret")

        # --------------------------------------
        # ROW 3 — STRATEGY IMPACT
        # --------------------------------------
        if "strategytype" in df.columns:
            st.markdown("### ⚖️ Burnout by Learning Strategy")

            fig = px.box(df, x="strategytype", y="burnout_score")
            st.plotly_chart(fig, use_container_width=True, key="burnout_strategy")

        if "methodname" in df.columns:
            st.markdown("### 🧩 Burnout by Method")

            fig = px.bar(df, x="methodname", y="burnout_score")
            st.plotly_chart(fig, use_container_width=True, key="burnout_method")

        # --------------------------------------
        # AI SUMMARY
        # --------------------------------------
        st.markdown("### 🧠 AI Executive Summary")

        if current_score > 70:
            st.error("""
    🚨 **High Burnout Detected**

    - Excessive study hours are reducing efficiency  
    - Retention is dropping despite effort  
    - Immediate action required:
        • Reduce study time  
        • Switch to active recall  
        • Take recovery breaks  
    """)

        elif current_score > 40:
            st.warning("""
    ⚠️ **Moderate Burnout Risk**

    - Learning efficiency is declining  
    - Signs of fatigue visible  

    👉 Recommendation:
        • Break sessions into smaller chunks  
        • Add revision cycles  
        • Use active learning techniques  
    """)

        else:
            st.success("""
    ✅ **Healthy Learning State**

    - Good balance of effort & retention  
    - No burnout detected  

    🚀 Recommendation:
        • Maintain current strategy  
        • Gradually increase challenge level  
    """)

    # ==========================================
    # TAB 5
    # ==========================================
        with tabs[4]:
            st.markdown("## 🔍 Deep Data Explorer")

            # ==============================
            # SMART FILTERS
            # ==============================
            st.markdown("### 🎛️ Filter Data")

            col1, col2 = st.columns(2)

            with col1:
                if "methodname" in df.columns:
                    methods = st.multiselect(
                        "Select Method",
                        options=df["methodname"].unique(),
                        default=list(df["methodname"].unique())
                    )
                else:
                    methods = None

            with col2:
                if "retention" in df.columns:
                    retention_range = st.slider(
                        "Retention Range",
                        float(df["retention"].min()),
                        float(df["retention"].max()),
                        (float(df["retention"].min()), float(df["retention"].max()))
                    )
                else:
                    retention_range = None

            # Apply filters
            filtered_df = df.copy()

            if methods:
                filtered_df = filtered_df[filtered_df["methodname"].isin(methods)]

            if retention_range:
                filtered_df = filtered_df[
                    (filtered_df["retention"] >= retention_range[0]) &
                    (filtered_df["retention"] <= retention_range[1])
                ]

            # ==============================
            # KPI SUMMARY
            # ==============================
            st.markdown("### 📊 Summary Metrics")

            k1, k2, k3 = st.columns(3)

            k1.metric("📄 Records", len(filtered_df))
            k2.metric("📈 Avg Retention", f"{filtered_df['retention'].mean():.2f}%")
            k3.metric("🔥 Max Retention", f"{filtered_df['retention'].max():.2f}%")

            # ==============================
            # ADVANCED TABLE
            # ==============================
            st.markdown("### 📋 Data Preview")

            st.dataframe(
                filtered_df.head(100),
                use_container_width=True,
                height=350
            )

            # ==============================
            # ADVANCED BAR CHART
            # ==============================
            if "methodname" in filtered_df.columns:
                st.markdown("### 📊 Retention by Method")

                agg_df = (
                    filtered_df
                    .groupby("methodname")["retention"]
                    .mean()
                    .reset_index()
                    .sort_values(by="retention", ascending=False)
                )

                fig = px.bar(
                    agg_df,
                    x="methodname",
                    y="retention",
                    color="retention",
                    text_auto=".2f",
                    title="📈 Average Retention per Method"
                )

                fig.update_layout(
                    template="plotly_dark",
                    title_x=0.5,
                    xaxis_title="Method",
                    yaxis_title="Retention %",
                    height=450
                )

                st.plotly_chart(fig, use_container_width=True)

            # ==============================
            # BONUS: HEATMAP (ADVANCED INSIGHT)
            # ==============================
            if "methodname" in filtered_df.columns and "strategytype" in filtered_df.columns:
                st.markdown("### 🔥 Method vs Strategy Impact")

                heat_df = filtered_df.pivot_table(
                    index="methodname",
                    columns="strategytype",
                    values="retention",
                    aggfunc="mean"
                )

                fig2 = px.imshow(
                    heat_df,
                    text_auto=True,
                    aspect="auto",
                    title="📊 Retention Heatmap"
                )

                fig2.update_layout(
                    template="plotly_dark",
                    height=500,
                    title_x=0.5
                )

                st.plotly_chart(fig2, use_container_width=True)
    # ==========================================
    # TAB 6 (AI)
    # ==========================================

        with tabs[5]:

            st.subheader("🔮 Retention Prediction")

            col1, col2 = st.columns(2)

            with col1:
                input_hours = st.slider("Study Hours", 0.5, 10.0, 2.0)

            with col2:
                strategy = st.selectbox("Strategy", ["Active", "Passive"])

            strategy_encoded = le.transform([strategy])[0] if le else 0

            pred = model.predict([[input_hours, strategy_encoded]])[0] * 100

            st.success(f"📈 Predicted Retention: {pred:.1f}%")

            # 🔥 Dynamic Burnout
            score = burnout_score_dynamic(input_hours, pred)

            if score > 70:
                st.error(f"🔥 Burnout Score: {score} (High Risk)")
            elif score > 40:
                st.warning(f"⚠️ Burnout Score: {score} (Moderate)")
            else:
                st.success(f"✅ Burnout Score: {score} (Healthy)")

            # ==========================================
            # 🤖 AI INSIGHTS (MOVE INSIDE TAB)
            # ==========================================
            st.markdown("---")
            st.subheader("🤖 AI Learning Insights")

            # ------------------------------------------
            # 🎨 FORMAT BULLET POINTS
            # ------------------------------------------
            def format_points(text):
                lines = text.split("\n")
                points = []

                for line in lines:
                    line = line.strip()

                    if not line:
                        continue

                    line = line.replace("-", "").replace("*", "").strip()
                    points.append(f"<li style='margin-bottom:8px;'>• {line}</li>")

                return "<ul style='padding-left:20px;'>" + "".join(points) + "</ul>"

            # ------------------------------------------
            # SESSION STATE
            # ------------------------------------------
            if "ai_output" not in st.session_state:
                st.session_state.ai_output = {}

            if "show_rec" not in st.session_state:
                st.session_state.show_rec = False

            if "show_advice" not in st.session_state:
                st.session_state.show_advice = False

            # ------------------------------------------
            # FUNCTION (UNCHANGED)
            # ------------------------------------------
            def generate_ai_insights(df):

                ret = round(df["retention"].mean() * 100, 2)
                hours = round(df["study_hours"].sum(), 2)
                rph = round(ret / hours, 2) if hours else 0

                active_ratio = 0
                if "strategytype" in df.columns:
                    active_hours = df[df["strategytype"] == "Active"]["study_hours"].sum()
                    active_ratio = round((active_hours / hours) * 100, 2) if hours else 0

                prompt = f"""
                You are an expert in learning science.

                Analyze this student data:
                Retention: {ret}%
                Study Hours: {hours}
                RPH: {rph}
                Active Learning Ratio: {active_ratio}%

                STRICT FORMAT:

                PROBLEMS:
                - ...

                INSIGHTS:
                - ...

                RECOMMENDATIONS:
                - ...

                ADVICE:
                - ...
                """

                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    return response.choices[0].message.content

                except Exception as e:
                    return f"Error: {e}"

            # ------------------------------------------
            # GENERATE BUTTON
            # ------------------------------------------
            if st.button("🚀 Generate Analysis"):

                with st.spinner("Analyzing..."):
                    full_text = generate_ai_insights(df)

                sections = {
                    "problems": "",
                    "insights": "",
                    "recommendations": "",
                    "advice": ""
                }

                current = None
                for line in full_text.split("\n"):
                    line = line.strip()

                    if "PROBLEMS" in line.upper():
                        current = "problems"
                    elif "INSIGHTS" in line.upper():
                        current = "insights"
                    elif "RECOMMENDATIONS" in line.upper():
                        current = "recommendations"
                    elif "ADVICE" in line.upper():
                        current = "advice"
                    elif current:
                        sections[current] += line + "\n"

                st.session_state.ai_output = sections

            # ------------------------------------------
            # DISPLAY
            # ------------------------------------------
            data = st.session_state.ai_output

            if data.get("problems") or data.get("insights"):

                col1, col2 = st.columns(2)

                with col1:
                    if data.get("problems"):
                        st.markdown("### 🚨 Problems")
                        st.markdown(f"""
                        <div style="background:#7f1d1d;padding:15px;border-radius:10px;">
                        {format_points(data['problems'])}
                        </div>
                        """, unsafe_allow_html=True)

                with col2:
                    if data.get("insights"):
                        st.markdown("### 🔍 Insights")
                        st.markdown(f"""
                        <div style="background:#1e3a8a;padding:15px;border-radius:10px;">
                        {format_points(data['insights'])}
                        </div>
                        """, unsafe_allow_html=True)

            if data.get("problems"):
                if st.button("📌 Show Recommendations"):
                    st.session_state.show_rec = True

            if st.session_state.show_rec:
                st.markdown("### 📌 Recommendations")
                st.markdown(f"""
                <div style="background:#78350f;padding:15px;border-radius:10px;">
                {format_points(data.get('recommendations',''))}
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.show_rec:
                if st.button("🎯 Show Final Advice"):
                    st.session_state.show_advice = True

            if st.session_state.show_advice:
                st.markdown("### 🎯 Final Advice")
                st.markdown(f"""
                <div style="background:#064e3b;padding:15px;border-radius:10px;">
                {format_points(data.get('advice',''))}
                </div>
                """, unsafe_allow_html=True)

                st.subheader("🎯 Personalized Study Plan")
                for step in study_plan(df):
                    st.write("•", step)
