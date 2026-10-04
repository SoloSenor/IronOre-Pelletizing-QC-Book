# Chapter 15 — Early-Warning & Closed-Loop Quality Control (CLQC)

داده‌های **شبیه‌سازی‌شده و صرفاً آموزشی** برای فصل ۱۵ (MSPC / EWDS / CLQC) — مناسب برای
تمرین در **Python (pandas/scikit-learn)، Minitab و Power BI**. این داده‌ها نباید به DCS واقعی متصل شوند.

## فایل‌ها
- `chapter15_clqc_training_data.xlsx` — ۷ شیت (شرح زیر)

## شیت‌ها
| شیت | محتوا | کاربرد آموزشی |
|---|---|---|
| `01_Process_Data` | ۲۴۰ نمونه ۱۵ دقیقه‌ای: دانسیته پالپ، دبی، فشار سیکلون، جریان آسیاب، رطوبت، خروجی سنسور نرم و نتیجه LIMS (هر ۲ ساعت، با تاخیر مرده Td=120min) | ساخت سنسور نرم، تحلیل زمان مرده، Time Alignment |
| `02_MSPC_Monitoring` | آماره‌های T² هاتلینگ، Q/SPE، EWMA (λ=0.2, L=3) با حدود کنترل و آلارم‌ها | PCA/MSPC، نمودار T² و EWMA در Minitab/Python |
| `03_Control_Loop_Log` | لاگ حلقه کنترل: بایاس آزمایشگاهی، PI، Rate Limiting و Clamping ست‌پوینت پمپ معرف | شبیه‌سازی Smith Predictor + Soft Sensor + PI |
| `04_Data_Validation` | ۸۰ نمونه آزمایشگاهی شامل خطای فاحش (5.5%)، Flat-line و Spike با نتیجه ۷ لایه اعتبارسنجی و قرنطینه | طراحی فیلتر Gross Error و منطق Quarantine/Advisory |
| `05_CLQC_Matrix` | ماتریس MV/CV جدول ۲۲ برای فلوتاسیون، سیکلون، پلتایزینگ، میکسر و کوره | مرجع طراحی حلقه‌ها |
| `06_FMEA` | حالات خرابی، علت ریشه‌ای، تشخیص و اقدام Fail-Safe | تمرین FMEA اتوماسیون |
| `07_Rollout_Plan` | مسیر ۴ مرحله‌ای Monitoring→Advisory→Supervisory→Closed-Loop | برنامه استقرار تدریجی |

## پیشنهاد تمرین
1. Python: PCA روی داده شیت ۰۱، محاسبه مجدد T²/Q و مقایسه با شیت ۰۲.
2. Minitab: نمودار EWMA و T² (Multivariate Charts) روی شیت ۰۲؛ تحلیل توانمندی عیار در شیت ۰۱.
3. Power BI: داشبورد HMI با وضعیت آلارم‌ها، Setpoint و قرنطینه (شیت‌های ۰۲، ۰۳، ۰۴).

> هشدار: تمام اعداد سنتتیک و برای آموزش هستند؛ حدود کنترل و قیود واقعی باید از شناسایی فرآیند همان کارخانه تعیین شود.

## Repository structure

| File | Description |
|---|---|
| `CHAPTER_15_FULL_TEXT.md` | Full chapter text |
| `chapter15_clqc_training_data.xlsx` | Training dataset, 7 sheets (process data, MSPC, control-loop log, validation, CLQC matrix, FMEA, rollout plan) |
| `generate_chapter15_data.py` | Reproducible synthetic data generator (numpy seed 15) |
| `clqc_simulation_tutorial.py` | Simulation tutorial script (EWMA / dead-time compensation demo) |
| `tutorials/TUTORIAL_01_PYTHON.md` | Python workflow tutorial |
| `tutorials/TUTORIAL_02_EXCEL.md` | Excel workflow tutorial |
| `tutorials/TUTORIAL_03_MINITAB.md` | Minitab workflow tutorial (I-MR, EWMA, Hotelling T², cross-correlation) |
| `tutorials/TUTORIAL_04_POWERBI.md` | Power BI dashboard tutorial (model, DAX measures, visuals) |

## Quick start
```bash
python generate_chapter15_data.py      # regenerates the xlsx dataset
python clqc_simulation_tutorial.py     # runs the EWMA/dead-time simulation
```

Open `chapter15_clqc_training_data.xlsx` in Excel/Minitab/Power BI and follow
the matching tutorial in `tutorials/`.
