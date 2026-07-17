import pandas as pd
import numpy as np
from scipy.stats import gamma, norm
import os

model_names = ["CMCC_CM2_VHR4", "FGOALS_f3_H", "HiRAM_SIT_HR", "MRI_AGCM3_2_S", "EC_Earth3P_HR", "MPI_ESM1_2_XR", "NICAM16_8S"]

def compute_spi(monthly_precip):
    values = monthly_precip.values
    positive = values[values > 0]
    if len(positive) < 10:
        return pd.Series([np.nan]*len(values), index=monthly_precip.index)
    shape, loc, scale = gamma.fit(positive, floc=0)
    prob_zero = (values == 0).mean()
    cdf = prob_zero + (1 - prob_zero) * gamma.cdf(values, shape, loc=loc, scale=scale)
    cdf = np.clip(cdf, 1e-6, 1 - 1e-6)
    return pd.Series(norm.ppf(cdf), index=monthly_precip.index)

all_spi = []
for model in model_names:
    df = pd.read_csv(f"precipitation_{model}.csv", parse_dates=["date"])
    df["year_month"] = df["date"].dt.to_period("M")
    monthly = df.groupby("year_month")["precipitation_sum"].sum()
    spi = compute_spi(monthly)
    spi_df = pd.DataFrame({"year_month": spi.index.astype(str), "SPI": spi.values, "model": model})
    all_spi.append(spi_df)
    print(f"SPI calcule -> {model}")

result = pd.concat(all_spi, ignore_index=True)
result.to_csv("spi_mensuel.csv", index=False)
print("Sauvegarde OK -> spi_mensuel.csv")
