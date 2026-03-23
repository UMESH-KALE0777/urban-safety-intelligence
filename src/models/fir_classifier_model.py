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

# Expanded English keyword descriptions per IPC section
IPC_DESCRIPTIONS = {
    # THEFT
    '379': 'theft stolen property goods snatched took away stole burglar',
    '380': 'theft dwelling house building broke entered stole burglary',
    '381': 'theft clerk servant employee stole office workplace',
    '382': 'theft preparation hurt weapon robbery',
    '356': 'snatching assault theft chain mobile gold snatched person',
    '457': 'lurking trespass theft night broke house entered stole',
    '454': 'house breaking theft entered stole jewelry cash gold',

    # ASSAULT
    '302': 'murder killed death culpable homicide stabbed shot dead body',
    '304': 'culpable homicide death negligence died killed',
    '307': 'attempt murder assault weapon knife stabbed attacked',
    '323': 'voluntarily hurt assault beat struck punch slap injured',
    '324': 'hurt dangerous weapon knife rod assault bleeding injured',
    '325': 'grievous hurt serious injury fracture hospitalized',
    '326': 'grievous hurt acid dangerous weapon attack burn disfigure',
    '351': 'assault criminal force threat intimidate pushed attacked',
    '147': 'riot unlawful assembly violence mob attack group',
    '148': 'riot armed weapon mob group attack violence',
    '363': 'kidnapping abduction minor child taken missing',
    '364': 'kidnapping murder ransom held captive',
    '365': 'kidnapping wrongful confinement locked held captive',

    # FRAUD
    '420': 'cheating fraud deception dishonestly money cash deceived tricked',
    '406': 'criminal breach trust misappropriation betrayed stole entrusted',
    '415': 'cheating deception property money transferred fake',
    '417': 'cheating fraud punishment deceived money property',
    '419': 'cheating impersonation fake identity fraud pretended',
    '463': 'forgery false document fake certificate fraud signature',
    '465': 'punishment forgery fake document created',
    '468': 'forgery cheating fraud purpose document fake',
    '471': 'using forged document genuine fake presented',
    '384': 'extortion threat fear injury demanded money blackmail',
    '386': 'extortion death grievous hurt threat demanded money',

    # WOMEN SAFETY
    '376': 'rape sexual assault woman victim forced intercourse',
    '354': 'assault woman modesty outrage touched groped molestation',
    '354A': 'sexual harassment unwelcome physical contact demand favour',
    '354B': 'assault woman disrobe force removed clothes',
    '354C': 'voyeurism watching woman private act recorded',
    '354D': 'stalking woman follow monitor obsessively watching',
    '498': 'husband relative cruelty woman domestic violence',
    '498A': 'cruelty husband family dowry harassment tortured wife',
    '304B': 'dowry death woman husband family killed burned',
    '306': 'abetment suicide woman harassment drove suicide',
    '509': 'word gesture insult modesty woman eve teasing comment',
    '366': 'kidnapping woman compel marriage abducted forced',

    # ACCIDENT
    '279': 'rash driving road accident vehicle hit run over speed',
    '304A': 'death negligence accident careless died killed vehicle',
    '337': 'hurt rash negligence driving road accident injured',
    '338': 'grievous hurt rash negligence vehicle road accident serious',

    # PROPERTY CRIME
    '436': 'mischief fire house destroy burned arson set fire',
    '447': 'criminal trespass property entered without permission',
    '448': 'house trespass breaking entering unauthorised',
    '425': 'mischief wrongful loss damage property destroyed',
    '426': 'mischief punishment property damage vandalised',
    '435': 'mischief fire property damage arson burned',
}

def decode_act_section(act_text):
    import re
    if pd.isna(act_text):
        return ''
    act_str = str(act_text)
    decoded_parts = []
    sections = re.findall(r'\b(\d{2,3}[A-Z]?)\b', act_str)
    for sec in sections:
        if sec in IPC_DESCRIPTIONS:
            decoded_parts.append(IPC_DESCRIPTIONS[sec])
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

# ── Augment with plain English sentences ──────────────────────
# This bridges the gap between legal text and real descriptions
log.info("Augmenting with plain English sentences...")

english_samples = [
    # THEFT
    ("thieves broke into house stole gold jewelry cash valuables", "theft"),
    ("unknown person snatched mobile phone gold chain near bus stop", "theft"),
    ("burglar entered through back door stole laptop cash jewelry", "theft"),
    ("vehicle was stolen from parking lot during night", "theft"),
    ("pickpocket stole wallet purse in crowded market bus", "theft"),
    ("robbers looted shop at gunpoint took cash ornaments", "theft"),
    ("cycle motorcycle stolen from outside house compound", "theft"),

    # ASSAULT
    ("victim was assaulted beaten grievously hurt by accused", "assault"),
    ("accused attacked victim with knife rod causing serious injury", "assault"),
    ("mob attacked victim with sticks rods caused bleeding injuries", "assault"),
    ("accused attempted to murder victim stabbed multiple times", "assault"),
    ("victim was kidnapped and held captive demanding ransom", "assault"),
    ("accused punched slapped kicked victim in public", "assault"),
    ("fight broke out group attacked victim with weapons", "assault"),

    # FRAUD
    ("accused cheated victim of two lakhs through fake UPI payment", "fraud"),
    ("online fraud victim transferred money to fake account", "fraud"),
    ("accused impersonated bank officer cheated victim of savings", "fraud"),
    ("fake investment scheme defrauded multiple victims of crores", "fraud"),
    ("accused forged documents signature to obtain loan fraudulently", "fraud"),
    ("job fraud accused collected money promising employment abroad", "fraud"),
    ("phishing link sent victim lost money from bank account", "fraud"),

    # WOMEN SAFETY
    ("woman harassed stalked by neighbour repeatedly following her", "women_safety"),
    ("accused outraged modesty of woman touched inappropriately", "women_safety"),
    ("victim of domestic violence beaten by husband daily", "women_safety"),
    ("woman subjected to dowry harassment cruelty by in-laws", "women_safety"),
    ("accused made obscene gestures comments towards woman", "women_safety"),
    ("woman raped by known person on false promise of marriage", "women_safety"),
    ("girl child sexually assaulted by neighbour relative", "women_safety"),

    # ACCIDENT
    ("car accident on hosur road driver fled the scene hit and run", "accident"),
    ("rash driving caused accident pedestrian injured on road", "accident"),
    ("drunk driver ran red light hit motorcycle rider injured", "accident"),
    ("lorry truck overturned on highway multiple injured", "accident"),
    ("speeding vehicle hit pedestrian on zebra crossing", "accident"),
    ("auto rickshaw collision caused grievous injuries to passengers", "accident"),

    # PROPERTY CRIME
    ("accused set fire to house property out of revenge arson", "property_crime"),
    ("neighbour trespassed property damaged boundary wall", "property_crime"),
    ("accused damaged vehicle windshield out of personal enmity", "property_crime"),
    ("group vandalised shop broke windows damaged property", "property_crime"),
]

# Create dataframe from English samples — repeat to give weight
english_df = pd.DataFrame(english_samples * 500,  # 500x repetition
    columns=['text', 'crime_type'])

log.info(f"Added {len(english_df)} English augmentation samples")

# Merge with existing balanced data
df_balanced = pd.concat([df_balanced, english_df], ignore_index=True)
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
log.info(f"Final training shape: {df_balanced.shape}")

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
 
