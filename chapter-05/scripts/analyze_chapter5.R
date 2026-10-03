# اسکریپت تحلیل کامل دیتاست فصل ۵ در R
library(readxl); library(tidyverse); library(qcc)
f <- "../data/Pellet_Induration_QC_Chapter5_Dataset.xlsx"
proc <- read_excel(f, sheet="Fact_Process_Hourly")
qc   <- read_excel(f, sheet="Fact_QC_Samples")

print(proc %>% group_by(Campaign) %>%
        summarise(across(Temp_Firing_C, list(mean=mean, sd=sd))))

ergun_dp <- function(L, dp_mm, eps, mu, rho, vs){
  dp <- dp_mm/1000
  visc <- 150*((1-eps)^2/eps^3)*(mu*vs/dp^2)
  inert<-1.75*((1-eps)/eps^3)*(rho*vs^2/dp)
  (visc+inert)*L/1000
}
print(paste("DP_Firing =", round(ergun_dp(0.42,12.5,0.365,5.35e-5,0.222,1.8),3), "kPa"))

qcc(proc$Temp_Firing_C, type="xbar.one", title="I-Chart: Temp_Firing_C")

fit <- lm(Pellets_FeO_pct ~ Linked_Temp_Firing_C + Linked_O2_Firing_pct, data=qc)
print(summary(fit))
