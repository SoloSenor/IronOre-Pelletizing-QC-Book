# Tutorial 04 — Python: Machine-Vision Pelletizing QC Pipeline
**Dataset:** `data/Chapter10_MachineVision_Pelletizing_Dataset.xlsx`
**Stack:** pandas · OpenCV · scikit-learn · matplotlib · seaborn
All code below is runnable top-to-bottom (`pip install pandas numpy opencv-python scikit-learn matplotlib seaborn openpyxl scipy`).

---

## 1. Load and Explore

```python
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import cv2, warnings
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="deep")
rng = np.random.default_rng(42)

PATH = "data/Chapter10_MachineVision_Pelletizing_Dataset.xlsx"
hourly  = pd.read_excel(PATH, sheet_name="size_distribution_hourly", parse_dates=["timestamp"])
pellets = pd.read_excel(PATH, sheet_name="pellet_features_sample")
liner   = pd.read_excel(PATH, sheet_name="liner_roi_weekly", parse_dates=["inspection_date"])
val     = pd.read_excel(PATH, sheet_name="validation_lab_vs_vision", parse_dates=["sampling_timestamp"])
grr     = pd.read_excel(PATH, sheet_name="gage_rr_study")

print(hourly.shape, pellets.shape)
print(hourly["process_state"].value_counts())
display(hourly.describe().T)          # in scripts: print(hourly.describe().T)

# Quality gate: size fractions must sum to 100
frac_sum = hourly[["pct_fines_under9mm","pct_normal_9_16mm","pct_oversize_over16mm"]].sum(axis=1)
print("Rows failing fraction check:", ((frac_sum < 99.9) | (frac_sum > 100.1)).sum())
hourly["span"] = (hourly["d90_mm"] - hourly["d10_mm"]) / hourly["d50_mm"]   # granulometric span
```

## 2. Control Charts (I-MR + Nelson rules) from scratch

```python
def imr_chart(series, title="I-MR Chart", rules=(1,2,3,5,6)):
    x = series.to_numpy(float)
    mr = np.abs(np.diff(x)); mrbar = mr.mean(); xbar = x.mean()
    sigma = mrbar / 1.128
    ucl, lcl = xbar + 3*sigma, xbar - 3*sigma
    # Nelson rule 6: 4 of 5 beyond 1 sigma, same side
    flags = pd.Series(False, index=series.index)
    for i in range(len(x)):
        w = x[max(0,i-4):i+1]
        if len(w) == 5 and (np.sum(w > xbar + sigma) >= 4 or np.sum(w < xbar - sigma) >= 4):
            flags.iloc[i] = True
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    ax[0].plot(x, lw=0.8); ax[0].axhline(xbar, c="g"); 
    ax[0].axhline(ucl, c="r", ls="--"); ax[0].axhline(lcl, c="r", ls="--")
    ax[0].plot(series.index[flags], x[flags.to_numpy()], "rx", ms=10, label="Nelson 6")
    ax[0].set_title(title); ax[0].legend()
    ax[1].plot(mr, lw=0.8); ax[1].axhline(mrbar, c="g")
    ax[1].axhline(3.267*mrbar, c="r", ls="--"); ax[1].set_title("Moving Range")
    plt.tight_layout(); plt.savefig("imr_d50.png", dpi=150); plt.show()
    return {"xbar": xbar, "sigma": sigma, "ucl": ucl, "lcl": lcl, "nelson6": int(flags.sum())}

stats = imr_chart(hourly["d50_mm"], "d50 Individuals & MR (Balling Disc)")
```

## 3. OpenCV: Image Processing & Morphology for Pellet Segmentation

