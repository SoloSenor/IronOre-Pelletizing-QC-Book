# آموزش گام‌به‌گام Minitab برای تحلیل QC فصل ۱۴

> فایل تمرین: [دیتاست مصنوعی فصل](QC_Ch13_Ch14_Synthetic_Dataset.xlsx) | [متن فصل ۱۴](CHAPTER_14_TEXT.md) | [README](README.md)
> سایر مسیرهای نرم‌افزاری: [Power BI](POWER_BI_TUTORIAL.md) | [Excel Power Pivot](EXCEL_POWER_PIVOT_TUTORIAL.md) | [Python](PYTHON_TUTORIAL.md)

Minitab ابزار مرجع برای **آزمون‌های آماری کلاسیک**، **نمودارهای کنترل استاندارد** و **تحلیل قابلیت فرآیند** است. در این فصل، Minitab را برای سه کاربرد تاکتیکی/عملیاتی به کار می‌گیریم:
1. مقایسه آماری شیفت‌ها (آیا تفاوت A/B/C واقعی است؟ — لایه Tactical در [متن فصل](CHAPTER_14_TEXT.md#۱۴-۱-تعریف-kpi-و-حدود))
2. پایش فرآیند با نمودارهای کنترل (I-MR و Xbar-R با قواعد Nelson)
3. تحلیل قابلیت فرآیند (Cp/Cpk/Pp/Ppk حتی برای داده غیرنرمال)

نسخه پیشنهادی: Minitab 21 یا جدیدتر (در نسخه‌های قدیمی‌تر مسیر منوها کمی متفاوت است). همه مثال‌ها روی `Fact_QC_Result` دیتاست مصنوعی اجرا می‌شوند.

---

## ۱. ورود داده از اکسل به Minitab

### ۱-۱. ایمپورت مستقیم
1. `File → Open → Worksheet` و در File of type گزینه **Excel (*.xlsx)** را انتخاب کنید.
2. فایل [QC_Ch13_Ch14_Synthetic_Dataset.xlsx](QC_Ch13_Ch14_Synthetic_Dataset.xlsx) را انتخاب کنید؛ Minitab فقط **یک شیت را در هر بار** باز می‌کند. شیت `Fact_QC_Result` را باز کنید.
3. در پنجره باز شدن، تیک **"Treat numbers as text if..."** را بردارید و مطمئن شوید ستون‌های زمانی به‌درستی Date/Time شناسایی شده‌اند (اگر متن شدند، از `Data → Change Data Type` اصلاح کنید).

### ۱-۲. آماده‌سازی داده (قبل از هر تحلیل)
دیتاست به فرمت Long است (هر ردیف یک نمونه-پارامتر). برای تحلیل یک پارامتر:
- در `Data → Subset Worksheet…` یک زیرمجموعه بسازید با شرط:
  - Condition: `Parameter = "Fe" And MaterialID = 2`
  - نام: `WS_Fe_Concentrate`
- برای حذف رکوردهای مشکوک، از `Data → Subset` با شرط `DataQualityFlag = "OK"` استفاده کنید (حذف نکنید؛ برای پایش کیفیت داده جدا نگه دارید — همان توصیه [Power BI](POWER_BI_TUTORIAL.md)).

### ۱-۳. Unstack کردن (تبدیل Long به ستون‌های شیفت)
برای آزمون‌های چندنمونه‌ای، داده هر شیفت باید در یک ستون باشد:
1. `Data → Unstack Columns…`
2. Unstack the data in: `Value` | Using subscripts in: `Shift`
3. After last column را انتخاب کنید و گزینه **Name the columns...** را بزنید (مثلاً پیشوند `Fe_`).
4. نتیجه: سه ستون `Fe_A`, `Fe_B`, `Fe_C` — این ستون‌ها ورودی ANOVA و Mood's Median خواهند بود.
> معکوس این عمل `Stack Columns` است (پوشه‌بندی چند ستون به فرمت Long).

### ۱-۴. مرتب‌سازی زمانی برای نمودار کنترل
- `Data → Sort…` روی ستون `SampleDateTime` (ascending)؛ نمودار کنترل به ترتیب زمانی حساس است.
- برای ساخت زیرگروه‌های شیفتی (Xbar-R): از `Calc → Make Patterned Data` یا یک ستون Subgroup بسازید، مثلاً هر ۴ نتیجه متوالی یک زیرگروه:
  `Calc → Calculator` → ذخیره در `Subgroup` → فرمول: `INT((ROW()-2)/4)+1` (در صورت وجود هدر در ردیف ۱؛ شماره ردیف اولین داده را تنظیم کنید).

---

## ۲. آزمون‌های مقایسه شیفت‌ها (لایه Tactical)

هدف: پاسخ به پرسش «آیا تفاوت میانگین Fe (یا هر KPI) بین شیفت‌های A/B/C واقعی یا ناشی از تصادف است؟» — هم‌راستا با [متن فصل، بخش ۱۴-۲](CHAPTER_14_TEXT.md).

### ۲-۱. گام صفر: بررسی نرمال بودن (پیش‌نیاز انتخاب آزمون)
1. پس از برازش One-way ANOVA، از نمودار نرمالیتی باقی‌مانده‌ها در Four-in-one استفاده کنید؛ برای آزمون رسمی، باقی‌مانده‌ها را ذخیره کرده و `Stat → Basic Statistics → Normality Test…` را اجرا کنید.
2. برای بررسی اولیه داده‌ها، Variable: ستون `Value` (مثلاً `WS_Fe_Concentrate`)؛ Test: **Anderson-Darling** (قدرتمندتر برای انحراف دنباله). فرض نرمال بودن ANOVA درباره باقی‌مانده‌های مدل است، نه لزوماً داده‌های خام تجمیع‌شده.
3. تفسیر: اگر **P-Value > 0.05** → شواهد کافی برای رد نرمال بودن نیست → ادامه با One-way ANOVA. اگر **P ≤ 0.05** → نرمال نیست → Mood's Median (بخش ۲-۴) یا تبدیل Box-Cox (بخش ۴-۳).
4. برای مشاهده گرافیکی: `Graph → Probability Plot…` (نمودار احتمال نرمال با فاصله اطمینان ۹۵٪).

### ۲-۲. One-way ANOVA
1. `Stat → ANOVA → One-Way…`
2. **Response data are in one column for all factor levels** را انتخاب کنید:
   - Response: `Value`
   - Factor: `Shift`
3. تب **Comparisons…** → تیک **Tukey** (همچنین پیشنهاد: Fisher برای جفت‌های مشخص، و تیک **Interval plot** و **Grouping Information**).
4. تب **Graphs…** → تیک **Boxplot of data** و **Four-in-one residual plots**.
5. OK.

**تفسیر:**
- در جدول ANOVA اگر **P-Value < 0.05** → حداقل یک شیفت متفاوت است.
- خروجی Tukey «Grouping» را می‌دهد: شیفت‌هایی که حرف گروه مشترک دارند تفاوت معنادار ندارند (مثلاً `A 67.2 a / B 67.0 a / C 66.6 b` یعنی C جدا افتاده).
- Interval Plot: بازه‌های اطمینان میانگین‌ها که هم‌پوشانی نداشته باشند تفاوت را نشان می‌دهند.
- بافت‌های باقی‌مانده (Residual Four-in-one) باید تقریباً تصادفی و نرمال باشند؛ الگوی منظم یعنی مدل ناقص است (مثلاً اثر روز/خط نبوده).

> توجه: اگر ساختار داده شامل روز، خط یا Batch است، اثر این عوامل را در مدل چندعاملی/آمیخته لحاظ کنید تا اختلاط اثر خط با شیفت رخ ندهد. `Fact_QC_Result` نمونه این بسته ستون LineID ندارد؛ برای چنین مدلی ابتدا Fact را با جدول تولید/خط مرتبط کنید، سپس `Stat → ANOVA → General Linear Model` به‌کار ببرید.

### ۲-۳. خروجی نتایج برای داشبورد
نتایج Tukey را کپی کنید و در بخش «یافته‌های تاکتیکی» گزارش Power BI بگذارید — نمودار رابطه‌ای شیفت‌ها در [POWER_BI_TUTORIAL.md](POWER_BI_TUTORIAL.md) (صفحه Tactical) جایگزین آزمون نیست؛ مکمل آن است.

### ۲-۴. Mood's Median Test (داده غیرنرمال)
وقتی Anderson-Darling نرمال بودن را رد می‌کند یا داده دنباله‌دار/پرت دارد:
1. `Stat → Nonparametrics → Mood's Median Test…`
2. Response: `Value` | Factor: `Shift` (یا **Samples in different columns** با ستون‌های خروجی Unstack).
3. Graphs: تیک **Boxplot**.
**تفسیر:** P-Value < 0.05 یعنی میانه حداقل یک شیفت متفاوت است. جدول `CI for eta` فاصله اطمینان میانه هر شیفت را می‌دهد.
- مقایسه: Mood's Median نسبت به پرت‌ها مقاوم است ولی قدرت (power) کمتری از ANOVA روی داده نرمال دارد — اگر نرمال بود، ANOVA را انتخاب کنید.
- گزینه‌های دیگر: `Kruskal-Wallis` (میانه‌های چندگروهی با فرض توزیع هم‌شکل) و `Levene's Test` (`Stat → ANOVA → Test for Equal Variances`) برای برابری واریانس‌ها — پیش‌نیاز ANOVA است؛ اگر واریانس‌ها نابرابر شدند از `Welch ANOVA` (گزینه **Assume unequal variances** در One-Way) استفاده کنید.

---

## ۳. نمودارهای پایش فرآیند (لایه Operational)

نمودار کنترل حد کنترل آماری می‌سازد، نه حد Spec — تفکیک مفهومی در [متن فصل، ۱۴-۱](CHAPTER_14_TEXT.md).

### ۳-۱. I-MR (تک‌اندازه‌گیری — Individuals & Moving Range)
برای پارامترهایی که هر نمونه یک بار اندازه‌گیری می‌شود (مثل نتیجه XRF نمونه‌های متوالی):
1. `Stat → Control Charts → Variables Charts for Individuals → I-MR…`
2. Variables: `Value` (داده مرتب‌شده زمانی از بخش ۱-۴).
3. `I-MR Options…` → تب **Tests** → تیک همه **آزمون‌های هشت‌گانه** (Nelson Rules):
   | # | قانون | معنی |
   |---|---|---|
   | 1 | ۱ نقطه بیرون از ۳σ | تغییر بزرگ/پرت |
   | 2 | ۹ نقطه پیاپی یک سمت مرکز | شیفت میانگین |
   | 3 | ۶ نقطه صعودی/نزولی پیاپی | روند (Trend) |
   | 4 | ۱۴ نقطه با بالا/پایین متناوب | نوسان غیرتصادفی |
   | 5 | ۲ از ۳ نقطه در ناحیه ۲σ (هم‌سمت) | هشدار زودهنگام |
   | 6 | ۴ از ۵ نقطه در ناحیه ۱σ (هم‌سمت) | شیفت کوچک |
   | 7 | ۱۵ نقطه در ناحیه ۱σ (دو سمت) | حدود بیش‌ازحد باز/داده ترکیبی |
   | 8 | ۸ نقطه پیاپی بیرون ۱σ (بدون پشت‌سرهم بودن سمت) | مخلوط بودن دو فرآیند |
4. تب **Estimate** → روش پیش‌فرض Average Moving Range نگه دارید؛ در صورت وجود روند، گزینه **Median MR** مقاوم‌تر است.
5. تب **Display** → می‌توانید **Limit the number of subgroups** بگذارید تا فقط دوره پایدار مبنای حدود شود (Phase 1).
**تفسیر:** هر نقطه قرمز = نقض یک قانون (شماره قانون کنار نقطه درج می‌شود). قبل از هر محاسبه Cpk (بخش ۴) فرآیند باید «In Control» باشد.

### ۳-۲. Xbar-R (زیرگروه‌های شیفتی)
وقتی در هر شیفت چند اندازه‌گیری دارید (زیرگروه ۲≤n≤10) — مثلاً ۴ نتیجه Fe در هر شیفت:
1. زیرگروه‌سازی را طبق بخش ۱-۴ انجام دهید (ستون `Subgroup`).
2. `Stat → Control Charts → Variables Charts for Subgroups → Xbar-R…`
3. **All observations for a chart are in one column** → Chart values: `Value` | Subgroup sizes: `Subgroup`.
4. در `Xbar-R Options → Tests` همه ۸ آزمون Nelson را فعال کنید.
5. تب **Box-Cox** در همان Options: اگر داده لگ‌نرمال بود، Minitab λ را برآورد و خودکار اعمال می‌کند (برای جزئیات بخش ۴-۳ را ببینید).
**تفسیر:** نمودار بالایی (Xbar) پایداری میانگین بین زیرگروه‌ها، نمودار پایینی (R) پایداری پراکندگی درون زیرگروه را نشان می‌دهد. اگر فقط R بی‌ثبات است، اول عامل پراکندگی (نمونه‌برداری/آزمونگاه) را پیدا کنید.

> برای داده با واریانس همبسته (Autocorrelation)، I-MR کلاسیک ممکن است هشدار کاذب بدهد؛ در این حالت از `Stat → Control Charts → Time-Weighted Charts → EWMA/CUSUM` استفاده کنید و خودهمبستگی را جداگانه بررسی کنید. مجموعه تمرین مکمل خارج از این پکیج گیت‌هاب نگهداری می‌شود.

---

## ۴. تحلیل قابلیت فرآیند (لایه Strategic)

**ترتیب اجباری:** ۱) پایداری (نمودار کنترل بخش ۳) → ۲) نرمال بودن (بخش ۲-۱) → ۳) گزارش قابلیت. گزارش Cpk روی فرآیند ناپایدار، عددی بی‌معناست.

