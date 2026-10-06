# -*- coding: utf-8 -*-
"""
پیوست ۲: شروع کار با پایتون برای مهندسی کیفیت — SPC و توانمندی فرایند
--------------------------------------------------------------------
پیش‌نیاز (نصب در Terminal یا CMD):
    pip install numpy pandas matplotlib seaborn scipy openpyxl
"""

# ============================================================
# ۱. نقشه راه و ابزارهای مورد نیاز
# ============================================================
# چهار کتابخانه اصلی پایتون مثل چهار عنصر حیات (یا بهتر بگویم:
# فیدر، بالمیل، هیدروسیکلون و درام مگنت!) عمل می‌کنند:
#
#   - Pandas:      جدول‌بندی، کار با تایم‌سریزها، خواندن اکسل/CSV و تمیزکاری دیتای پرت
#   - NumPy:       محاسبات برداری، ماتریس‌ها و جبر خطی سریع
#   - Matplotlib & Seaborn: رسم نمودارهای استاندارد، توزیع داده، Scatter و Boxplot
#   - SciPy (stats): آزمون‌های نرمال بودن، حدود کنترل آماری (SPC) و شاخص‌های توانمندی

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# تنظیم استایل پیش‌فرض برای گزارش‌های مهندسی شیک و تمیز
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

# ============================================================
# ۲. راه‌اندازی و ورود داده‌ها (Data Ingestion)
# ============================================================
# در آزمایشگاه‌های QC، خروجی‌ها معمولاً فایل اکسل آزمایشگاه شیمی (XRF)
# یا سیستم اسکادا (SCADA) خط است:
#
# df = pd.read_excel('pellet_plant_qc_data.xlsx')

# برای تست، یک دیتای شبیه‌سازی‌شده از پارامترهای گندله‌سازی می‌سازیم:
np.random.seed(42)
n_samples = 200

data = {
    'Timestamp': pd.date_range(start='2026-01-01', periods=n_samples, freq='h'),
    'Fe_Total':  np.random.normal(loc=67.2, scale=0.35, size=n_samples),  # درصد آهن کنسانتره
    'SiO2':      np.random.normal(loc=1.85, scale=0.15, size=n_samples),  # درصد سیلیس
    'Blaine':    np.random.normal(loc=1850, scale=45,  size=n_samples),   # سطح ویژه بلین (cm2/g)
    'Moisture':  np.random.normal(loc=9.2,  scale=0.4,  size=n_samples),  # رطوبت کیک فیلتر
    'Pellet_CCS': np.random.normal(loc=265, scale=25,  size=n_samples)    # استحکام فشاری گندله پخته (daN)
}

df = pd.DataFrame(data)

# نگاه سریع به ۵ سطر اول
print("=== 5 سطر اول دیتا ===")
print(df.head())

# ============================================================
# ۳. خلاصه آماری و غربالگری داده‌ها (EDA)
# ============================================================
# اولین کار رئیس QC قبل از هر نتیجه‌گیری: آمار توصیفی!

qc_summary = df.describe().T[['mean', 'std', 'min', '50%', 'max']]
qc_summary.columns = ['Mean', 'Std_Dev', 'Min', 'Median (Q2)', 'Max']
print("\n=== خلاصه آماری پارامترهای کلیدی فرایند ===")
print(qc_summary)

print("\nتعداد داده‌های خالی در هر ستون:")
print(df.isnull().sum())

# ============================================================
# ۴. مصورسازی داده‌ها و نمودارهای پایش کیفیت
# ============================================================

# الف) نمودار جعبه‌ای (Boxplot) جهت تشخیص داده‌های پرت (Outliers)
plt.figure(figsize=(8, 4))
sns.boxplot(x=df['SiO2'], color='salmon')
plt.title('Boxplot of SiO2% - شناسایی داده‌های پرت سیلیس')
plt.xlabel('SiO2 (%)')
plt.tight_layout()
plt.show()

# ب) ماتریس همبستگی (Heatmap): اثر متقابل متغیرها
# آیا بالا رفتن رطوبت و بلین روی استحکام گندله سبز و نهایتاً CCS اثر منفی گذاشته است؟
plt.figure(figsize=(7, 5))
correlation_matrix = df[['Fe_Total', 'SiO2', 'Blaine', 'Moisture', 'Pellet_CCS']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title('ماتریس همبستگی پارامترهای فیزیکی-شیمیایی گندله')
plt.tight_layout()
plt.show()

# ============================================================
# ۵. محاسبه شاخص‌های کنترل آماری فرآیند (SPC) و توانمندی (Cp, Cpk)
# ============================================================
# تبدیل تئوری‌های SPC به کدهای یک‌خطی!
# فرض: حد مشخصات مهندسی (Tolerance Limits) برای عیار آهن کنسانتره:
#   USL (Upper Specification Limit): 68.0%
#   LSL (Lower Specification Limit): 66.5%

fe = df['Fe_Total']
usl = 68.0
lsl = 66.5
mean_fe = fe.mean()
# در صنعت معمولاً برای Cpk از انحراف معیار نمونه استفاده می‌شود:
sigma_fe = fe.std(ddof=1)

# محاسبه شاخص‌های پتانسیل و کارایی فرایند
cp  = (usl - lsl) / (6 * sigma_fe)
cpu = (usl - mean_fe) / (3 * sigma_fe)
cpl = (mean_fe - lsl) / (3 * sigma_fe)
cpk = min(cpu, cpl)

print(f"میانگین آهن: {mean_fe:.3f}% | انحراف معیار: {sigma_fe:.3f}")
print(f"شاخص پتانسیل فرایند (Cp):   {cp:.2f}")
print(f"شاخص توانمندی فرایند (Cpk): {cpk:.2f}")

if cpk < 1.33:
    print("⚠️ وضعیت هشدار: فرایند نیازمند بهینه‌سازی پارامترهای فلوتاسیون/مگنتیک است!")
else:
    print("✅ وضعیت عالی: فرایند کاملاً در کنترل و توانمند است.")

# ============================================================
# ۶. رسم نمودار کنترل شوهارت (Shewhart Control Chart - I Chart)
# ============================================================
# نمودار کنترل روند انفرادی متغیر عیار آهن (X-Chart)
# با خطوط میانگین و حدود ±3σ:

ucl = mean_fe + 3 * sigma_fe
lcl = mean_fe - 3 * sigma_fe

plt.figure(figsize=(12, 5))
plt.plot(df['Timestamp'], fe, marker='o', markersize=3, linestyle='-',
         color='navy', label='Fe Sample')
plt.axhline(mean_fe, color='green', linestyle='--', label=f'CL (Mean: {mean_fe:.2f})')
plt.axhline(ucl, color='red', linestyle='--', label=f'UCL (+3σ: {ucl:.2f})')
plt.axhline(lcl, color='red', linestyle='--', label=f'LCL (-3σ: {lcl:.2f})')

# مشخص کردن نقاط خارج از کنترل (Out-of-Control)
out_of_control = df[(fe > ucl) | (fe < lcl)]
plt.scatter(out_of_control['Timestamp'], out_of_control['Fe_Total'],
            color='darkred', s=60, zorder=5, label='OOC Signal')

plt.title('نمودار کنترل انفرادی عیار آهن (Fe Total Control Chart - I Chart)')
plt.xlabel('زمان نمونه‌برداری')
plt.ylabel('درصد Fe')
plt.legend(loc='lower left')
plt.tight_layout()
plt.show()
