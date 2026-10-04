# -*- coding: utf-8 -*-
"""
Generate chapter15_clqc_training_data.xlsx and README_chapter15.md
Synthetic training datasets for Chapter 15 (Early-Warning & Closed-Loop
Quality Control of iron ore concentrator / pelletizing plant).
Proper order: create all DataFrames -> write workbook with styling -> verify.
"""
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os

RNG = np.random.default_rng(15)
N = 240  # samples (15-min intervals => ~2.5 days)

# ---------------------------------------------------------------- 1. Process
ts = pd.date_range("2024-06-01 00:00", periods=N, freq="15min")

# latent state: slow drift + noise
state = np.cumsum(RNG.normal(0, 0.05, N)) + 0.3 * np.sin(np.linspace(0, 8*np.pi, N))

pulp_density = 1650 + 60*state + RNG.normal(0, 8, N)          # kg/m3
mass_flow    = 320  + 12*state + RNG.normal(0, 3, N)          # t/h
cyclone_press= 1.8  + 0.08*state + RNG.normal(0, 0.02, N)     # bar
mill_current = 420  + 15*state + RNG.normal(0, 5, N)          # A
feed_moisture= 8.5  + 0.2*state + RNG.normal(0, 0.1, N)       # %

# true sulfur (latent quality) + soft sensor estimate with noise
sulfur_true = 0.20 + 0.02*state + RNG.normal(0, 0.01, N)
soft_sensor = sulfur_true + RNG.normal(0, 0.015, N)           # Td ~ 0

# lab results every ~2h (8 cycles) with dead time Td=120 min (8 steps)
lab_vals = []
for i in range(N):
    j = i - 8            # dead-time delayed sample
    if i % 8 == 3 and j >= 0:
        v = sulfur_true[j] + RNG.normal(0, 0.012)
        lab_vals.append(round(float(v), 3))
    else:
        lab_vals.append(np.nan)

df = pd.DataFrame({
    "timestamp": ts,
    "pulp_density_kg_m3": pulp_density.round(1),
    "mass_flow_t_h": mass_flow.round(2),
    "cyclone_pressure_bar": cyclone_press.round(3),
    "mill_current_A": mill_current.round(1),
    "feed_moisture_pct": feed_moisture.round(2),
    "soft_sensor_sulfur_pct": soft_sensor.round(4),
    "lab_sulfur_pct": lab_vals,
})
df["data_source"] = np.where(df.lab_sulfur_pct.notna(), "LIMS_lab", "SoftSensor_online")
df["delay_Td_min"] = np.where(df.lab_sulfur_pct.notna(), 120, 0)

# ------------------------------------------- 2. Multivariate monitoring (T2/Q/EWMA)
X = df[["pulp_density_kg_m3","mass_flow_t_h","cyclone_pressure_bar",
        "mill_current_A","feed_moisture_pct"]].to_numpy()
Xs = (X - X.mean(0)) / X.std(0)
C = np.cov(Xs.T)
eigval, eigvec = np.linalg.eigh(C)
order = np.argsort(eigval)[::-1]
eigval, eigvec = eigval[order], eigvec[:, order]
a = 2
P = eigvec[:, :a]
Tscores = Xs @ P
Resid = Xs - Tscores @ P.T
T2 = np.sum(Tscores**2 / eigval[:a], axis=1)
Q  = np.sum(Resid**2, axis=1)

# 95% control limits (parametric bootstrap from in-control calibration)
cal = T2[:120]
T2_ucl = np.percentile(cal, 97.5) + 2.5
Q_ucl  = np.percentile(Q[:120], 97.5) + 1.5

lam, L, mu0, s0 = 0.2, 3.0, df.soft_sensor_sulfur_pct.mean(), 0.018
z = np.zeros(N); ewma_ucl = np.zeros(N); ewma_lcl = np.zeros(N)
for t in range(N):
    z[t] = lam*df.soft_sensor_sulfur_pct.iloc[t] + (1-lam)*(z[t-1] if t else mu0)
    f = L*s0*np.sqrt(lam/(2-lam)*(1-(1-lam)**(2*(t+1))))
    ewma_ucl[t] = mu0 + f; ewma_lcl[t] = mu0 - f

mon = pd.DataFrame({
    "timestamp": ts,
    "T2_hotelling": T2.round(3),
    "T2_UCL": round(T2_ucl, 3),
    "Q_spe": Q.round(3),
    "Q_UCL": round(Q_ucl, 3),
    "EWMA_Z": z.round(4),
    "EWMA_UCL": ewma_ucl.round(4),
    "EWMA_LCL": ewma_lcl.round(4),
    "alarm_T2": (T2 > T2_ucl).astype(int),
    "alarm_Q": (Q > Q_ucl).astype(int),
    "alarm_EWMA": ((z > ewma_ucl) | (z < ewma_lcl)).astype(int),
})
mon["mews_alarm"] = ((mon.alarm_T2 | mon.alarm_Q | mon.alarm_EWMA) > 0).astype(int)

