"""Chapter 12 PCA and SHAP analysis for the accompanying workbook."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

FEATURES = ['Blaine_cm2g', 'FilterCake_Moisture_pct', 'Bentonite_pct',
            'PreheatTemp_C', 'FiringTemp_C', 'Silica_pct']
TARGET = 'CCS_kg_pellet'

def main():
    path = Path(__file__).resolve().parent.parent / 'data' / 'ch12_pca_shap_dataset.xlsx'
    if not path.exists():
        sys.exit(f'Dataset not found: {path}')
    df = pd.read_excel(path, sheet_name='data')
    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        sys.exit(f'Expected columns missing from workbook: {missing}
Found: {list(df.columns)}')
    clean = df[FEATURES + [TARGET]].dropna()
    X, y = clean[FEATURES], clean[TARGET]
    scaler = StandardScaler()
    z = scaler.fit_transform(X)
    pca = PCA(n_components=min(3, len(FEATURES)))
    pca.fit(z)
    print(f'Rows used: {len(clean)}')
    print('PCA variance ratios (%):', np.round(100*pca.explained_variance_ratio_, 2))
    # Holdout assessment (random split for demonstration; use temporal/group split when appropriate).
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    try:
        from xgboost import XGBRegressor
        model = XGBRegressor(n_estimators=150, max_depth=4, learning_rate=0.05,
                             random_state=42, n_jobs=1)
    except ImportError:
        sys.exit('Install xgboost: pip install xgboost')
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    print(f'Holdout R2: {r2_score(yte, pred):.4f}; MAE: {mean_absolute_error(yte, pred):.3f}')
    try:
        import shap
        values = shap.TreeExplainer(model)(Xte)
        out = path.parent.parent / 'shap_summary.png'
        shap.summary_plot(values, Xte, show=False)
        import matplotlib.pyplot as plt
        plt.tight_layout(); plt.savefig(out, dpi=180, bbox_inches='tight'); plt.close()
        print(f'SHAP summary saved: {out}')
    except ImportError:
        print('SHAP is not installed; skipping explanation plot.')

if __name__ == '__main__':
    main()