### ۴-۱. Normal Capability (داده نرمال)
1. `Stat → Quality Tools → Capability Analysis → Normal…`
2. Single column: `Value` | Subgroup size: `1` (یا ستون Subgroup برای Xbar-R).
3. Lower spec / Upper spec را از شیت `Dim_Spec` (مثلاً Fe: LSL=66.5, USL=68.5) وارد کنید — و نسخه Spec (EffectiveFrom) را حتماً با دوره داده تطبیق دهید.
4. تب **Options** → Target را وارد کنید و **Include confidence intervals** و گزینه Benchmark Z را بگذارید.
**خروجی و تفسیر شاخص‌ها:**

| شاخص | تعریف | حداقل قابل قبول صنعتی |
|---|---|---|
| Cp | قابلیت بالقوه = (USL−LSL)/6σ_within (بدون توجه به مرکز بودن) | ≥ 1.33 |
| Cpk | قابلیت واقعی = min(CPU, CPL) — نزدیکی میانگین به نزدیک‌ترین حد | ≥ 1.33 |
| Pp | همان Cp با σ کلی (Overall, بلندمدت) | ≥ 1.33 |
| Ppk | همان Cpk با σ کلی | ≥ 1.33 |

- **شکاف Cpk و Ppk:** اگر Cpk ≫ Ppk باشد، واریانس درون‌زیرگروهی کوچک است ولی بین‌زیرگروهی شیفت دارد → فرآیند در بلندمدت ناپایدار/دریفت‌دار است؛ اول علت شیفت (مثلاً تفاوت شیفت‌ها از بخش ۲) را برطرف کنید.
- **Cpk منفی/نزدیک صفر:** میانگین فرآیند خارج یا چسبیده به Spec → اقدام فوری.
- **σ Within vs Overall:** Within از MR یا زیرگروه‌ها برآورد می‌شود؛ Overall انحراف معیار همه داده است.
- در خروجی Minitab بخش «Observed/Expected PPM» تعداد کالاهای خارج از Spec را پیش‌بینی می‌کند؛ برای گزارش ماهانه به `Fact_Monthly_KPI` (ستون `Cpk_Fe`) در داشبورد [Power BI](POWER_BI_TUTORIAL.md) وصل کنید.