# ------------------------------------------- 3. Control loop log (soft sensor + PI + clamping)
target, kp, ki = 0.20, 12.0, 0.8
max_step, sp_min, sp_max = 3.0, 20.0, 80.0
bias, integ = 0.0, 0.0
rows = []
sp = 45.0
for i in range(0, N, 8):
    est = df.soft_sensor_sulfur_pct.iloc[i]
    if not np.isnan(df.lab_sulfur_pct.iloc[i]):
        bias = df.lab_sulfur_pct.iloc[i] - est
    corr = est + bias
    err = corr - target
    integ = float(np.clip(integ + err, -10, 10))
    delta = float(np.clip(kp*err + ki*integ, -max_step, max_step))
    new_sp = float(np.clip(sp + delta, sp_min, sp_max))
    rows.append({
        "cycle": len(rows)+1,
        "timestamp": df.timestamp.iloc[i],
        "soft_sensor_est_pct": round(est, 4),
        "lab_bias_correction": round(bias, 4),
        "corrected_prediction_pct": round(corr, 4),
        "error_pct": round(err, 4),
        "delta_setpoint_L_h": round(delta, 2),
        "new_setpoint_reagent_pump_L_h": round(new_sp, 2),
        "mode": "Supervisory_advisory",
        "validated": "OK",
    })
    sp = new_sp
loop = pd.DataFrame(rows)

# ------------------------------------------- 4. Data validation / quarantine
raw = np.concatenate([RNG.normal(0.20, 0.02, 40), [5.5], RNG.normal(0.20, 0.02, 9),
                      [0.20]*5, RNG.normal(0.20, 0.02, 25), [0.85]])  # gross error, flatline, spike
vt = pd.date_range("2024-06-01 00:00", periods=len(raw), freq="30min")
val_rows = []; prev = raw[0]
for i, v in enumerate(raw):
    checks = []
    if v < 0 or v > 1.0: checks.append("Range_Check_FAIL")
    if prev and abs(v - prev) > 0.15: checks.append("Delta_Check_FAIL")
    if i >= 4 and raw[i-4:i+1].std() == 0: checks.append("Flatline_SUSPECT")
    status = "Quarantine" if checks else ("Advisory" if "Flatline" in str(checks) else "Accepted")
    val_rows.append({
        "sample_id": f"S{i+1:03d}", "timestamp": vt[i],
        "raw_sulfur_pct": v, "prev_value": prev,
        "checks_failed": ";".join(checks) or "-",
        "status": status,
        "route": "Manual review" if status != "Accepted" else "Control loop",
    })
    if status == "Accepted": prev = v
validation = pd.DataFrame(val_rows)

# ------------------------------------------- 5. CLQC matrix (Table 22)
matrix = pd.DataFrame([
 ["فلوتاسیون کنسانتره","دبی کلکتور/کف‌ساز و هوای ورودی (L/h)","عیار S یا SiO2 کنسانتره (%)","XRF آنلاین / LIMS","۵-۱۵","اصلاح دوز کلکتور Δu=Kp·e+Kd·de/dt"],
 ["هیدروسیکلون و آسیاب","دبی آب چاهک و فشار هیدروسیکلون (bar)","٪ ذرات زیر ۴۴µm / عدد بلین","لیزری دانه‌بندی آنلاین","۳-۸","افزایش فشار سیکلون و کاهش نرخ خوراک آسیاب"],
 ["دیسک‌های پلتایزینگ","دور و شیب دیسک، دبی آب (RPM/°)","توزیع ۹-۱۲.۵mm گندله سبز","بینایی ماشین ۳بعدی","<۰.۵","افزایش دور دیسک و افت آب زون بالا (Over-size>16mm)"],
 ["میکسر و اختلاط","نرخ بنتونیت Loss-in-Weight (%)","Drop Number و مقاومت تر","تست مکانیکی خودکار","۴۵-۶۰","پله‌های 0.05% بنتونیت + تثبیت رطوبت"],
 ["کوره پخت Traveling Grate","دبی سوخت و فن‌های مکنده","FeO (%) و CCS گندله پخته","تیتراسیون FeO / پرس فشاری","۹۰-۱۸۰","افزایش هوای زون بازیافت و دمای پیش‌گرمایش"],
], columns=["مرحله فرآیند","MV (متغیر دستکاری‌شونده)","CV (شاخص کیفیت)","سنسور بازخورد","τ (دقیقه)","منطق تغییر Setpoint"])

