import pandas as pd
import numpy as np
import joblib
import logging
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────
BASE    = r'D:\urban-safety-intelligence'
DATA    = os.path.join(BASE, 'data', 'raw', 'fir_dataset.csv')
MDL_DIR = os.path.join(BASE, 'models')
os.makedirs(MDL_DIR, exist_ok=True)

# ── Step 1: Load ──────────────────────────────────────────────
log.info("Loading dataset...")
df = pd.read_csv(DATA, low_memory=False)   # fixes DtypeWarning
log.info(f"Raw shape: {df.shape}")

# ── Step 2: Use BOTH columns as text ──────────────────────────
# ActSection has IPC details, CrimeGroup has category
# Combine both → richer signal for TF-IDF
df['text'] = (
    df['CrimeGroup_Name'].fillna('').str.strip() + ' ' +
    df['ActSection'].fillna('').str.strip()
).str.lower()

# ── Step 3: Smart label mapping ───────────────────────────────
# Map ALL CrimeGroup_Name values into clean categories
# Based on actual values we can see in your data

def map_crime(crime_group):
    cg = str(crime_group).upper().strip()

    # NOISE — remove these rows entirely
    noise = ['KARNATAKA POLICE ACT', 'POLICE ACT', 'TAKA POLICE']
    if any(n in cg for n in noise):
        return None

    # THEFT
    if any(x in cg for x in [
        'THEFT', 'BURGLARY', 'ROBBERY', 'DACOITY',
        'SNATCHING', 'PICKPOCKET', 'MOTOR VEHICLE THEFT',
        'CYCLE THEFT', 'STOLEN'
    ]):
        return 'theft'

    # ASSAULT / VIOLENCE
    if any(x in cg for x in [
        'ASSAULT', 'MURDER', 'HURT', 'RIOT',
        'KIDNAPPING', 'ABDUCTION', 'GRIEVOUS',
        'ATTEMPT TO MURDER', 'CULPABLE HOMICIDE'
    ]):
        return 'assault'

    # FRAUD / CHEATING
    if any(x in cg for x in [
        'FRAUD', 'CHEATING', 'FORGERY', 'COUNTERFEITING',
        'CYBER', 'ONLINE', 'MISAPPROPRIATION', 'BREACH OF TRUST',
        'EXTORTION', 'CORRUPTION'
    ]):
        return 'fraud'

    # WOMEN SAFETY
    if any(x in cg for x in [
        'RAPE', 'MOLESTATION', 'SEXUAL', 'HARASSMENT',
        'DOWRY', 'CRUELTY BY HUSBAND', 'INDECENT',
        'STALKING', 'WOMEN', 'CHILD MARRIAGE'
    ]):
        return 'women_safety'

    # ACCIDENT / NEGLIGENCE
    if any(x in cg for x in [
        'ACCIDENT', 'MOTOR VEHICLE', 'NEGLIGENCE',
        'FATAL', 'NON-FATAL', 'HIT AND RUN'
    ]):
        return 'accident'

    # PROPERTY CRIME
    if any(x in cg for x in [
        'TRESPASS', 'MISCHIEF', 'ARSON', 'DAMAGE',
        'PROPERTY', 'BREAKING'
    ]):
        return 'property_crime'

    return None   # unmapped → drop

log.info("Mapping crime categories...")
df['crime_type'] = df['CrimeGroup_Name'].apply(map_crime)

# ── Step 4: Drop noise rows ───────────────────────────────────
before = len(df)
df = df[df['crime_type'].notna()].copy()
df = df[df['text'].str.len() > 5].copy()
log.info(f"Dropped {before - len(df)} noise rows → {len(df)} clean rows")

# ── Step 5: Class distribution ────────────────────────────────
log.info("\nClass distribution:")
print(df['crime_type'].value_counts())

# ── Step 6: Balance classes (upsample minorities) ─────────────
log.info("Balancing classes...")
max_size = df['crime_type'].value_counts().max()
balanced = []
for crime_type, group in df.groupby('crime_type'):
    if len(group) < 100:   # skip classes with too few samples
        continue
    upsampled = resample(group,
        replace=True,
        n_samples=min(max_size, len(group) * 3),
        random_state=42)
    balanced.append(upsampled)

df_balanced = pd.concat(balanced).reset_index(drop=True)
log.info(f"Balanced shape: {df_balanced.shape}")
log.info("\nBalanced distribution:")
print(df_balanced['crime_type'].value_counts())

# ── Step 7: Train/test split ──────────────────────────────────
X = df_balanced['text']
y = df_balanced['crime_type']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# ── Step 8: Build pipeline ────────────────────────────────────
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 2),      # drop trigrams → faster on 1M rows
        max_features=30000,      # reduced → still accurate
        min_df=3,
        sublinear_tf=True,
        strip_accents='unicode',
        analyzer='word',
    )),
    ('clf', LinearSVC(           # 10x faster than LogisticRegression
        C=1.0,                   # on large datasets
        class_weight='balanced',
        max_iter=2000,
        random_state=42,
    ))
])

# ── Step 9: Cross-validation first ───────────────────────────
log.info("Running 3-fold cross-validation on sample...")
# Use smaller sample for CV — no need to CV on 1.3M rows
X_cv_sample = X_train.sample(n=50000, random_state=42)
y_cv_sample = y_train[X_cv_sample.index]
cv_scores = cross_val_score(pipeline, X_cv_sample, y_cv_sample, cv=3, scoring='accuracy')
log.info(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# ── Step 10: Train final model ────────────────────────────────
log.info("Training final model...")
pipeline.fit(X_train, y_train)

# ── Step 11: Evaluate ─────────────────────────────────────────
y_pred = pipeline.predict(X_test)
test_acc = (y_pred == y_test).mean()
log.info(f"Test Accuracy: {test_acc:.4f}")

log.info("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── Step 12: Save model ───────────────────────────────────────
joblib.dump(pipeline, os.path.join(MDL_DIR, 'fir_model.pkl'))
log.info(f"Model saved → {MDL_DIR}/fir_model.pkl")

# ── Step 13: Test with real sentences ─────────────────────────
test_cases = [
    "Thieves broke into the house and stole gold jewelry and cash",
    "Unknown person snatched mobile phone near bus stop",
    "Accused cheated victim of 2 lakhs through fake UPI payment",
    "Victim was assaulted and grievously hurt by accused",
    "Woman harassed and stalked by neighbour repeatedly",
    "Car accident on Hosur Road, driver fled the scene",
]

log.info("\n── Live Predictions ──────────────────────────")
for text in test_cases:
    pred = pipeline.predict([text])[0]
    # LinearSVC uses decision scores instead of probabilities
    scores = pipeline.decision_function([text])[0]
    conf = (np.exp(scores) / np.exp(scores).sum()).max() * 100
    log.info(f"Input:  {text[:55]}...")
    log.info(f"Result: {pred.upper()} ({conf:.1f}% confidence)\n")

