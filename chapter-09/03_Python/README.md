# 🐍 پیاده‌سازی سنسور نرم تخمین بلین مدار آسیاب کنسانتره آهن (Soft Sensor Pipeline)
> **مربوط به بخش سوم - فصل نهم:** علم داده و هوش مصنوعی در آزمایشگاه و خط تولید  
> **نویسنده/مدرس:** امین  

---

## 🎯 مقدمه و هدف مسئله

در فرآوری مواد معدنی و کارخانه‌های تولید کنسانتره سنگ‌آهن، سنجش ظرافت پودر خروجی مدار خردایش (**سطح ویژه بلین - Blaine** و **درصد عبوری از الک ۴۵ میکرون - Passing 45µm**) توسط آزمایشگاه LIMS معمولاً با **تاخیر زمانی ۱ تا ۲ ساعته** به اتاق کنترل گزارش می‌شود.  

این تاخیر طولانی موجب می‌شود که در صورت نوسان سختی سنگ‌آهن یا تغییر بار در گردش، کنترل‌کننده خط با تاخیر فاز مداخله کرده و منجر به تولید بار با دانه‌بندی نامطلوب یا اتلاف شدید انرژی گردد.

**هدف این پایپ‌لاین:** ساخت یک **سنسور نرم (Soft Sensor)** بر پایه الگوریتم قدرتمند `XGBoost` که با خواندن تله‌متری ۱ دقیقه‌ای سنسورهای سخت‌افزاری SCADA (توان آسیاب، دبی، فشار هیدروسیکلون، دانسیته و آب ورودی)، مقدار بلین را در لحظه ($t$) تخمین بزند.

---

## ⚙️ متدولوژی و روابط فیزیکی حاکم (Physical & Metallurgical Dynamics)

در این مدل، متغیرهای متالورژیکی با روابط زیر شبیه‌سازی و مهندسی شده‌اند:

1. **نرخ انرژی ویژه خردایش (Specific Grinding Energy):**
   $$E_{\text{spec}} = \frac{\text{Mill\_Power (kW)}}{\text{Feed\_Flow} \times \frac{\text{Slurry\_Density}}{1000} + 10^{-4}} \quad [\text{kWh/ton}]$$

2. **تاخیر فاز هیدرودینامیکی (Hydrodynamic Time Lags):**
   * زمان اقامت بار در آسیاب گلوله‌ای: $\tau_{\text{mill}} \approx 8 \text{ min}$
   * زمان پاسخ دینامیکی کلاستر هیدروسیکلون: $\tau_{\text{cyclone}} \approx 2 \text{ min}$
   * اثر اینرسی دانسیته پالپ: $\tau_{\text{density}} \approx 1 \text{ min}$

3. **جلوگیری از نشت اطلاعات (Data Leakage Prevention):**
   * استفاده از تقسیم‌بندی زمانی `TimeSeriesSplit` (عدم استفاده از `Shuffle` تصادفی).
   * مقیاس‌بندی توسط `RobustScaler` با میانگین و چندک‌های بازه آموزش (Train).

---

## 💻 کد کامل پایپ‌لاین پایتون (قابل اجرا در Jupyter Notebook)

