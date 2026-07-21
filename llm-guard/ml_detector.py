import joblib

# Load model only once
model = joblib.load("jailbreak_detector.pkl")
vectorizer = joblib.load("vectorizer.pkl")


def detect_jailbreak(message: str):
    """
    Returns:
    prediction -> SAFE or JAILBREAK
    """

    features = vectorizer.transform([message])

    prediction = model.predict(features)[0]

    if prediction == 1:
        return "JAILBREAK"

    return "SAFE"