# ------------------------------------------- 6. FMEA
fmea = pd.DataFrame([
 ["قطعی شبکه/سرور LIMS","خطای فیزیکی شبکه یا بروزرسانی سرور","عدم دریافت داده آزمایشگاهی","Heartbeat/Watchdog 5 دقیقه","فریز bias، کار با سنسور نرم، هشدار زرد"],
 ["انسداد نمونه‌گیر خودکار","چسبندگی ذرات مرطوب در قیف","داده فریز یا تحلیل نمونه خالی","Flat-line Detection (واریانس صفر متوالی)","سوییچ به Advisory و دستور بازرسی"],
 ["انحراف کالیبراسیون XRF","کثیفی پنجره آشکارساز","مقادیر عیار نادرست پیوسته","نمودار Bland-Altman با آزمایشگاه مرجع","خروج آنالایزر از ماتریس، تعادل جرم"],
 ["اشباع محرک (پمپ دوزینگ)","رسیدن به 100% توان","ناتوانی کنترلر در اصلاح","مقایسه Readback با Setpoint","Anti-windup + هشدار بحرانی به اپراتور"],
], columns=["Failure Mode","Root Cause","اثر بر فرآیند","Detection","Fail-Safe Action"])

# ------------------------------------------- 7. Phase/rollout plan
rollout = pd.DataFrame([
 [1,"Monitoring","نمایش وضعیت و تشخیص انحراف (T2/Q/EWMA)","Advisory فقط","هفته 1-4"],
 [2,"Advisory","پیشنهاد Setpoint بدون اعمال خودکار","تایید اپراتور","هفته 5-12"],
 [3,"Supervisory","اعمال محدود اصلاحات با نظارت اپراتور","اپراتور می‌تواند Override کند","ماه 3-6"],
 [4,"Closed-Loop","اجرای خودکار با قیود و Fail-Safe","مجوز مهندسی + SAT کامل","ماه 6+"],
], columns=["مرحله","حالت","توضیح","سطح مجوز","بازه زمانی"])

# ================================================== write workbook
XLSX = "/mnt/data/chapter15_clqc_training_data.xlsx"
sheets = [
 ("01_Process_Data", df),
 ("02_MSPC_Monitoring", mon),
 ("03_Control_Loop_Log", loop),
 ("04_Data_Validation", validation),
 ("05_CLQC_Matrix", matrix),
 ("06_FMEA", fmea),
 ("07_Rollout_Plan", rollout),
]
with pd.ExcelWriter(XLSX, engine="openpyxl", datetime_format="yyyy-mm-dd hh:mm") as xw:
    for name, d in sheets:
        d.to_excel(xw, sheet_name=name, index=False)

# styling pass
wb = load_workbook(XLSX)
hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(color="FFFFFF", bold=True)
thin = Border(*[Side(style="thin", color="B0B0B0")]*4)
for name, d in sheets:
    ws = wb[name]
    ws.freeze_panes = "A2"
    for c in ws[1]:
        c.fill, c.font = hdr_fill, hdr_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for col_idx, col in enumerate(d.columns, 1):
        width = max(12, min(45, max([len(str(col))] + [len(str(v)) for v in d[col].head(50)]) + 2))
        ws.column_dimensions[get_column_letter(col_idx)].width = width
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(d.columns)):
        for c in row:
            c.border = thin
            if isinstance(c.value, float):
                c.number_format = "0.000"
wb.save(XLSX)

# ================================================== README
readme = """# فصل ۱۵ — داده‌های آموزشی مهندسی سیستم‌های هشدار زودهنگام و کنترل کیفیت حلقه‌بسته (CLQC)

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
"""
MD = "/mnt/data/README_chapter15.md"
with open(MD, "w", encoding="utf-8") as f:
    f.write(readme)

# ================================================== verification
print("=" * 60)
assert os.path.exists(XLSX) and os.path.exists(MD), "file missing!"
for name, d in sheets:
    print(f"{name:24s} rows={len(d):4d} cols={len(d.columns)}")
wb2 = load_workbook(XLSX)
assert wb2.sheetnames == [s[0] for s in sheets]
# sanity: alarms exist, loop clamps respected
assert mon.mews_alarm.sum() > 0
assert loop.new_setpoint_reagent_pump_L_h.between(sp_min, sp_max).all()
assert (validation.status == "Quarantine").sum() >= 3
print("All checks passed. Sheets:", wb2.sheetnames)
print("README bytes:", os.path.getsize(MD), "| XLSX bytes:", os.path.getsize(XLSX))
