import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import confusion_matrix, precision_recall_curve, precision_score, recall_score, roc_curve

from model import FEATURES, generate_synthetic_data, train_model


st.set_page_config(page_title="AI Diabetes Risk Dashboard", page_icon="📊", layout="wide")
st.title("AI Diabetes Risk Dashboard")
st.caption("Synthetic-data ML demonstration — not for medical diagnosis or clinical use")


@st.cache_resource
def load_bundle():
    data = generate_synthetic_data()
    return data, train_model(data)


data, bundle = load_bundle()
threshold = st.sidebar.slider("Classification threshold", 0.10, 0.90, 0.50, 0.05)
predictions = (bundle.probabilities >= threshold).astype(int)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Synthetic records", f"{len(data):,}")
col2.metric("ROC-AUC", f"{bundle.auc:.3f}")
col3.metric("Precision", f"{precision_score(bundle.y_test, predictions, zero_division=0):.3f}")
col4.metric("Recall", f"{recall_score(bundle.y_test, predictions, zero_division=0):.3f}")

tab1, tab2, tab3 = st.tabs(["Model performance", "Cohort explorer", "Risk demonstration"])

with tab1:
    left, right = st.columns(2)
    fpr, tpr, _ = roc_curve(bundle.y_test, bundle.probabilities)
    roc = go.Figure(go.Scatter(x=fpr, y=tpr, name="Model"))
    roc.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(dash="dash"))
    roc.update_layout(title="ROC curve", xaxis_title="False-positive rate", yaxis_title="True-positive rate")
    left.plotly_chart(roc, use_container_width=True)
    precision, recall, _ = precision_recall_curve(bundle.y_test, bundle.probabilities)
    pr = px.line(x=recall, y=precision, labels={"x": "Recall", "y": "Precision"}, title="Precision-recall curve")
    right.plotly_chart(pr, use_container_width=True)
    matrix = confusion_matrix(bundle.y_test, predictions)
    st.plotly_chart(px.imshow(matrix, text_auto=True, labels=dict(x="Predicted", y="Actual"), title=f"Confusion matrix at {threshold:.2f}"), use_container_width=True)

with tab2:
    feature = st.selectbox("Feature", FEATURES[:-1])
    plot_data = data.copy()
    plot_data["Risk label"] = plot_data["diabetes_risk_label"].map({0: "Lower", 1: "Higher"})
    st.plotly_chart(px.histogram(plot_data, x=feature, color="Risk label", barmode="overlay", marginal="box"), use_container_width=True)

with tab3:
    st.info("This form illustrates model behavior on synthetic inputs. The score is not medical advice.")
    inputs = {
        "age": st.slider("Age", 18, 80, 45),
        "bmi": st.slider("BMI", 16.0, 55.0, 28.0),
        "glucose": st.slider("Glucose (synthetic feature)", 55, 240, 105),
        "blood_pressure": st.slider("Blood pressure", 45, 140, 78),
        "activity_minutes": st.slider("Weekly activity minutes", 0, 500, 150),
        "family_history": st.selectbox("Family-history indicator", [0, 1]),
    }
    row = pd.DataFrame([inputs])
    score = float(bundle.pipeline.predict_proba(row)[0, 1])
    st.metric("Demonstration risk score", f"{score:.1%}")
    st.progress(float(np.clip(score, 0, 1)))

