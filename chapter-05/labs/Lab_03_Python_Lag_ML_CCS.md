<div dir="rtl">

# کارگاه ۳ — پایتون: همگام‌سازی تأخیر زمانی (Time-Lag Alignment)، آموزش مدل Random Forest برای پیش‌بینی CCS و تحلیل رویه پاسخ (Response Surface)

> 📊 **مجموعه داده مرجع:** [`Pellet_Induration_QC_Chapter5_Dataset.xlsx`](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx)  
> 🐍 **اسکریپت مستقل پایتون:** [`ccs_prediction_rf.py`](../scripts/ccs_prediction_rf.py)  
> 🏷️ **شیت‌های مبنا:** `Fact_Process_Hourly` (۷۲۰ رکورد داده ساعتی) و `Fact_QC_Samples` (۱۸۰ رکورد نمونه‌های آزمایشگاهی با فرکانس ۴ ساعته)

---

## ۱. مقدمه متالورژیکی و صورت مسئله مهندسی کیفیت (QC)

در خطوط پخت گندله سنگ‌آهن (Straight-Grate یا Grate-Kiln)، یکی از خطاهای بزرگ متداول در تحلیل‌های علم داده سنتی، نادیده گرفتن **زمان اقامت و جابجایی (Residence & Transit Time)** گندله در طول زون‌ها است. 

از لحظه ورود گندله خام از رولرفیدر به زون‌های خشک‌ایش (`UDD`/`DDD`)، عبور از پیش‌گرمایش (`PH`) و پخت (`Firing`)، تا عبور از زون‌های سرمایش (`Cooling`)، تخلیه بر روی نوار محصول و انجام آزمون مقاومت فشاری سرد (CCS مطابق با استاندارد **ISO 4700**) در آزمایشگاه QC، بسته به سرعت پالت‌کار (`Pallet_Speed_mpm`) و ضخامت بستر (`Bed_Height_mm`)، حدود **45 دقیقه الی 1 ساعت** اختلاف فاز زمانی وجود دارد.

اگر داده‌های فرایند در ساعت $t$ مستقیماً به نتایج کیفی ساعت $t$ متصل شوند، همبستگی‌های کاذب ایجاد شده و مدل الگوهای گمراه‌کننده‌ای یاد می‌گیرد. در این کارگاه:
1. انطباق زمانی را با روش مهندسی **Rolling-Window Lag Join** پیاده‌سازی می‌کنیم.
2. با تقسیم داده مبتنی بر زمان (**Time-Based Split**)، مانع از نشت داده‌ها (**Data Leakage**) می‌شویم.
3. مدل **Random Forest Regressor** را آموزش داده و ارزیابی می‌کنیم.
4. اثر متقابل متالورژیکی دمای پخت و بازیسیته را با **رویه پاسخ (Response Surface)** استخراج و تفسیر می‌کنیم.

---

## ۲. معماری سه‌لایه‌ای داده‌های پایش کوره (QC Data Architecture)

جهت تضمین قابلیت ردیابی، دادگان فایل اکسل بر اساس استاندارد سه‌لایه‌ای مهندسی فرایند چیدمان شده‌اند:
```text
┌────────────────────────────────────────────────────────────────────────┐
│                        لایه ۱: خوراک (Feed Layer)                      │
│   Feed_Fe_pct | Feed_FeO_pct | Feed_SiO2_pct | Feed_Al2O3_pct         │
│   Feed_CaO_pct | Feed_MgO_pct | Basicity_B2 | Basicity_B4             │
│   Blaine_cm2g | Green_Moisture_pct                                    │
└───────────────────────────────────┬────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────────────────────┐
│                     لایه ۲: فرآیند کوره (Process Layer)                 │
│   Temp_UDD_C | Temp_DDD_C | Temp_PH_C | Temp_Firing_C                  │
│   Temp_AfterFiring_C | Temp_Cooling_C | Windbox_Avg_DP_kPa            │
│   Total_Gas_Flow_Nm3h | Main_Burner_Gas_Nm3h | O2_Firing_pct           │
│   Bed_Height_mm | Pallet_Speed_mpm                                     │
└───────────────────────────────────┬────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────────────────────┐
│                     لایه ۳: محصول نهایی (Product Layer)                │
│   CCS_Mean_daN | CCS_StdDev_daN | CCS_Min_daN                          │
│   ISO_Tumble_pct | Abrasion_Index_pct | Porosity_pct                   │
│   Pellets_FeO_pct | Black_Core_pct                                     │
└────────────────────────────────────────────────────────────────────────┘
```
⚠️ هشدار نشت داده (Data Leakage): هنگام تعریف متغیر هدف (CCS_Mean_daN)، هیچ‌یک از متغیرهای لایه ۳ (مانند CCS_StdDev_daN، CCS_Min_daN یا Porosity_pct) نباید به عنوان فیچر ورودی استفاده شوند، چراکه در زمان پخت کوره، این پارامترها هنوز در آزمایشگاه اندازه‌گیری نشده‌اند

