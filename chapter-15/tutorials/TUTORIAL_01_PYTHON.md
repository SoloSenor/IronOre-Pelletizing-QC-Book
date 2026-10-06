# آموزش پایتون: کنترل کیفیت و سنسور نرم (فصل ۱۵)

این راهنما برای پیاده‌سازی گام‌به‌گام سیستم هشدار زودهنگام و سنسور نرم با استفاده از پایتون تدوین شده است.

## پیش‌نیازها
- نصب پایتون (نسخه ۳.۹+)
- کتابخانه‌های مورد نیاز: `pandas`, `scikit-learn`, `numpy`

## گام‌های اجرایی
1. **آماده‌سازی داده**:
   استفاده از فایل [`chapter15_clqc_training_data.xlsx`](chapter15_clqc_training_data.xlsx) و شیت `01_Process_Data`.

```python
   سلول ۱: کتابخانه‌ها، کلاس‌های مهندسی و لاجیک کنترلر

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Optional

# --- ۱. کلاس تنظیمات و قیود متالورژیکی ---
@dataclass
class QualityConstraints:
    target_value: float = 0.20        # عیار هدف گوگرد در کنسانتره (%)
    lower_spec_limit: float = 0.05    # حد پایین مشخصه فنی (%)
    upper_spec_limit: float = 0.30    # حد بالای مشخصه فنی (%)
    max_step_change: float = 3.0      # حداکثر تغییر مجاز نقطه تنظیم در هر گام (L/h)
    min_setpoint_clamp: float = 20.0  # کف فیزیکی دوزینگ پمپ معرف (L/h)
    max_setpoint_clamp: float = 80.0  # سقف فیزیکی دوزینگ پمپ معرف (L/h)
    rate_of_change_max: float = 0.15  # حداکثر پرش مجاز آزمایشگاه (Delta Check)

# --- ۲. فیلتر اعتبارسنجی داده و حذف خطاهای فاحش (LIMS Filter) ---
class DataReconciliationFilter:
    def __init__(self, constraints: QualityConstraints, memory_window: int = 5):
        self.constraints = constraints
        self.history = []
        self.memory_window = memory_window

    def validate_lab_data(self, raw_value: float) -> Tuple[bool, str]:
        # ۱. بررسی حدود امکان‌پذیر فیزیکی متالورژی
        if raw_value < 0.0 or raw_value > 5.0:
            return False, f"داده ارسالی ({raw_value:.3f}%) خارج از محدوده فیزیکی است."
        
        # ۲. بررسی جهش ناگهانی عیار نسبت به آزمون قبلی (Delta Jump)
        if self.history:
            last_valid = self.history[-1]
            delta = abs(raw_value - last_valid)
            if delta > self.constraints.rate_of_change_max:
                return False, f"جهش ناگهانی ({delta:.3f}%) بیش از حد مجاز {self.constraints.rate_of_change_max} است."
        
        self.history.append(raw_value)
        if len(self.history) > self.memory_window:
            self.history.pop(0)
        return True, "داده آزمایشگاه تایید شد."

# --- ۳. کنترلر کیفیت پیش‌بین با جبران‌ساز بایاس و Anti-windup ---
class PredictiveQualityController:
    def __init__(self, constraints: QualityConstraints, kp: float = 12.0, ki: float = 0.8):
        self.constraints = constraints
        self.kp = kp
        self.ki = ki
        self.integrated_error = 0.0
        self.bias_correction = 0.0
        self.last_bias_update_idx = -1

    def update_lab_bias(self, true_lab_val: float, past_predicted_val: float):
        """به‌روزرسانی خطای سنسور نرم بر اساس نتیجه واقعی آزمایشگاه پس از تاخیر زمانی"""
        self.bias_correction = true_lab_val - past_predicted_val

    def calculate_new_setpoint(self, current_sp: float, estimated_val: float) -> Tuple[float, float, float, float]:
        # تصحیح برآورد آنلاین سنسور نرم با آخرین بایاس معتبر آزمایشگاه
        corrected_prediction = estimated_val + self.bias_correction
        
        # محاسبه خطا نسبت به تارگت متالورژیکی (0.20% S)
        error = corrected_prediction - self.constraints.target_value
        self.integrated_error += error
        
        # جلوگیری از پدیده Windup در بخش انتگرال‌گیر
        self.integrated_error = float(np.clip(self.integrated_error, -10.0, 10.0))

        # ساختار کنترلی PI جهت اصلاح دبی پمپ معرف
        delta_adjustment = (self.kp * error) + (self.ki * self.integrated_error)

        # اعمال Rate Limiting (جلوگیری از ضربه مکانیکی به پمپ و آشفتگی سلول‌ها)
        delta_clamped = float(np.clip(
            delta_adjustment, 
            -self.constraints.max_step_change, 
            self.constraints.max_step_change
        ))

        # اعمال Bounding / Clamping فیزیکی
        new_setpoint = float(np.clip(
            current_sp + delta_clamped, 
            self.constraints.min_setpoint_clamp, 
            self.constraints.max_setpoint_clamp
        ))

        return new_setpoint, delta_clamped, error, corrected_prediction

سلول ۲: بارگذاری داده‌های واقعی فایل اکسل و اجرای پایپ‌لاین حلقه بسته

# --- بارگذاری دیتاست فصل ۱۵ ---
excel_candidates = ["chapter15_clqc_training_data-(2).xlsx", "chapter15_clqc_training_data.xlsx"]
excel_path = next((f for f in excel_candidates if os.path.exists(f)), None)

if not excel_path:
    raise FileNotFoundError("فایل اکسل داده‌های فصل ۱۵ یافت نشد! لطفا فایل را در کنار نوت‌بوک قرار دهید.")

print(f"در حال خواندن داده‌ها از: {excel_path}")
df_process = pd.read_excel(excel_path, sheet_name="01_Process_Data")
df_mspc = pd.read_excel(excel_path, sheet_name="02_MSPC_Monitoring")

# مقداردهی اولیه سیستم
constraints = QualityConstraints()
validator = DataReconciliationFilter(constraints=constraints)
controller = PredictiveQualityController(constraints=constraints, kp=12.0, ki=0.8)

# نقطه تنظیم اولیه پمپ دوزینگ معرف (L/h)
current_pump_sp = 45.0
history = []

for idx, row in df_process.iterrows():
    ts = row['timestamp']
    soft_sensor_val = row['soft_sensor_sulfur_pct']
    lab_val = row['lab_sulfur_pct']
    has_lab = pd.notna(lab_val)
    
    validation_status = "NO_SAMPLE"
    bias_updated = False

    # در صورت رسیدن گزارش آزمایشگاه LIMS (با تاخیر زمانی)
    if has_lab:
        is_valid, msg = validator.validate_lab_data(float(lab_val))
        if is_valid:
            validation_status = "ACCEPTED"
            controller.update_lab_bias(true_lab_val=float(lab_val), past_predicted_val=soft_sensor_val)
            bias_updated = True
        else:
            validation_status = "QUARANTINE"

    # محاسبه نقطه تنظیم جدید برای پمپ
    new_sp, delta_sp, error, corrected_val = controller.calculate_new_setpoint(
        current_sp=current_pump_sp,
        estimated_val=soft_sensor_val
    )
    
    history.append({
        'timestamp': ts,
        'pulp_density': row['pulp_density_kg_m3'],
        'mass_flow': row['mass_flow_t_h'],
        'soft_sensor_sulfur': soft_sensor_val,
        'lab_sulfur': lab_val if has_lab else np.nan,
        'lab_status': validation_status,
        'lab_bias': controller.bias_correction,
        'corrected_prediction': corrected_val,
        'error': error,
        'delta_sp': delta_sp,
        'pump_sp': new_sp
    })
    
    # اعمال مقدار جدید به عنوان نقطه تنظیم فعلی
    current_pump_sp = new_sp

df_sim = pd.DataFrame(history)
print(f"شبیه‌سازی با موفقیت روی {len(df_sim)} چرخه فرایندی اجرا شد.")
df_sim.head()

سلول ۳: رسم داشبورد نتایج تحلیلی متالورژیکی (Visualization)

                                                                    
fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True, dpi=120)
plt.subplots_adjust(hspace=0.25)

# ۱. پایش عیار گوگرد (سنسور نرم در برابر آزمایشگاه)
ax = axes[0]
ax.plot(df_sim['timestamp'], df_sim['soft_sensor_sulfur'], label='Soft Sensor (%S)', color='#1f77b4', lw=1.5, alpha=0.8)
ax.plot(df_sim['timestamp'], df_sim['corrected_prediction'], label='Bias-Corrected (%S)', color='#2ca02c', lw=1.5, linestyle='--')
lab_pts = df_sim.dropna(subset=['lab_sulfur'])
ax.scatter(lab_pts['timestamp'], lab_pts['lab_sulfur'], color='#d62728', s=45, zorder=5, label='LIMS Lab (%S)')
ax.axhline(constraints.target_value, color='black', linestyle=':', label=f'Target ({constraints.target_value}%)')
ax.axhline(constraints.upper_spec_limit, color='red', linestyle='-.', alpha=0.7, label=f'USL ({constraints.upper_spec_limit}%)')
ax.set_title('۱. پایش برخط عیار گوگرد و نتایج آزمایشگاه LIMS', fontsize=12, fontweight='bold')
ax.set_ylabel('عیار گوگرد (%)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True, ncol=3)

# ۲. خطای پیش‌بینی و بایاس آزمایشگاه
ax = axes[1]
ax.plot(df_sim['timestamp'], df_sim['error'], color='#ff7f0e', lw=1.5, label='Control Error (e = y_pred - y_target)')
ax.plot(df_sim['timestamp'], df_sim['lab_bias'], color='#9467bd', lw=1.2, linestyle=':', label='Lab Bias Correction')
ax.axhline(0, color='gray', lw=1)
ax.set_title('۲. خطای متالورژیکی و میزان بایاس اصلاحی مدل', fontsize=12, fontweight='bold')
ax.set_ylabel('انحراف عیار (%)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True)

# ۳. گام اصلاحی پمپ و Rate Limiting (Clamping)
ax = axes[2]
ax.step(df_sim['timestamp'], df_sim['delta_sp'], color='#8c564b', where='post', lw=1.2, label='Delta Setpoint (L/h)')
ax.axhline(constraints.max_step_change, color='orange', linestyle='--', alpha=0.7, label=f'+Rate Limit (+{constraints.max_step_change})')
ax.axhline(-constraints.max_step_change, color='orange', linestyle='--', alpha=0.7, label=f'-Rate Limit (-{constraints.max_step_change})')
ax.set_title('۳. تغییرات لحظه‌ای نقطه تنظیم و اعمال محدودساز نرخ (Rate Limiting)', fontsize=12, fontweight='bold')
ax.set_ylabel('Δ Setpoint (L/h)')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True)

# ۴. نقطه تنظیم نهایی پمپ دوزینگ معرف در DCS
ax = axes[3]
ax.plot(df_sim['timestamp'], df_sim['pump_sp'], color='#17becf', lw=2, label='Final Reagent Pump Setpoint (L/h)')
ax.axhline(constraints.max_setpoint_clamp, color='darkred', linestyle='--', alpha=0.6, label=f'Max Clamp ({constraints.max_setpoint_clamp} L/h)')
ax.axhline(constraints.min_setpoint_clamp, color='darkgreen', linestyle='--', alpha=0.6, label=f'Min Clamp ({constraints.min_setpoint_clamp} L/h)')
ax.set_title('۴. نقطه تنظیم اعمالی به کنترلر صنعتی پمپ دوزینگ (DCS Target)', fontsize=12, fontweight='bold')
ax.set_ylabel('دبی پمپ (L/h)')
ax.set_xlabel('زمان (Time)', fontsize=11)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True)

plt.tight_layout()
plt.show()
   ```
2. **سنسور نرم**:
   پیاده‌سازی مدل رگرسیونی برای تخمین گوگرد بر اساس چگالی و دبی.
3. **تحلیل چندمتغیره (MSPC)**:
   استفاده از `PCA` از کتابخانه `scikit-learn` برای محاسبه آماره‌های T² و Q مطابق کدهای ارائه‌شده در فصل.

> **نکته ایمنی**: این کدها صرفاً آموزشی هستند و برای محیط‌های عملیاتی باید طبق استانداردهای کنترل فرایند بازنویسی و اعتبارسنجی شوند.
