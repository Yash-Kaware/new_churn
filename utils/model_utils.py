from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def preprocess(df):
    df = df.dropna()
    encoders = {}
    for col in df.select_dtypes(include=['object']).columns:
        enc = LabelEncoder()
        df[col] = enc.fit_transform(df[col])
        encoders[col] = enc
    return df

def generate_decision_tree(df):
    df = preprocess(df)
    if df.shape[0] < 5:
        return {"tree": "Not enough data to train the tree."}
    X = df.drop('target', axis=1, errors='ignore')
    y = df['target'] if 'target' in df else df.iloc[:, -1]
    if len(set(y)) <= 1:
        return {"tree": "Not enough class diversity to train tree."}
    clf = DecisionTreeClassifier()
    clf.fit(X, y)
    return {"tree": export_text(clf, feature_names=list(X.columns))}

def get_feature_importance(df):
    df = preprocess(df)
    if df.shape[0] < 5:
        return {"importance": {}, "message": "Not enough data."}
    X = df.drop('target', axis=1, errors='ignore')
    y = df['target'] if 'target' in df else df.iloc[:, -1]
    if len(set(y)) <= 1:
        return {"importance": {}, "message": "Only one class present. Cannot compute importance."}
    model = RandomForestClassifier()
    model.fit(X, y)
    importance = dict(zip(X.columns, model.feature_importances_))
    return {"importance": importance}
