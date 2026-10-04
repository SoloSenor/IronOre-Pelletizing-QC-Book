# فصل ۱۴ — داشبوردهای QC در Power BI

این بسته آموزشی سه افق تصمیم‌گیری را پوشش می‌دهد: **Operational** (واکنش سریع)، **Tactical** (مقایسه شیفت‌ها) و **Strategic** (روند ماهانه). داده همراه مصنوعی و آموزشی است؛ برای استفاده صنعتی، Spec، واحدها، شیفت‌ها و اقدام‌ها را با مالک داده تأیید کنید.

## پیش‌نیازها
Power BI Desktop؛ Excel دارای Power Query و Data Model/Power Pivot؛ Python 3.10+ با pandas, openpyxl, numpy, scipy, seaborn, matplotlib, plotly؛ و Minitab برای مسیر آماری. برای داده واقعی، منطقه زمانی، تعریف ShiftDate، کیفیت داده و مجوز دسترسی نیز باید تعیین شوند.

## ساختار پوشه GitHub
```text
chapter-14-powerbi-dashboards/
├── README.md
├── CHAPTER_14_TEXT.md
├── POWER_BI_TUTORIAL.md
├── EXCEL_POWER_PIVOT_TUTORIAL.md
├── PYTHON_TUTORIAL.md
├── MINITAB_TUTORIAL.md
└── QC_Ch13_Ch14_Synthetic_Dataset.xlsx
```

## نقشه راه و فایل‌ها
1. [متن فصل ۱۴](CHAPTER_14_TEXT.md) — مفاهیم و معیارهای طراحی.
2. [دیتاست مصنوعی آموزشی](QC_Ch13_Ch14_Synthetic_Dataset.xlsx) — مدل ستاره‌ای، رکوردهای QC و KPI ماهانه.
3. [آموزش Power BI](POWER_BI_TUTORIAL.md) — مدل، DAX، سه صفحه داشبورد، RLS و Freshness.
4. [Excel Power Query و Power Pivot](EXCEL_POWER_PIVOT_TUTORIAL.md).
5. [Python](PYTHON_TUTORIAL.md) — داشبورد تعاملی و تحلیل آماری.
6. [Minitab](MINITAB_TUTORIAL.md) — آزمون شیفت، نمودار کنترل و قابلیت.

## شیت‌های دیتاست
`Dim_PlantArea`, `Dim_Material`, `Dim_Shift`, `Dim_Line`, `Dim_Operator`, `Dim_TestType`, `Dim_Parameter`, `Dim_Spec`, `Dim_ActionRule`, `Dim_DateTime`, `Dim_KPI_Target`, `Fact_QC_Result`, `Fact_Process_Tag`, `Fact_Monthly_KPI`, `README`.

> **محدودیت:** مستندات آموزشی‌اند و فایل داده منبع زنده کارخانه نیست. آزمون آماری علت اختلاف را به‌تنهایی اثبات نمی‌کند؛ Cp/Cpk فقط پس از احراز پایداری و بررسی توزیع گزارش شود. RLS در سرویس باید آزمون شود.