### ۴-۲. ارزیابی فرض نرمال بودن
1. `Stat → Basic Statistics → Normality Test…` → **Anderson-Darling** روی همان ستون.
2. همزمان `Capability Analysis → Normal` خودش در پنل خروجی P-Value Anderson-Darling را گزارش می‌کند.
3. تفسیر: P > 0.05 → نرمالیتی رد نمی‌شود، ادامه با Normal Capability. P ≤ 0.05 → به ۴-۳ بروید.
4. اگر فقط دنباله سمت بالا/پایین انحراف دارد، Probability Plot نقاط را از خط جدا می‌کند؛ جهت انحراف را در انتخاب تبدیل در نظر بگیرید.

### ۴-۳. Box-Cox و Johnson Transformation (داده غیرنرمال)
**Box-Cox (نیازمند مقادیر مثبت):**
1. `Stat → Quality Tools → Capability Analysis → Nonnormal…`
2. Distribution: **Box-Cox transformation**؛ وارد کردن Specها مثل ۴-۱.
3. در `Options → Transform` می‌توانید گزینه **Store transformed values** را بزنید تا λ و داده تبدیل‌شده ذخیره شود.
4. Minitab λ بهینه را پیدا می‌کند (مثلاً λ=−0.5 یعنی 1/√y). شاخص‌ها روی مقیاس تبدیل‌شده گزارش می‌شوند — در گزارش بنویسید که بر پایه تبدیل Box-Cox (λ=...) است.
> محدودیت: Box-Cox با مقادیر صفر/منفی کار نمی‌کند (مثل رکوردهای منفی دیتاست برای برخی پارامترها — ابتدا داده را بررسی/اصلاح کنید یا روش دیگر بگیرید).

