from fmp_python.fmp import FMP
import os
import pandas as pd

os.environ["FMP_API_KEY"] = "606d643d87241cde956b5cd85a3c56d1"
fmp = FMP()

df = fmp.get_cash_flow_statement('ABT')
print(df)