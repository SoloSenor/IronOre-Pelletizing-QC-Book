# راهنمای ساخت داشبورد قابلیت و عدم‌انطباق فرآیند در Power BI
## فصل ۸: پایش هوشمند ریسک کیفی گندله‌سازی

هدف: ایجاد یک داشبورد تعاملی برای مدیران QC جهت اتصال شاخص‌های آماری به متغیرهای فرایندی کوره پخت (Induration Furnace).

داده ورودی: شیت `data_long` از [`Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx`](../data/Chapter08_Pellet_Nonnormal_Capability_Dataset.xlsx)

---

### ۱. فرمول‌های کلیدی DAX برای پایش عدم‌انطباق

#### الف) میانگین و میانه CCS
```dax
Avg_CCS = AVERAGE('data_long'[CCS_kg])
```
```dax
Median_CCS = MEDIAN('data_long'[CCS_kg])
```

#### ب) نرخ واقعی عدم انطباق تجربی (% Below LSL)
```dax
Percent_Below_LSL = 
DIVIDE(
    CALCULATE(COUNTROWS('data_long'), 'data_long'[CCS_kg] < 250),
    COUNTROWS('data_long'),
    0
) * 100
```

#### ج) شاخص Cpl نرمال تقریبی (برای مقایسه)
```dax
Cpl_Normal = 
VAR MeanCCS = AVERAGE('data_long'[CCS_kg])
VAR StdCCS = STDEV.S('data_long'[CCS_kg])
RETURN
DIVIDE(MeanCCS - 250, 3 * StdCCS, 0)
```

#### د) تفکیک رژیم‌های عملیاتی و هشدار علت ویژه
```dax
Special_Cause_Alert = 
IF(
    SELECTEDVALUE('data_long'[Flag]) = "Special_Cause",
    "🔴 نوسان کنترل‌نشده فرایند (افت دما/گاز)",
    "🟢 پایدار تحت رژیم نرمال"
)
```

---

### ۲. چیدمان و ویژوال‌های پیشنهادی در بوم داشبورد (Canvas Layout)

1. **کارت‌های KPI بالایی (Card Visuals):**
   - کارت ۱: میانگین CCS (`Avg_CCS`) همراه با شاخص رنگی (هدف: >300).
   - کارت ۲: درصد گندله‌های زیر حد مشخصات (`Percent_Below_LSL`).
   - کارت ۳: شاخص Cpl.

2. **نمودار روند زمانی (Line Chart):**
   - محور افقی: `DateTime`
   - محور عمودی: `CCS_kg`
   - خط مرجع ثابت (Constant Line): مقدار `250` به رنگ قرمز به عنوان LSL.
   - خط روند دمای پخت (`Firing_Temp`) در محور دوم برای مشاهده همزمان اثر افت دما بر سقوط مقاومت گندله.

3. **نمودار پراکندگی علت و معلول (Scatter Plot):**
   - محور افقی: `Firing_Temp`
   - محور عمودی: `CCS_kg`
   - دسته رنگ‌ها (Legend): `Regime` (رژیم R1، R2، R3)
   - به وضوح نشان می‌دهد چولگی مقاومت گندله ناشی از کاهش دما در رژیم R3 است.

4. **نمودار توزیع فراوانی (Histogram / Clustered Column):**
   - دسته‌بندی مقاومت فشاری سرد برای نمایش بصری عدم تقارن (چولگی مثبت).
