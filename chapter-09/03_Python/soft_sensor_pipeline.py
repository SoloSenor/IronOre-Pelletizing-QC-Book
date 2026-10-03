# ==============================================================================
# Soft Sensor Pipeline for Mill Grinding & Blaine Prediction
# Chapter 09: Data-Driven QC & AI in Mineral Processing
# ==============================================================================

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error
import matplotlib.pyplot as plt

def load_data(filepath):
    print(f"Loading continuous SCADA data from {filepath}...")
    df = pd.read_excel(filepath, sheet_name='SCADA_1min_Telemetry')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

def feature_engineering(df, lag_steps=[2, 5, 8, 12]):
    df_feat = df.copy()
    # Specific energy proxy
    dry_solids = df_feat['Feed_Flow_m3h'] * (df_feat['Slurry_Density_kgm3'] / 1000.0)
    df_feat['Specific_Energy'] = df_feat['Mill_Power_kW'] / (dry_solids + 1e-4)

    # Time lags
    lag_cols = ['Mill_Power_kW', 'Feed_Flow_m3h', 'Cyclone_Pressure_kPa', 'Slurry_Density_kgm3', 'Specific_Energy']
    for col in lag_cols:
        for lag in lag_steps:
            df_feat[f'{col}_lag_{lag}'] = df_feat[col].shift(lag)

    # Rolling window smoothing
    for col in ['Mill_Power_kW', 'Cyclone_Pressure_kPa']:
        df_feat[f'{col}_roll_mean_5'] = df_feat[col].rolling(window=5).mean()
        df_feat[f'{col}_roll_std_5'] = df_feat[col].rolling(window=5).std()

    return df_feat.dropna().reset_index(drop=True)

def train_and_evaluate(df):
    target = 'True_Blaine_Target_cm2g'
    drop_cols = ['Timestamp', 'True_Blaine_Target_cm2g', 'True_Pass_45um_Target_Pct', 'Lab_Blaine_LIMS', 'Lab_Pass_45um_LIMS']
    features = [c for c in df.columns if c not in drop_cols]

    X = df[features]
    y = df[target]

    # TimeSeries Split (80% Train, 20% Test)
    train_size = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1
    )

    print("Training XGBoost Soft Sensor model...")
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred) * 100

    print("=== XGBoost Soft Sensor Results ===")
    print(f"RMSE: {rmse:.2f} cm2/g")
    print(f"R² Score: {r2:.4f}")
    print(f"MAPE: {mape:.2f} %")

if __name__ == '__main__':
    data_path = '../Chapter09_SoftSensor_Grinding_Quality_Dataset.xlsx'
    df_raw = load_data(data_path)
    df_features = feature_engineering(df_raw)
    train_and_evaluate(df_features)
