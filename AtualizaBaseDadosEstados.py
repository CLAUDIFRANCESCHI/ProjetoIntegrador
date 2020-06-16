# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 18:57:11 2020 
Interface com banco de Dados SQLite para escrever os arquivos 
selecionados na internet. 

@author: UT0K
"""
import sqlite3
import pandas as pd
import csv 
     
#Importa aqquivo tipo CVS
def import_csv_from_site(location):     
    cr = csv.reader(open(location,"rb"))
    return cr

#Conecta o banco de dados de trabalho
def create_connection(db_file):     
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print("Erro ao conectar")
    return conn

# Verifica a ultima Data importada para o banco de dados.
banco_dados = "C:\\Users\\ut0k\\Desktop\\Estudos\\PosGraducaoCienciaDeDados\\PosGraducaoUTFprCienciaDados\\ProjetoIntegrador1\\Covid19\\covid19.db"
sqlquery = "Select max(data) datas from Casos_Estados;"
conn = create_connection(banco_dados)
cur = conn.cursor()
dfdata = pd.read_sql_query(sqlquery, conn)
datat =  (dfdata['datas'])
conn.commit()

# Obtem a tabela temporaria baixou no arquivo do site
arquivo = 'C:\\Users\\ut0k\\Downloads\\HIST_PAINEL_COVIDBR_15jun2020.xlsx'
municipios = pd.read_excel(arquivo)
municipios = municipios[municipios['data']> datat[0]]
 
# Insere a tabela temporaria na tabela de DadosDiariosMunicipios
municipios.to_sql("tempdadosDiariosMunicipios", conn, if_exists="replace")

sqlquery = "UPDATE tempdadosDiariosMunicipios SET estado = 'BR' WHERE regiao = 'Brasil';"
cur = conn.cursor()
cur.execute(sqlquery)
conn.commit()

#Atualiza a tabela DadosDiariosMunicipios
sqlquery = "Select max(data) as mdata from DadosDiariosMunicipios;"
conn = create_connection(banco_dados)
cur = conn.cursor()
dfdata = pd.read_sql_query(sqlquery, conn)
datam =  (dfdata['mdata'])
conn.commit()
dataf = datam[0]
dataf = dataf[0:10]

camposDiariosMun = ' regiao, estado,  municipio, coduf, codmun, data, codRegiaoSaude , nomeRegiaoSaude , semanaEpi, populacaoTCU2019, casosAcumulado, casosNovos, obitosAcumulado, obitosNovos, Recuperadosnovos, emAcompanhamentoNovos '
sqlquery = 'INSERT INTO DadosDiariosMunicipios (' + camposDiariosMun + ') SELECT DISTINCT' + camposDiariosMun + ' FROM tempdadosDiariosMunicipios '
sqlquery = sqlquery + " WHERE data > date('" +  dataf + "');"
cur = conn.cursor()
cur.execute(sqlquery)
conn.commit()

#Atualiza a tabela DadosDiariosMunicipios


#Atualiza a tabela Casos_Estados consolidando dados dos municipios 
# Obtem a ultima data de cadastro
sqlquery = "Select max(data) as mdata from Casos_Estados;"
conn = create_connection(banco_dados)
cur = conn.cursor()
dfdata = pd.read_sql_query(sqlquery, conn)
datam =  (dfdata['mdata'])
conn.commit()
dataf = datam[0]
dataf = dataf[0:10]
dia = int(dataf[8:10]) + 1
if int(dia) < 10:
    sdia = "0" + str(dia)
else:
    sdia =  str(dia)
dataf = dataf[0:8] + sdia

sqlquery1  = "SELECT DISTINCT regiao,  estado,  data,  max(casosAcumulado), max(casosNovos),  max(obitosAcumulado),  max(obitosNovos)"
sqlquery1  = sqlquery1 + " FROM DadosDiariosMunicipios"
sqlquery1  = sqlquery1 + " GROUP BY estado, data"
sqlquery1  = sqlquery1 + " HAVING   casosAcumulado > 0 AND estado is not null AND data > date('" +  dataf + "');"
sqlquery = "INSERT INTO Casos_Estados (regiao, estado, data, casosAcumulados, casosNovos, obitosAcumulados, obitosNovos )"
sqlquery =  sqlquery + sqlquery1
cur = conn.cursor()
cur.execute(sqlquery)
conn.commit()

#Atualiza Os  Estados com os valores de Casos_Estados
cur = conn.cursor()
sqlquery = 'UPDATE Estados SET UltimaData = (SELECT datam FROM MaximoCasosEstados WHERE (Estados.estado = MaximoCasosEstados.estado)); '            
cur.execute(sqlquery)
conn.commit()

cur = conn.cursor()
sqlquery = 'UPDATE Estados SET casosAcumulados = (SELECT casosAcumuladosL FROM MaximoCasosEstados WHERE (Estados.estado = MaximoCasosEstados.estado)); '            
cur.execute(sqlquery)
conn.commit()

cur = conn.cursor()
sqlquery = 'UPDATE Estados SET obitosAcumulados = (SELECT obitosAcumuladosL FROM MaximoCasosEstados WHERE (Estados.estado = MaximoCasosEstados.estado)); '            
cur.execute(sqlquery)
conn.commit()

 
 

 

 