کد زیر را می‌توانید به صورت یکجا در یک سلول جوپیتر کپی و اجرا کنید. این اسکریپت هم از دیتاست اکسل پشتیبانی می‌کند و هم در صورت نبود فایل، دیتای استاندارد صنعتی را در حافظه شبیه‌سازی می‌کند:
```python
# ==============================================================================
# Soft Sensor Pipeline for Mill Grinding & Blaine Prediction
# Chapter 09: Industrial AI & Quality Engineering
# ==============================================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error

# ------------------------------------------------------------------------------
# گام ۱: بارگذاری داده (از فایل اکسل یا ساخت دیتاست سنتتیک صنعتی)
# ------------------------------------------------------------------------------
def get_industrial_dataset(excel_path=None):
if excel_path and os.path.exists(excel_path):
print(f"📥 Loading dataset from file: {excel_path}")
df = pd.read_excel(excel_path, sheet_name='SCADA_1min_Telemetry')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# در صورت وجود نام‌های بزرگ‌حرف در اکسل:
rename_map = {
'Mill_Power_kW': 'mill_power',
'Feed_Flow_m3h': 'feed_flow',
'Cyclone_Pressure_kPa': 'cyclone_pressure',
'Slurry_Density_kgm3': 'slurry_density',
'Feed_Water_m3h': 'feed_water',
'True_Blaine_Target_cm2g': 'lab_blaine',
'True_Pass_45um_Target_Pct': 'lab_pass_45um'
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
return df

print("⚠️ Dataset file not found. Generating realistic industrial simulation data...")
np.random.seed(42)
n_samples = 5000  # بازه زمانی معادل ۵۰۰۰ دقیقه

# متغیرهای سنسورهای سخت‌افزاری برخط
mill_power = np.random.normal(loc=3200, scale=40, size=n_samples)
feed_flow = np.random.normal(loc=450, scale=8, size=n_samples)
cyclone_pressure = np.random.normal(loc=120, scale=4, size=n_samples)
slurry_density = np.random.normal(loc=1650, scale=15, size=n_samples)
feed_water = np.random.normal(loc=85, scale=4, size=n_samples)

time_lag = 8
true_blaine = np.zeros(n_samples)
true_pass_45 = np.zeros(n_samples)

for t in range(time_lag, n_samples):
# انرژی ویژه خردایش بر اساس تناژ خشک ورودی
dry_tonnage = feed_flow[t - time_lag] * (slurry_density[t - time_lag] / 1000.0)
specific_energy = mill_power[t - time_lag] / (dry_tonnage + 1e-4)

press_effect = cyclone_pressure[t - 2] * 4.2
dens_penalty = (slurry_density[t - 1] - 1600) * 0.8

# تخمین بلین و درصد عبوری از ۴۵ میکرون همراه با نویز طبیعی متالورژیکی
true_blaine[t] = 1100 + (specific_energy * 180) + press_effect - dens_penalty + np.random.normal(0, 15)
true_pass_45[t] = 60 + (specific_energy * 4.2) + (press_effect * 0.05) - (dens_penalty * 0.02) + np.random.normal(0, 0.5)

df_synthetic = pd.DataFrame({
'mill_power': mill_power,
'feed_flow': feed_flow,
'cyclone_pressure': cyclone_pressure,
'slurry_density': slurry_density,
'feed_water': feed_water,
'lab_blaine': true_blaine,
'lab_pass_45um': true_pass_45
}).iloc[time_lag:].reset_index(drop=True)

return df_synthetic

# ------------------------------------------------------------------------------
# گام ۲: مهندسی ویژگی‌های تاخیر زمانی (Time-lag Feature Engineering)
# ------------------------------------------------------------------------------
def create_industrial_features(df, lag_steps=[2, 5, 8, 12]):
df_feat = df.copy()

# ۱. محاسبه نرخ انرژی ویژه
dry_solids = df_feat['feed_flow'] * (df_feat['slurry_density'] / 1000.0)
df_feat['specific_energy_proxy'] = df_feat['mill_power'] / (dry_solids + 1e-4)

# ۲. ایجاد لَگ‌های زمانی دینامیک آسیاب و سیکلون
base_cols = ['mill_power', 'feed_flow', 'cyclone_pressure', 'slurry_density', 'specific_energy_proxy']
for col in base_cols:
for lag in lag_steps:
df_feat[f'{col}_lag_{lag}'] = df_feat[col].shift(lag)

# ۳. محاسبه میانگین و انحراف معیار متحرک جهت فیلتر نویز ابزاردقیق
for col in ['mill_power', 'cyclone_pressure']:
df_feat[f'{col}_roll_mean_5'] = df_feat[col].rolling(window=5).mean()
df_feat[f'{col}_roll_std_5'] = df_feat[col].rolling(window=5).std()

# حذف سطرهای اولیه دارای مقادیر خالی ناشی از شیفت زمانی
return df_feat.dropna().reset_index(drop=True)

# ------------------------------------------------------------------------------
# گام ۳: آموزش مدل، مقیاس‌بندی و ارزیابی
# ------------------------------------------------------------------------------
def run_pipeline():
# بررسی مسیر دیتاست
dataset_file = 'Chapter09_SoftSensor_Grinding_Quality_Dataset.xlsx'
raw_df = get_industrial_dataset(dataset_file)
processed_df = create_industrial_features(raw_df)

# تفکیک ماتریس ویژگی‌ها و تارگت بلین
target_col = 'lab_blaine'
ignore_cols = ['Timestamp', 'lab_blaine', 'lab_pass_45um', 'Lab_Blaine_LIMS', 'Lab_Pass_45um_LIMS']
features = [c for c in processed_df.columns if c not in ignore_cols]

X = processed_df[features]
y = processed_df[target_col]

# جداسازی سری زمانی (۸۰٪ آموزش، ۲۰٪ تست بدون نشت اطلاعات آینده)
train_size = int(len(processed_df) * 0.8)
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

# مقیاس‌بندی مقاوم در برابر داده‌های پرت
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# تعریف و تنظیم هایپرپارامترهای صنعتی XGBoost
model = xgb.XGBRegressor(
n_estimators=300,
max_depth=5,
learning_rate=0.03,
subsample=0.85,
colsample_bytree=0.85,
random_state=42,
n_jobs=-1
)

print("🚀 Training XGBoost Soft Sensor model...")
model.fit(X_train_scaled, y_train)

# ارزیابی روی داده‌های تست
y_pred = model.predict(X_test_scaled)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred) * 100

print("\n" + "="*50)
print("📊 نتایج ارزیابی سنسور نرم تخمین بلین")
print("="*50)
print(f"🔹 ضریب تبیین مدل (R² Score):       {r2:.4f}")
print(f"🔹 خطای ریشه میانگین مربعات (RMSE): {rmse:.2f} cm²/g")
print(f"🔹 میانگین درصد خطای مطلق (MAPE):   {mape:.2f} %")
print("="*50)

# رسم نمودار روند زمانی پایش آنلاین
plot_results(y_test.values, y_pred)

# ------------------------------------------------------------------------------
# گام ۴: رسم نمودار کیفیت مانیتورینگ اتاق کنترل
# ------------------------------------------------------------------------------
def plot_results(y_true, y_pred, window=250):
plt.figure(figsize=(14, 6), dpi=100)

plt.plot(y_true[:window], label='Actual Process Blaine (داده واقعی فرآیند)', color='#1f77b4', lw=2)
plt.plot(y_pred[:window], label='Soft Sensor Predicted (پیش‌بینی برخط سنسور نرم)', color='#ff7f0e', linestyle='--', lw=2)

# حدود استاندارد کیفیت کنسانتره آهن
plt.axhline(1800, color='green', linestyle='-', alpha=0.8, label='Target (1800 cm²/g)')
plt.axhline(1850, color='red', linestyle=':', alpha=0.7, label='Upper Spec Limit (USL = 1850)')
plt.axhline(1750, color='red', linestyle=':', alpha=0.7, label='Lower Spec Limit (LSL = 1750)')

plt.title('Real-time Blaine Soft Sensor Monitoring vs Actual Lab Quality', fontsize=13, fontweight='bold')
plt.xlabel('Time Step (Minutes)', fontsize=11)
plt.ylabel('Blaine Fineness (cm²/g)', fontsize=11)
plt.legend(loc='upper right', frameon=True)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# اجرا در نوت‌بوک
if __name__ == '__main__':
run_pipeline()