. پیش‌نیازها و راه‌اندازی محیط

کتابخانه‌های مورد نیاز را در محیط پایتون نصب و فعال کنید:

```bash
pip install pandas openpyxl scikit-learn matplotlib seaborn scipy numpy
```

۴. پیاده‌سازی گام‌به‌گام در پایتون
گام ۱: بارگذاری داده‌ها و انطباق پنجره‌ای تأخیر (Lag Join)

در این بخش، میانگین شرایط کوره در پنجره ۲ ساعته منتهی به زمان نمونه‌برداری آزمایشگاه QC محاسبه و متناظر می‌شود:

```python
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.interpolate import griddata
from sklearn.ensemble import RandomForestRegressor
import arabic_reshaper

# ==========================================
# ۰. پیکربندی فونت و تابع اصلاح متن فارسی
# ==========================================
# جستجوی فونت تاهوما یا فونت‌های فارسی استاندارد ویندوز در WSL
font_candidates = [
    "/mnt/c/Windows/Fonts/tahoma.ttf",
    "/mnt/c/Windows/Fonts/segoeui.ttf",
    "/mnt/c/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

chosen_font = None
for f_path in font_candidates:
    if os.path.exists(f_path):
        fm.fontManager.addfont(f_path)
        prop = fm.FontProperties(fname=f_path)
        chosen_font = prop.get_name()
        plt.rcParams['font.family'] = chosen_font
        print(f"✅ فونت فعال شد: {chosen_font} ({f_path})")
        break

plt.rcParams['axes.unicode_minus'] = False  # برای نمایش صحیح علامت منفی (-)

def fa(text):
    """اصلاح حروف جدا شده و معکوس کردن جهت برای نمایش بی‌نقص در Matplotlib"""
    if not text:
        return text
    reshaped = arabic_reshaper.reshape(str(text))
    return reshaped[::-1]

# ==========================================
# ایجاد دایرکتوری خروجی‌ها در صورت عدم وجود
# ==========================================
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# ۱. بارگذاری فایل اکسل کارخانه
file_path = "/home/qc/Pellet_Induration_QC_Chapter5_Dataset.xlsx"
df_process = pd.read_excel(file_path, sheet_name="Fact_Process_Hourly", parse_dates=["Timestamp"])
df_qc = pd.read_excel(file_path, sheet_name="Fact_QC_Samples", parse_dates=["Sample_Timestamp"])

# مرتب‌سازی زمانی دقیق
df_process = df_process.sort_values("Timestamp").reset_index(drop=True)
df_qc = df_qc.sort_values("Sample_Timestamp").reset_index(drop=True)

# ۲. تعریف تابع استخراج میانگین شرایط کوره در پنجره [t - 2h, t)
def extract_process_window(t_sample):
    t_start = t_sample - pd.Timedelta(hours=2)
    window = df_process[(df_process["Timestamp"] >= t_start) & (df_process["Timestamp"] < t_sample)]

    if len(window) == 0:
        return pd.Series(dtype=float)

    return pd.Series({
        "Temp_UDD_C": window["Temp_UDD_C"].mean(),
        "Temp_DDD_C": window["Temp_DDD_C"].mean(),
        "Temp_PH_C": window["Temp_PH_C"].mean(),
        "Temp_Firing_C": window["Temp_Firing_C"].mean(),
        "Temp_AfterFiring_C": window["Temp_AfterFiring_C"].mean(),
        "Temp_Cooling_C": window["Temp_Cooling_C"].mean(),
        "Windbox_Avg_DP_kPa": window["Windbox_Avg_DP_kPa"].mean(),
        "O2_Firing_pct": window["O2_Firing_pct"].mean(),
        "Bed_Height_mm": window["Bed_Height_mm"].mean(),
        "Pallet_Speed_mpm": window["Pallet_Speed_mpm"].mean()
    })

# ۳. همگام‌سازی و آماده‌سازی ماتریس داده
aligned_process = df_qc["Sample_Timestamp"].apply(extract_process_window)
dataset = pd.concat([df_qc.reset_index(drop=True), aligned_process.reset_index(drop=True)], axis=1)
dataset = dataset.dropna(subset=["Temp_Firing_C"]).reset_index(drop=True)

feature_cols = [
    "Feed_Fe_pct", "Feed_SiO2_pct", "Basicity_B2", "Blaine_cm2g", "Green_Moisture_pct",
    "Temp_UDD_C", "Temp_PH_C", "Temp_Firing_C", "Temp_AfterFiring_C", "Temp_Cooling_C",
    "Windbox_Avg_DP_kPa", "O2_Firing_pct", "Bed_Height_mm", "Pallet_Speed_mpm"
]
target_col = "CCS_Mean_daN"

X = dataset[feature_cols]
y = dataset[target_col]

# تقسیم زمانی (Time-Based Split: 80% آموزش گذشته، 20% تست آینده)
split_idx = int(len(dataset) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
timestamps_test = dataset.loc[split_idx:, "Sample_Timestamp"]

# آموزش مدل Random Forest
rf_regressor = RandomForestRegressor(
    n_estimators=300, max_depth=10, min_samples_leaf=2, random_state=42, n_jobs=-1
)
rf_regressor.fit(X_train, y_train)

# پیش‌بینی روی تست
y_pred = rf_regressor.predict(X_test)

# ==========================================
# 📄 خروجی ۱: ذخیره فایل CSV نتایج تست و باقیمانده‌ها
# ==========================================
df_predictions = pd.DataFrame({
    "Sample_Timestamp": timestamps_test.values,
    "Actual_CCS_daN": y_test.values,
    "Predicted_CCS_daN": np.round(y_pred, 2),
    "Residual_Error": np.round(y_test.values - y_pred, 2),
    "Abs_Percentage_Error": np.round(np.abs((y_test.values - y_pred) / y_test.values) * 100, 2)
})
csv_path = os.path.join(output_dir, "predictions_test_set.csv")
df_predictions.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"✅ خروجی اول ذخیره شد: {csv_path}")

# ==========================================
# 📊 خروجی ۲: نمودار میله‌ای اهمیت متغیرها (Feature Importance)
# ==========================================
importances = pd.Series(rf_regressor.feature_importances_, index=feature_cols).sort_values(ascending=True)

plt.figure(figsize=(10, 6.5))
bars = plt.barh(importances.index, importances.values * 100, color="#1f77b4", edgecolor="black", alpha=0.85)

# عناوین با پوشش تابع fa()
plt.xlabel(fa("اهمیت نسبی متغیرها در پیش‌بینی مقاومت گندله (%)"), fontsize=11)
plt.title(fa("سهم عوامل فیزیکی، شیمیایی و حرارتی در مدل پخت (Random Forest Importance)"), fontsize=12, fontweight='bold')
plt.grid(axis="x", linestyle="--", alpha=0.6)

# درج برچسب درصد روی هر میله
for bar in bars:
    plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.1f}%", 
             va='center', ha='left', fontsize=9, color="black")

plt.tight_layout()
feat_imp_path = os.path.join(output_dir, "feature_importance.png")
plt.savefig(feat_imp_path, dpi=300)
plt.close()
print(f"✅ خروجی دوم ذخیره شد: {feat_imp_path}")

# ==========================================
# 🗺️ خروجی ۳: نقشه کانتوری رویه پاسخ متالورژیکی (Response Surface)
# ==========================================
temp_arr = dataset["Temp_Firing_C"].values
base_arr = dataset["Basicity_B2"].values
ccs_arr = dataset["CCS_Mean_daN"].values

grid_temp, grid_base = np.mgrid[
    temp_arr.min():temp_arr.max():150j,
    base_arr.min():base_arr.max():150j
]

grid_ccs = griddata((temp_arr, base_arr), ccs_arr, (grid_temp, grid_base), method="cubic")

plt.figure(figsize=(10, 6.5))
contour = plt.contourf(grid_temp, grid_base, grid_ccs, levels=25, cmap="turbo")
cbar = plt.colorbar(contour)
cbar.set_label(fa("میانگین مقاومت فشاری سرد گندله — CCS (daN/pellet)"), fontsize=11)

# مستطیل بهینه متالورژیکی (Sweet Spot)
plt.axvline(x=1290, color="white", linestyle="--", linewidth=1.5, alpha=0.8)
plt.axvline(x=1315, color="white", linestyle="--", linewidth=1.5, alpha=0.8)
plt.axhline(y=0.95, color="white", linestyle="--", linewidth=1.5, alpha=0.8)
plt.axhline(y=1.05, color="white", linestyle="--", linewidth=1.5, alpha=0.8)

plt.scatter(temp_arr, base_arr, c="black", alpha=0.35, s=20, edgecolors="none", label=fa("داده‌های آزمایشگاهی کوره"))

# متن‌ها و محورهای فارسی شده
plt.title(fa("رویه پاسخ متالورژیکی: اثر متقابل دمای پخت و بازیسیته بر CCS"), fontsize=12, fontweight='bold')
plt.xlabel(fa("دمای منطقه پخت کوره — Firing Temp (°C)"), fontsize=11)
plt.ylabel(fa("بازیسیته دوتایی خوراک ورودی — B2 (CaO/SiO2)"), fontsize=11)
plt.grid(True, linestyle=":", alpha=0.5)
plt.legend(loc="upper left")

plt.tight_layout()
resp_surf_path = os.path.join(output_dir, "ccs_response_surface.png")
plt.savefig(resp_surf_path, dpi=300)
plt.close()
print(f"✅ خروجی سوم ذخیره شد: {resp_surf_path}")

print("\n🎯 تمامی ۳ خروجی استاندارد با فونت تمیز و متون کاملاً درست فارسی ذخیره شدند!")
```
۵. چک‌لیست کاربردی ممیزی QC و عیب‌یابی متالورژیکی

