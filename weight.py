import re
import httpx
import asyncio
import numpy as np
import pandas as pd

INDEXLIST=[
    "NIFTY 50",
    "NIFTY BANK",
    "NIFTY FINANCIAL SERVICES",
    "NIFTY MIDCAP SELECT",
    "NIFTY NEXT 50",
    "NIFTY 100",
    "NIFTY 200",
    "NIFTY 500",
    "NIFTY TOTAL MARKET",
    "NIFTY OIL & GAS",
    "NIFTY CONSUMER DURABLES",
    "NIFTY ENERGY",
    "NIFTY AUTO",
    "NIFTY METAL",
    "NIFTY PHARMA",
    "NIFTY PRIVATE BANK",
    "NIFTY PSU BANK",
    "NIFTY REALTY",
    "NIFTY FMCG",
    "NIFTY HEALTHCARE",
    "NIFTY IT",
    "NIFTY MEDIA"
]

async def AsyncIndicesWeightClosure(CLIENT, SEMAPHORE, INDEX) -> pd.DataFrame:
    URL=fr"https://blob.niftyindices.com/jsonfiles/SectorialIndex/SectorialIndexData{INDEX}.js"
    
    async with SEMAPHORE:
        RESULT=await CLIENT.get(URL)

    DF=pd.Series([R.string[R.end()+3:R.end()+50] for R in re.finditer("label", RESULT.text)])
    DF=DF.str.split(",").str[0].str[:-2]
    DF=DF[~DF.str.split(" ").str[0].str.contains("\"")]
    DF=DF[DF.str.split(" ").str[0].str.isupper()]
    DF=pd.DataFrame(DF.str.split(" ", expand=True).values, columns=["symbol", "weight"])
    DF["weight"]=DF["weight"].astype(np.float64)
    DF["indice"]=INDEX
    DF=DF.sort_values("weight", ascending=False)
    
    print(INDEX)

    return DF

async def AsyncIndicesWeight(HEADER) -> list:
    CLIENT=httpx.AsyncClient(headers=HEADER)
    SEMAPHORE=asyncio.Semaphore(3)

    APOOL=[asyncio.create_task(AsyncIndicesWeightClosure(CLIENT, SEMAPHORE, I)) for I in INDEXLIST]

    RESULT=await asyncio.gather(*APOOL)

    return RESULT

HEADER={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"}
RESULT=asyncio.run(AsyncIndicesWeight(HEADER))
DF=pd.concat(RESULT).reset_index(drop=True)

WRITER=pd.ExcelWriter("IndexWeight.xlsx", engine="openpyxl")
COLDIM={"A":20, "B":10}
for I in DF["indice"].unique():
    DF[DF["indice"]==I].drop("indice", axis=1).to_excel(WRITER, sheet_name=I, index=False)
    for C in ["A", "B"]:
        WRITER.sheets[I].column_dimensions[C].width=COLDIM[C]

WRITER.close()