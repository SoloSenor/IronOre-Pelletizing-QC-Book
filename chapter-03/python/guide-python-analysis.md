# راهنمای تحلیل داده‌محور موازنه و پایش کیفیت با Python

این اسکریپت داده‌های Excel را خوانده، موازنه آهن را بررسی کرده و رابطه میان متغیرهای جدایش، تیکنر و فیلتراسیون را تحلیل می‌کند.

---

## نصب پیش‌نیازها

```bash
pip install pandas numpy matplotlib openpyxl
```

---

## اسکریپت اجرایی

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. بارگذاری داده‌ها
file_path = "../datasets/Chapter03_QC_Separation_Dewatering_Data.xlsx"

df = pd.read_excel(
    file_path,
    sheet_name="Process_Data"
)

print(f"تعداد رکوردهای بارگذاری شده: {len(df)}")

# 2. بررسی ستون‌های ضروری
required_columns = [
    "DateTime",
    "Shift",
    "Feed_Fe_pct",
    "Concentrate_Fe_pct",
    "Fe_Balance_Error_pct",
    "Feed_Slimes_pct",
    "Liberation_pct",
    "Flotation_pH",
    "Amine_Dose_gpt",
    "Thickener_Overflow_Turbidity_NTU",
    "Thickener_Rake_Torque_pct",
    "Filter_Vacuum_kPa",
    "Filter_Cake_Moisture_pct",
    "Fe_Recovery_pct",
    "Concentrate_SiO2_pct"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"ستون‌های زیر در Dataset وجود ندارند: {missing_columns}"
    )

# 3. غربالگری موازنه آهن
anomalies = df[
    df["Fe_Balance_Error_pct"].abs() > 5.0
].copy()

print(
    "تعداد شیفت‌های دارای خطای موازنه آهن "
    f"بیش از 5 درصد: {len(anomalies)}"
)

print(
    anomalies[
        [
            "DateTime",
            "Shift",
            "Feed_Fe_pct",
            "Concentrate_Fe_pct",
            "Fe_Balance_Error_pct"
        ]
    ]
)

# 4. ماتریس همبستگی
key_vars = [
    "Feed_Slimes_pct",
    "Liberation_pct",
    "Flotation_pH",
    "Amine_Dose_gpt",
    "Thickener_Overflow_Turbidity_NTU",
    "Thickener_Rake_Torque_pct",
    "Filter_Vacuum_kPa",
    "Filter_Cake_Moisture_pct",
    "Fe_Recovery_pct",
    "Concentrate_SiO2_pct"
]

corr_matrix = df[key_vars].corr()

fig, ax = plt.subplots(figsize=(11, 8))

image = ax.imshow(
    corr_matrix,
    vmin=-1,
    vmax=1,
    aspect="auto"
)

ax.set_xticks(range(len(key_vars)))
ax.set_yticks(range(len(key_vars)))

ax.set_xticklabels(
    key_vars,
    rotation=60,
    ha="right"
)

ax.set_yticklabels(key_vars)

for i in range(len(key_vars)):
    for j in range(len(key_vars)):
        value = corr_matrix.iloc[i, j]

        ax.text(
            j,
            i,
            f"{value:.2f}",
            ha="center",
            va="center"
        )

ax.set_title(
    "Correlation Matrix: Separation, Thickening & Dewatering"
)

fig.colorbar(
    image,
    ax=ax,
    label="Pearson Correlation"
)

fig.tight_layout()

fig.savefig(
    "correlation_matrix_ch03.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# 5. Grade-Recovery Trade-off
fig, ax = plt.subplots(figsize=(9, 5))

scatter = ax.scatter(
    df["Concentrate_Fe_pct"],
    df["Fe_Recovery_pct"],
    c=df["Feed_Slimes_pct"],
    alpha=0.8
)

ax.set_xlabel("Concentrate Fe (%)")
ax.set_ylabel("Fe Recovery (%)")

ax.set_title(
    "Grade-Recovery Trade-off Colored by Feed Slimes"
)

ax.grid(
    True,
    linestyle="--",
    alpha=0.6
)

fig.colorbar(
    scatter,
    ax=ax,
    label="Feed Slimes (%)"
)

fig.tight_layout()

fig.savefig(
    "grade_recovery_tradeoff.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
```

---

## تفسیر خروجی

### موازنه آهن

اگر:

$$
|Fe\_Balance\_Error| > 5\%
$$

باشد، رکورد باید برای بررسی بیشتر علامت‌گذاری شود.

این علامت می‌تواند ناشی از:

* خطای نمونه‌برداری؛
* اختلاف زمان نمونه‌برداری جریان‌ها؛
* خطای آزمایشگاهی؛
* خطای ابزار دقیق؛
* تغییرات گذرا در فرآیند؛
* یا نادرستی یکی از داده‌های جرمی

باشد.

### همبستگی

ضریب همبستگی بالا به معنی رابطه علّی قطعی نیست.

برای مثال، اگر بین `Feed_Slimes_pct` و `Filter_Cake_Moisture_pct` همبستگی مثبت مشاهده شود، باید اثر متغیرهای مداخله‌گر مانند درصد جامد، خلأ، وضعیت پارچه و عملکرد تیکنر نیز بررسی شود.