| وضعیت متالورژیکی | شواهد رویه پاسخ | پیامد در تست‌های فیزیکی | اقدام اصلاحی سریع در اتاق کنترل |
| :--- | :--- | :--- | :--- |
| **کم‌پختی** (Under-Firing) | دمای پیک `T < 1260°C` (با هر بازیسیته) | افت شدید `CCS < 230 daN`، افزایش شاخص سایش `AI > 6.5%`، باقی‌ماندن مگنتیت | افزایش تزریق گاز برنر اصلی یا کاهش سرعت پالت‌کار |
| **پنجره بهینه** (Sweet Spot) | `1290 ≤ T ≤ 1315°C` و `0.95 ≤ B2 ≤ 1.05` | حداکثر استحکام `CCS ≥ 300 daN`، تخلخل `24-26%` و شاخص سایش عالی `AI < 5.0%` | تثبیت جریان گاز، حفظ ارتفاع بستر روی ۴۲۰ میلی‌متر |
| **بیش‌پختی** (Over-Firing) | دمای پیک `T > 1335°C` (با بازیسیته بالا) | افت مجدد `CCS`، ایجاد فاز شیشه‌ای سیلیکاتی ترد و پدیده چسبندگی (Clinkering) | کنترل اکسیژن زون پخت `O2 ≈ 13-15%` و کاهش حرارت برنرها |


