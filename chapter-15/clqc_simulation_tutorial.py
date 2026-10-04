"""آزمایشگاه آموزشی CLQC فصل ۱۵؛ شبیه‌سازی، نه اتصال به DCS واقعی."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).with_name("chapter15_clqc_training_data.xlsx")
SEED = 15

def load_data(path=DATA):
    if not Path(path).exists():
        raise FileNotFoundError(f"فایل داده کنار اسکریپت پیدا نشد: {path}")
    xls = pd.ExcelFile(path)
    raw = pd.read_excel(path, sheet_name="01_Process_Data")
    monitor = pd.read_excel(path, sheet_name="02_MSPC_Monitoring")
    print("Sheets:", xls.sheet_names)
    print("Process rows/columns:", raw.shape)
    return raw, monitor

def pca_monitor(df):
    cols = ["pulp_density_kg_m3", "mass_flow_t_h", "cyclone_pressure_bar", "mill_current_A", "feed_moisture_pct"]
    X = df[cols].dropna().to_numpy(float)
    scaler = StandardScaler().fit(X)
    Z = scaler.transform(X)
    model = PCA(n_components=0.90, svd_solver="full").fit(Z)
    T = model.transform(Z)
    T2 = np.sum((T**2) / model.explained_variance_, axis=1)
    reconstructed = model.inverse_transform(T)
    Q = np.sum((Z - reconstructed)**2, axis=1)
    print(f"PCA: {model.n_components_} PCs, explained={model.explained_variance_ratio_.sum():.3f}")
    print("Illustrative empirical 99% limits (Phase-I only):", np.quantile(T2,.99), np.quantile(Q,.99))
    print("T2/Q first five:", list(zip(np.round(T2[:5],3), np.round(Q[:5],3))))
    return T2, Q

def validate(value, previous=None, timestamp_age_min=0, quality="Good", low=0.0, high=2.0, max_delta=.08, max_age=30):
    errors=[]
    if not np.isfinite(value) or not low <= value <= high: errors.append("range/non-finite")
    if quality != "Good": errors.append("bad quality flag")
    if timestamp_age_min < 0 or timestamp_age_min > max_age: errors.append("stale/future timestamp")
    if previous is not None and abs(value-previous)>max_delta: errors.append("delta check")
    return (not errors, errors)

def ewma(values, lam=.2):
    z=[]
    for i,v in enumerate(values): z.append(v if i==0 else lam*v+(1-lam)*z[-1])
    return np.array(z)

def smith_predictor_demo(n=120, delay=8, seed=SEED):
    """فرایند مرتبه اول با تاخیر؛ نمایش مفهومی پیش‌بینی اسمیت."""
    rng=np.random.default_rng(seed); u=np.zeros(n); y=np.zeros(n); yhat=np.zeros(n)
    u[10:]=1.0
    a=.92; b=.08
    for k in range(1,n):
        uk=u[max(0,k-delay)]
        y[k]=a*y[k-1]+b*uk+rng.normal(0,.003)
        # مدل موازیِ بدون تاخیر و مدل با تأخیر؛ تخمین خروجی جاری با تصحیح اختلاف
        yhat[k]=a*yhat[k-1]+b*u[k-1]
    print("Smith demo final (delayed plant / predictor):", round(y[-1],3), round(yhat[-1],3))
    return y,yhat

def pi_step(sp, measured, integral, target=.20, kp=-2.0, ki=-.08, dt=1., step_max=.5, lo=20., hi=70.):
    """PI نمونه؛ بهره منفی فرضی برای جهت اثر خاص این مثال است، نه مقدار صنعتی."""
    err=measured-target
    trial_i=np.clip(integral+err*dt,-5.,5.)
    raw=kp*err+ki*trial_i
    delta=np.clip(raw,-step_max,step_max) # rate limit
    new=float(np.clip(sp+delta,lo,hi))     # actuator clamp
    # anti-windup: حفظ انتگرال قبلی در صورت حرکت بیشتر به داخل اشباع
    if new in (lo,hi) and np.sign(raw)==np.sign(new-sp): trial_i=integral
    return new,trial_i,err

def main():
    np.random.seed(SEED)
    df, mon=load_data()
    pca_monitor(df)
    print("Validation examples:", validate(.21,.20), validate(5.5,.20), validate(.22,.20,90))
    cols=["pulp_density_kg_m3","mass_flow_t_h"]
    train=df.dropna(subset=cols+["soft_sensor_sulfur_pct"])
    if len(train):
        X=np.c_[np.ones(len(train)),train[cols].to_numpy()]
        coef=np.linalg.lstsq(X,train.soft_sensor_sulfur_pct.to_numpy(),rcond=None)[0]
        print("Soft sensor linear coefficients [intercept, density, flow]:",np.round(coef,7))
    lab=df.lab_sulfur_pct.dropna()
    if len(lab): print("Lab samples:",len(lab),"mean bias (lab-soft):",round((df.loc[lab.index,"lab_sulfur_pct"]-df.loc[lab.index,"soft_sensor_sulfur_pct"]).mean(),5))
    z=ewma(df.soft_sensor_sulfur_pct.dropna().to_numpy(),.2)
    print("EWMA last value:",round(z[-1],4))
    smith_predictor_demo()
    sp=45.; integ=0.
    for meas in [.22,.24,.21]: sp,integ,e=pi_step(sp,meas,integ); print(f"PI: error={e:+.3f}, reagent_SP={sp:.2f}, I={integ:.3f}")
    print("Monitoring sheet MEWS alarms:",int(mon.mews_alarm.sum()))
    print("Educational simulation completed. Never connect this script directly to a live DCS.")

if __name__ == "__main__": main()
