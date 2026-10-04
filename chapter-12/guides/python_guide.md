# راهنمای Python

وابستگی‌ها: `pip install pandas numpy scikit-learn xgboost shap matplotlib openpyxl`

اسکریپت `../scripts/run_pca_shap_analysis.py` دیتاست را از پوشه `data` می‌خواند، شش ویژگی فرآیندی را استاندارد می‌کند، PCA را محاسبه و مدل XGBoost را ارزیابی می‌کند. برای کاربرد واقعی از جداسازی train/test زمانی یا گروهی استفاده کنید؛ برازش והערכה על همان داده‌ها نمره خوش‌بینانه می‌دهد.

ویژگی‌های متوقعة: `Blaine_cm2g`, `FilterCake_Moisture_pct`, `Bentonite_pct`, `PreheatTemp_C`, `FiringTemp_C`, `Silica_pct`; هدف `CCS_kg_pellet`. نام ستون‌های واقعی را در فایل اکسل بررسی و در صورت نیاز در اسکریپت اصلاح کنید.