۶. فایل‌های خروجی و دستاوردها

با اجرای اسکریپت در محیط پایپ‌لاین ریپازیتوری گیت‌هاب، موارد زیر به‌روزرسانی و آرشیو می‌شوند:

    📄 predictions_test_set.csv: مقایسه خط به خط مقادیر واقعی آزمایشگاه در برابر پیش‌بینی الگوریتم با درج خطای باقیمانده (Residuals).
    📊 feature_importance.png: نمودار ستونی سهم عوامل فیزیکی، شیمیایی و حرارتی در تکوین مقاومت گندله.
    🗺️ ccs_response_surface.png: نقشه کانتوری زون‌های بهینه حرارتی جهت کالیبراسیون و آموزش اپراتورهای اتاق کنترل.


---

### مزایای کلیدی این نسخه منطبق‌شده:
1. **هماهنگی ۱۰۰٪ با ستون‌های شیت‌های اکسل شما:** ستون‌هایی چون `Basicity_B2`، `Blaine_cm2g`، `Bed_Height_mm`، `Pallet_Speed_mpm` و `CCS_Mean_daN` دقیقاً مطابق با سطر هدر شیت‌های `Fact_Process_Hourly` و `Fact_QC_Samples` درج شده‌اند.
2. **پیشگیری از خطای داده‌شناسی (Data Leakage):** پارامترهای آزمایشگاهی لایه ۳ از فیچرهای ورودی حذف شدند تا مدل به دام خطای ارزیابی غیرواقعی نیافتد.
3. **فرمت آماده برای مستندسازی ریپازیتوری:** کل محتوا با Markdown استاندارد و درون تگ `<div dir="rtl">` تنظیم شده و قطعه‌کدهای LTR به‌شکل خوانا در آن جایگذاری .
