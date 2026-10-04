# راهنمای عملی فصل ۱۳ در اکسل (Excel)

## ۱. هدف
- تمیزکاری داده‌های سری‌زمانی و شناسایی سنسورهای خراب (`Bad Quality`).
- هم‌ترازی اولیه زمان آزمایشگاه با میانگین فرآیند با `AVERAGEIFS` و `XLOOKUP`.

## ۲. گام‌های اجرایی
### گام ۱: فیلتر داده‌های نامعتبر
از ابزار Filter یا فرمول زیر استفاده کنید:
```excel
=IF(OR(C2="Bad", C2="Uncertain"), "Exclude", "Valid")
```
### گام ۲: هم‌ترازی زمان ماند
برای زمان ماند ۶۰ دقیقه، میانگین فرآیند در بازه [T-60, T]:
```excel
=AVERAGEIFS(process_timeseries!$D:$D, process_timeseries!$A:$A, ">="&(A2 - TIME(1,0,0)), process_timeseries!$A:$A, "<="&A2)
```
