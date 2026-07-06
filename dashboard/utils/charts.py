import plotly.express as px
import pandas as pd

def fraud_distribution_chart(financial, credit, synthetic):

        data = pd.DataFrame({

            "Fraud Type": [
                "Financial Fraud",
                "Credit Card Fraud",
                "Synthetic Fraud"
            ],

            "Records": [
                financial,
                credit,
                synthetic
            ]

        })

        return px.pie(
            data,
            names="Fraud Type",
            values="Records",
            hole=0.4,
            title="Fraud Distribution"
        )


def fraud_bar_chart(financial, credit, synthetic):


    data = pd.DataFrame({

        "Module": [
            "Financial",
            "Credit Card",
            "Synthetic"
        ],

        "Records": [
            financial,
            credit,
            synthetic
        ]

    })

    return px.bar(
        data,
        x="Module",
        y="Records",
        title="Fraud Records"
    )

def risk_level_chart(df):

    temp = df.copy()

    temp["Risk"] = temp["fraud_probability"].apply(
        lambda x:
        "High" if x >= 0.80
        else "Medium" if x >= 0.50
        else "Low"
    )

    counts = (
        temp["Risk"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Risk",
        "Count"
    ]

    return px.pie(
        counts,
        names="Risk",
        values="Count",
        title="Risk Level Distribution"
    )

def prediction_chart(df):

    if "prediction" not in df.columns:
        return None

    counts = (
        df["prediction"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Prediction",
        "Count"
    ]

    return px.pie(
        counts,
        names="Prediction",
        values="Count",
        title="Fraud vs Legitimate"
    )

def probability_histogram(df):


    if "fraud_probability" not in df.columns:
        return None

    return px.histogram(
        df,
        x="fraud_probability",
        nbins=30,
        title="Fraud Probability Distribution"
    )

def timeline_chart(df):

    if "created_at" not in df.columns:
        return None

    timeline = (
        df.groupby(
            df["created_at"].dt.date
        )
        .size()
        .reset_index(name="Count")
    )

    return px.line(
        timeline,
        x="created_at",
        y="Count",
        title="Transactions Over Time"
    )

def kafka_chart(df):

    import plotly.express as px

    if df.empty:

        return None

    temp = df.copy()

    temp["created_at"] = pd.to_datetime(
        temp["created_at"]
    )

    temp["Minute"] = temp[
        "created_at"
    ].dt.floor("min")

    activity = (

        temp.groupby("Minute")

        .size()

        .reset_index(name="Messages")

    )

    return px.line(

        activity,

        x="Minute",

        y="Messages",

        markers=True,

        title="Kafka Streaming Activity"

    )
def kafka_topic_chart(df):

    if df.empty:

        return None

    import plotly.express as px

    counts = (

        df.groupby("topic_name")

        .size()

        .reset_index(name="Messages")

    )

    return px.bar(

        counts,

        x="topic_name",

        y="Messages",

        title="Messages per Topic"

    )
def ensemble_vote_chart(df):

    import plotly.express as px

    counts = (
        df["final_prediction"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Prediction",
        "Count"
    ]

    counts["Prediction"] = counts[
        "Prediction"
    ].replace(

        {

            1:"Fraud",

            0:"Legitimate"

        }

    )

    return px.pie(

        counts,

        names="Prediction",

        values="Count",

        hole=0.4,

        title="Final Ensemble Decisions"

    )