import sqlite3
import pandas as pd

conn = sqlite3.connect('abastecimento_erp_v11.db')

pd.read_sql('SELECT * FROM registros',  conn).to_csv('export_registros.csv',  index=False)
pd.read_sql('SELECT * FROM veiculos',   conn).to_csv('export_veiculos.csv',   index=False)
pd.read_sql('SELECT * FROM condutores', conn).to_csv('export_condutores.csv', index=False)

conn.close()

print('Exportado com sucesso!')