**Johnson Transformation (بدون محدودیت علامت):**
1. `Stat → Quality Tools → Johnson Transformation…` → Variable: `Value` → OK.
2. Minitab بهترین تابع (SB/SL/SU) و P-Value نرمالیتی پس از تبدیل را گزارش می‌دهد؛ سپس با ستون تبدیل‌شده Capability Normal اجرا کنید.
3. نتیجه را در گزارش علامت‌گذاری کنید؛ عدد Ppk روی مقیاس تبدیل‌شده برای مقایسه با Spec فیزیکی مستقیم نیست و باید با احتیاط تفسیر شود (همان هشدار «محدودیت» در [README](README.md)).

**Capability Sixpack:** برای گزارش حسابرسی‌پذیر از `Stat → Quality Tools → Capability Sixpack → Normal` استفاده کنید؛ در یک صفحه، نمودار کنترل Xbar/R (یا I-MR)، Last 25 observations، Normal Probability Plot و شاخص‌ها را می‌دهد — ترکیب کامل بخش ۳ و ۴.

---

## ۵. چک‌لیست خروجی Minitab برای گزارش فصل ۱۴

- [ ] زیرمجموعه پارامتر/ماده مشخص، داده مرتب زمانی، `DataQualityFlag = OK` (بخش ۱)
- [ ] Anderson-Darling گزارش شد و آزمون متناسب (ANOVA / Mood's Median) انتخاب شد (بخش ۲)
- [ ] Tukey Grouping و Interval Plot در گزارش تاکتیکی آمده است
- [ ] I-MR یا Xbar-R با ۸ آزمون Nelson و برچسب نقض‌ها (بخش ۳)
- [ ] قبل از Cpk: فرآیند In Control بوده (بخش ۴)
- [ ] Cp/Cpk/Pp/Ppk با تفکیک Within/Overall و نسخه Spec مندرج (بخش ۴-۱)
- [ ] برای داده غیرنرمال: نوع تبدیل (Box-Cox/Johnson) و λ یا تابع Johnson ثبت شده (بخش ۴-۳)
- [ ] نتیجه‌ها به داشبورد [Power BI](POWER_BI_TUTORIAL.md) یا [Excel Power Pivot](EXCEL_POWER_PIVOT_TUTORIAL.md) منتقل و با [Python](PYTHON_TUTORIAL.md) به‌عنوان مسیر دوم اعتبارسنجی شد

---

## ۶. سایر آموزش‌های این بسته
- [متن کامل فصل ۱۴](CHAPTER_14_TEXT.md) — مفاهیم سه‌لایه داشبورد و معماری داده
- [POWER_BI_TUTORIAL.md](POWER_BI_TUTORIAL.md) — مدل، DAX و سه صفحه داشبورد
- [EXCEL_POWER_PIVOT_TUTORIAL.md](EXCEL_POWER_PIVOT_TUTORIAL.md) — Power Query و Power Pivot
- [PYTHON_TUTORIAL.md](PYTHON_TUTORIAL.md) — تحلیل آماری و داشبورد تعاملی
- [README.md](README.md) — نقشه راه، پیش‌نیازها و محدودیت‌های بسته
