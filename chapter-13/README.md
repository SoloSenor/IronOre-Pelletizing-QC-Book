# فصل ۱۳: معماری داده کارخانه (از PLC و SCADA تا دریاچه‌داده)
> راهنمای جامع و تمرین‌های عملی پیاده‌سازی کنترل کیفیت داده‌محور در صنایع کنسانتره و گندله‌سازی آهن

این مخزن شامل متن کامل، مجموعه داده‌های آموزشی استاندارد و راهنماهای گام‌به‌گام پیاده‌سازی برای فصل سیزدهم کتاب است.

---

## 📂 ساختار مخزن (Repository Structure)
```text
├── README.md
├── Chapter13_Theory.md
├── data/
│   ├── ch13_factory_data_architecture_training.xlsx
│   └── ch13_process_timeseries_2days.csv
├── tutorials/
│   ├── Excel_Guide.md
│   ├── Minitab_Guide.md
│   ├── Python_Guide.md
│   └── PowerBI_Guide.md
└── scripts/
    └── time_alignment_spc_demo.py
```

## 📊 مشخصات مجموعه داده
- **process_timeseries**: داده‌های سری‌زمانی شامل متغیرهای PV/SP/MV و کیفیت سیگنال.
- **event_log**: رخدادهای فرآیندی، آلارم‌ها و توقف تجهیزات.
- **qc_lab_results**: نتایج آزمایشگاهی و زمان ماند.
- **batch_campaigns**, **shifts**, **asset_hierarchy** و **tag_dictionary**: اطلاعات کمپین، شیفت، دارایی‌ها و تگ‌ها.

## 🚀 راهنماهای آموزشی
- [آموزش اکسل](tutorials/Excel_Guide.md)
- [آموزش مینی‌تب](tutorials/Minitab_Guide.md)
- [آموزش پایتون](tutorials/Python_Guide.md)
- [آموزش پاور بی‌آی](tutorials/PowerBI_Guide.md)
