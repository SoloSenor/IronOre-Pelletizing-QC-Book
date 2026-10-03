# 🐍 کارگاه ۳ — پایتون: Time-Lag Alignment و پیش‌بینی CCS با Random Forest

> 📥 داده: [Pellet_Induration_QC_Chapter5_Dataset.xlsx](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx) · 🧾 اسکریپت مستقل: [ccs_prediction_rf.py](../scripts/ccs_prediction_rf.py)

## هدف
اتصال نمونه‌های QC به شرایط فرایند زمان تولید متناظر (با تأخیر ۲ ساعت)، ساخت مدل پیش‌بینی CCS و ارزیابی تعمیم‌پذیری بدون نشت زمانی.

## گام ۱ — آماده‌سازی محیط
```bash
pip install pandas openpyxl scikit-learn matplotlib seaborn
python ccs_prediction_rf.py
```

## گام ۲ — Lag Join صحیح
`Sample_Timestamp` زمان برداشت/ثبت QC و `Timestamp` زمان فرایند است. برای هر نمونه، پروفایل میانگین دو ساعت قبل از نمونه‌برداری را تجمیع کنید؛ نمونه کد:

```python
import pandas as pd
path = "Pellet_Induration_QC_Chapter5_Dataset.xlsx"
p = pd.read_excel(path, sheet_name="Fact_Process_Hourly", parse_dates=["Timestamp"])
q = pd.read_excel(path, sheet_name="Fact_QC_Samples", parse_dates=["Sample_Timestamp"])
# میانگین پنجره [نمونه‌برداری-۲h, نمونه‌برداری)؛ کنترل کنید دیتاست شیفت زمانی را دقیقاً همین‌طور تعریف کرده باشد.
def process_window(t):
    w = p.loc[(p.Timestamp >= t-pd.Timedelta(hours=2)) & (p.Timestamp < t)]
    return w[["Temp_UDD_C","Temp_DDD_C","Temp_PH_C","Temp_Firing_C",
              "Temp_AfterFiring_C","Temp_Cooling_C","Windbox_Avg_DP_kPa",
              "O2_Firing_pct"]].mean()
features = q.Sample_Timestamp.apply(process_window).apply(pd.Series)
data = pd.concat([q.reset_index(drop=True), features.reset_index(drop=True)], axis=1)
```

در صورت منظور بودن تأخیر ثابت ۲ ساعت (نه میانگین پنجره)، `merge_asof` را با `direction="backward"` روی `Sample_Timestamp - pd.Timedelta(hours=2)` انجام دهید. تعریف lag را با دانش فرایند و روش تولید فایل داده تأیید کنید؛ از اتصال ردیفی مستقیم دو شیت بپرهیزید.

## گام ۳ — مدل و اعتبارسنجی
- هدف: `CCS_Mean_daN`.
- ورودی‌ها: دماهای زون، `Windbox_Avg_DP_kPa`, `O2_Firing_pct` و متغیرهای خوراک (`Blaine_cm2g`, `Basicity_B2`, `Green_Moisture_pct`). از ویژگی‌هایی مانند `CCS_StdDev_daN` یا خروجی‌های QC دیگر که هم‌زمان/پس از هدف اندازه‌گیری شده‌اند، برای پیش‌بینی عملیاتی استفاده نکنید.
- تقسیم داده بر اساس زمان (مثلاً ۸۰٪ قدیمی‌تر train، ۲۰٪ جدیدتر test)، نه shuffle تصادفی.
- مدل: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42)`؛ گزارش MAE, RMSE, R² روی test و مقایسه با baseline پیش‌بینی میانگین train.

## گام ۴ — تفسیر و نمودار پاسخ
اهمیت ویژگی‌ها یا permutation importance را روی test محاسبه کنید؛ برای اثر دو متغیر `Temp_Firing_C` و `O2_Firing_pct` بر CCS، از partial dependence استفاده کنید. نمودار رابطه را «وابستگی مدل» تفسیر کنید، نه اثبات علت.

## گام ۵ — کنترل کیفیت مدل
بررسی کنید تعداد ردیف‌های حذف‌شده به‌علت نبود داده، محدوده زمان، و پراکندگی خطا در هر کمپین. دیتاست مصنوعی/آموزشی است؛ نتایج به خط تولید واقعی تعمیم مستقیم ندارد و مدل جایگزین آزمون استاندارد CCS نیست.

## خروجی
اسکریپت مستقل CSV پیش‌بینی‌ها، متریک‌های test و نمودار اهمیت ویژگی ذخیره می‌کند؛ مسیر خروجی در راهنمای اجرای اسکریپت آمده است.