```python
# Build a synthetic frame shaped like the camera ROI (use your real frames in production)
img = np.zeros((480, 640), np.uint8)
for _ in range(35):
    r = rng.integers(18, 40); c = rng.integers(2, 12)
    cv2.circle(img, tuple(rng.integers(40, 600, 2)), int(r*c*0.08)+15, 200, -1)
img = cv2.GaussianBlur(img, (5, 5), 0)
img = cv2.add(img, rng.normal(0, 12, img.shape).astype(np.uint8))   # sensor noise

# --- Segmentation pipeline: threshold -> morphology -> contours ---
_, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
clean = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)   # remove dust specks
clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel, iterations=2)  # fill pellet holes
# Watershed to split touching pellets
dist = cv2.distanceTransform(clean, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist, 0.5*dist.max(), 255, 0)
sure_fg, sure_bg = sure_fg.astype(np.uint8), cv2.dilate(clean, kernel, iterations=3)
unknown = cv2.subtract(sure_bg, sure_fg)
_, markers = cv2.connectedComponents(sure_fg)
markers = markers + 1; markers[unknown == 255] = 0
img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
cv2.watershed(img_bgr, markers)
seg = np.where(markers > 1, 255, 0).astype(np.uint8)

# --- Feature extraction (matches pellet_features_sample columns) ---
contours, _ = cv2.findContours(seg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
rows = []
MM_PER_PX = 0.05   # from calibration target
for c in contours:
    a, p = cv2.contourArea(c), cv2.arcLength(c, True)
    if a < 80: continue                      # drop noise
    A, P = a * MM_PER_PX**2, p * MM_PER_PX
    d_eq = 2 * np.sqrt(A / np.pi)
    circ = 4 * np.pi * A / P**2
    x, y, w, h = cv2.boundingRect(c)
    feret_max = max(w, h) * MM_PER_PX
    rows.append(dict(area_mm2=round(A, 2), perimeter_mm=round(P, 2),
                     Deq_mm=round(d_eq, 2), feret_max_mm=round(feret_max, 2),
                     circularity=round(circ, 3)))
feat = pd.DataFrame(rows)
print(feat.describe().round(2))

def classify(d_eq):                            # plant size classes
    return "Fines" if d_eq < 9 else ("Normal" if d_eq <= 16 else "Oversize")
feat["classification_label"] = feat["Deq_mm"].apply(classify)
print(feat["classification_label"].value_counts(normalize=True).round(3) * 100)

cv2.imwrite("segmentation_demo.png",
            cv2.drawContours(img_bgr.copy(), contours, -1, (0, 255, 0), 2))
```

## 4. Machine Learning with scikit-learn

### 4.1 Classify pellets (Normal / Fines / Oversize)

```python
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

X = feat[["area_mm2", "perimeter_mm", "Deq_mm", "feret_max_mm", "circularity"]]
y = feat["classification_label"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
clf = Pipeline([("sc", StandardScaler()),
                ("rf", RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42))])
cv = StratifiedKFold(5, shuffle=True, random_state=42)
print("CV F1-macro:", cross_val_score(clf, Xtr, ytr, cv=cv, scoring="f1_macro").mean().round(3))
clf.fit(Xtr, ytr)
print(classification_report(yte, clf.predict(Xte)))
print(confusion_matrix(yte, clf.predict(Xte)))
```

### 4.2 Predict d50 from process parameters + detect anomalies

```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics import r2_score, mean_absolute_error

cols = ["air_knife_pressure_bar", "ambient_dust_index", "exposure_time_us", "pellet_count_per_frame"]
Xp, yp = hourly[cols], hourly["d50_mm"]
Xtr, Xte, ytr, yte = train_test_split(Xp, yp, test_size=0.25, random_state=42)
reg = LinearRegression().fit(Xtr, ytr)
pred = reg.predict(Xte)
print(f"R2={r2_score(yte, pred):.3f}  MAE={mean_absolute_error(yte, pred):.3f} mm")
print(dict(zip(cols, reg.coef_.round(4))))   # dust coefficient = segmentation bias check

iso = IsolationForest(contamination=0.03, random_state=42).fit(Xp)
hourly["anomaly"] = iso.predict(Xp)          # -1 = anomaly
print("Anomalous hours:", (hourly.anomaly == -1).sum())
print(hourly.loc[hourly.anomaly == -1, ["timestamp", "special_cause_annotation"]].head())
```

