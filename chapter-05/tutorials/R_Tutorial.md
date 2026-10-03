# 🔵 آموزش تحلیل دیتاست فصل ۵ در **R**

[⬅ بازگشت به README](../README.md) | [دانلود دیتاست](../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx)

## ۰- نصب پیش‌نیازها
```r
install.packages(c("readxl","tidyverse","qcc","broom"))
```

## ۱- بارگذاری دیتاست
```r
library(readxl)
library(tidyverse)
f <- "../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx"
proc <- read_excel(f, sheet="Fact_Process_Hourly")
qc   <- read_excel(f, sheet="Fact_QC_Samples")
dim  <- read_excel(f, sheet="Dim_Zones_Campaigns")
head(proc); glimpse(qc)
```

## ۲- آمار توصیفی با tidyverse
```r
proc %>% group_by(Campaign) %>%
  summarise(across(c(Temp_Firing_C, Windbox_Avg_DP_kPa),
                   list(mean=mean, sd=sd), na.rm=TRUE))
```

## ۳- تحلیل معادله ارگون
```r
ergun_dp <- function(L, dp_mm, eps, mu, rho, vs){
  dp <- dp_mm/1000
  visc <- 150*((1-eps)^2/eps^3)*(mu*vs/dp^2)
  inert<-1.75*((1-eps)/eps^3)*(rho*vs^2/dp)
  (visc+inert)*L/1000
}
ergun_dp(0.42, 12.5, 0.365, 5.35e-5, 0.222, 1.8)   # زون پخت

expand.grid(dp=c(10,12.5,14), eps=c(0.33,0.365,0.39)) %>%
  mutate(DP_kPa = mapply(ergun_dp, 0.42, dp, eps, 5.35e-5, 0.222, 1.8))
```

## ۴- نمودارهای کنترل با qcc
```r
library(qcc)
x  <- proc$Temp_Firing_C
q1 <- qcc(x, type="xbar.one", title="I-Chart: Temp_Firing_C")
mr <- qcc(diff(x), type="R", title="Moving Range")
```

## ۵- توانایی فرایند
```r
qc %>%
  mutate(Campaign = cut(row_number(), breaks=c(0,60,120,180),
                        labels=c("Camp_A","Camp_B","Camp_C"))) -> qc2
# LSL کمپین A = 280 daN
process.capability(qcc(qc2$CCS_Mean_daN[qc2$Campaign=="Camp_A"], type="xbar.one"),
                   spec.limits=c(280, Inf))
```

## ۶- رگرسیون فرایند ← کیفیت
```r
fit <- lm(Pellets_FeO_pct ~ Linked_Temp_Firing_C + Linked_O2_Firing_pct, data=qc)
summary(fit); broom::tidy(fit)

ggplot(qc, aes(Linked_Temp_Firing_C, Pellets_FeO_pct)) +
  geom_point() + geom_smooth(method="lm") + theme_minimal() +
  labs(title="FeO vs Firing Temperature")
```

## ۷- رسم روند چندمتغیره
```r
proc %>%
  select(Timestamp, Temp_UDD_C, Temp_DDD_C, Temp_PH_C, Temp_Firing_C) %>%
  pivot_longer(-Timestamp) %>%
  ggplot(aes(Timestamp, value)) + geom_line() +
  facet_wrap(~name, scales="free_y", ncol=1) + theme_minimal()
```

---
[⬅ بازگشت به README](../README.md) | [فصل ۵](../chapter/Chapter05_Text.md) | [اسکریپت کامل آماده](../scripts/analyze_chapter5.R)
