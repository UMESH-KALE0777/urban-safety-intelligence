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

# ── Step 2: Text Processing (IPC Decoding) ─────────────────────
# ActSection has IPC details. We map IPC codes to their descriptions.

IPC_DESCRIPTIONS = {
    # THEFT
    '379': 'theft stolen property goods',
    '380': 'theft dwelling house building',
    '381': 'theft by clerk servant employee',
    '382': 'theft preparation hurt',
    '356': 'snatching assault theft person',
    '457': 'lurking house trespass theft night',
    '454': 'house breaking theft',

    # ASSAULT / VIOLENCE
    '302': 'murder culpable homicide death killed',
    '304': 'culpable homicide death negligence',
    '307': 'attempt to murder assault weapon',
    '323': 'voluntarily causing hurt assault beating',
    '324': 'hurt dangerous weapon knife assault',
    '325': 'grievous hurt injury serious',
    '326': 'grievous hurt acid dangerous weapon',
    '351': 'assault criminal force threat',
    '147': 'riot unlawful assembly violence',
    '148': 'riot armed deadly weapon',
    '149': 'unlawful assembly common object',
    '363': 'kidnapping abduction minor',
    '364': 'kidnapping murder ransom',
    '365': 'kidnapping wrongful confinement',
    '366': 'kidnapping woman compel marriage',

    # FRAUD / CHEATING
    '420': 'cheating fraud deception dishonestly',
    '406': 'criminal breach trust misappropriation',
    '408': 'criminal breach trust employee',
    '409': 'criminal breach trust public servant',
    '415': 'cheating deception property',
    '417': 'punishment cheating fraud',
    '418': 'cheating knowledge wrongful loss',
    '419': 'cheating impersonation fraud',
    '463': 'forgery false document fraud',
    '464': 'making false document forgery',
    '465': 'punishment forgery',
    '468': 'forgery cheating fraud purpose',
    '471': 'using forged document genuine',
    '384': 'extortion threat fear injury',
    '385': 'extortion fear death grievous hurt',
    '386': 'extortion death grievous hurt',

    # WOMEN SAFETY
    '376': 'rape sexual assault woman victim',
    '354': 'assault criminal force woman modesty',
    '354A': 'sexual harassment unwelcome physical contact',
    '354B': 'assault woman disrobe force',
    '354C': 'voyeurism watching woman private act',
    '354D': 'stalking woman follow monitor',
    '498': 'husband relative cruelty woman',
    '498A': 'cruelty husband family dowry harassment',
    '304B': 'dowry death woman husband family',
    '306': 'abetment suicide woman harassment',
    '509': 'word gesture insult modesty woman',

    # ACCIDENT
    '279': 'rash driving road accident vehicle',
    '304A': 'death negligence accident careless',
    '337': 'hurt rash negligence driving',
    '338': 'grievous hurt rash negligence vehicle',
    '427': 'mischief damage fifty rupees',

    # PROPERTY CRIME
    '436': 'mischief fire house destroy',
    '447': 'criminal trespass property',
    '448': 'house trespass breaking entering',
    '449': 'house trespass hurt death',
    '425': 'mischief wrongful loss damage property',
    '426': 'mischief punishment property damage',
    '430': 'mischief irrigation works',
    '435': 'mischief fire property damage',
}

def decode_act_section(act_text):
    """Extract IPC sections and replace with descriptions"""
    import re
    if pd.isna(act_text):
        return ''
    
    act_str = str(act_text)
    decoded_parts = []
    
    # Extract all section numbers from text like "IPC 1860 U/s: 379,380"
    sections = re.findall(r'\b(\d{2,3}[A-Z]?)\b', act_str)
    
    for sec in sections:
        if sec in IPC_DESCRIPTIONS:
            decoded_parts.append(IPC_DESCRIPTIONS[sec])
        else:
            decoded_parts.append(sec)  # keep original if not in map
    
    # Also keep original act text for context
    decoded_parts.append(act_str.lower())
    
    return ' '.join(decoded_parts)

log.info("Decoding IPC sections to descriptions...")
df['text'] = df['ActSection'].apply(decode_act_section)

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

# ── Step 6: Balance classes (Downsample/Upsample to 50K) ──────
log.info("Balancing classes...")
TARGET_PER_CLASS = 50000   # enough for excellent accuracy

balanced = []
for crime_type, group in df.groupby('crime_type'):
    if len(group) < 200:
        continue
    sampled = resample(group,
        replace=len(group) < TARGET_PER_CLASS,
        n_samples=TARGET_PER_CLASS,
        random_state=42)
    balanced.append(sampled)

df_balanced = pd.concat(balanced).sample(frac=1, random_state=42).reset_index(drop=True)
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
 