### 4.3 PCA of pellet shape features

```python
from sklearn.decomposition import PCA
Z = StandardScaler().fit_transform(X[["area_mm2","perimeter_mm","Deq_mm","feret_max_mm"]])
pca = PCA().fit(Z)
print("Explained variance:", pca.explained_variance_ratio_.round(3))
```

## 5. Visualization with matplotlib / seaborn

```python
fig, ax = plt.subplots(2, 2, figsize=(13, 9))
sns.lineplot(data=hourly, x="timestamp", y="d50_mm", hue="disc_id", ax=ax[0,0])
ax[0,0].axhline(9, c="r", ls="--"); ax[0,0].axhline(16, c="r", ls="--")
ax[0,0].set_title("d50 vs time with spec limits")
sns.regplot(data=hourly, x="ambient_dust_index", y="d50_mm", scatter_kws={"s":8, "alpha":.4}, ax=ax[0,1])
ax[0,1].set_title("Dust index vs d50 (vision bias)")
sns.histplot(data=pellets, x="equivalent_diameter_Deq_mm", hue="classification_label",
             bins=40, kde=True, ax=ax[1,0]); ax[1,0].set_title("Pellet size distribution")
sns.lineplot(data=liner, x="inspection_week", y="corrosion_rust_area_ratio_pct",
             hue="roi_zone_id", marker="o", ax=ax[1,1]); ax[1,1].set_title("Liner corrosion trend")
plt.tight_layout(); plt.savefig("chapter10_dashboard.png", dpi=150); plt.show()
```

## 6. QC Decision Pipeline (production pseudo-deploy)

```python
def qc_pipeline(hour_row, clf, reg, iso, stats):
    """One-hour decision gate for the vision system."""
    checks = {
        "exposure_ok":   200 <= hour_row.exposure_time_us <= 500,
        "fractions_ok":  99.9 <= hour_row.pct_fines_under9mm +
                         hour_row.pct_normal_9_16mm +
                         hour_row.pct_oversize_over16mm <= 100.1,
        "d50_in_limits": stats["lcl"] <= hour_row.d50_mm <= stats["ucl"],
        "circ_ok":       0.85 <= hour_row.avg_circularity <= 0.97,
        "ml_anomaly":    iso.predict([[hour_row[c] for c in cols]])[0] == 1,
    }
    verdict = "RELEASE" if all(v for k, v in checks.items() if k != "ml_anomaly") else "HOLD"
    if verdict == "HOLD" or checks["ml_anomaly"]:
        verdict = "INVESTIGATE"
    return verdict, checks

print(qc_pipeline(hourly.iloc[500], clf, reg, iso, stats))
```

## 7. Export Scripts

```python
# Excel multi-sheet report with formatting
with pd.ExcelWriter("Chapter10_QC_Report.xlsx", engine="openpyxl",
                    datetime_format="YYYY-MM-DD HH:MM") as xw:
    hourly.to_excel(xw, "hourly_flags", index=False)
    feat.to_excel(xw, "pellet_features", index=False)
    pd.DataFrame([stats]).to_excel(xw, "control_limits", index=False)
    pd.DataFrame({"coef": cols, "value": reg.coef_,
                  "r2": [reg.score(Xte, yte)]*len(cols)}).to_excel(xw, "regression", index=False)

hourly.to_csv("hourly_flags.csv", index=False)
feat.to_parquet("pellet_features.parquet")      # fast re-load for dashboards
import json; json.dump(stats, open("control_limits.json", "w"), indent=2)
```

## 8. Best Practices
- Fix a random seed everywhere for reproducibility (`random_state=42`).
- Always validate the segmentation with `segmentation_anomaly_flag == 0` rows before training.
- Track `MM_PER_PX` calibration in config; recalibrate when R² of lab-vs-vision drops below 0.95.
- Version outputs (`imr_d50.png`, `chapter10_dashboard.png`, `Chapter10_QC_Report.xlsx`) with dates for audit trails.
