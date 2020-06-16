# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 19:29:20 2020

@author: UT0K
"""
import numpy as np 
import sqlite3
import pandas as pd
import csv 
#from datetime import timedelta  
from datetime import date   
 

# Funcao que calcula parabola com coeficiente negativo y = rx(x-v)
def polinomio2l(x,y):
    r = sum((y*(-x+ 2*x.max())))/sum(pow(x*(2*x.max()-x),2))
    m = 3
    p =  [-r*m,m*r*max(x)*2,0]  
    return p
# Calcula a correlação entre 2 variavies
def correlacao(y,ym):         
    ssresid = sum(pow(y -ym,2))
    sstotal = len(ym) * np.var(ym)
    if sstotal > 0:
        razao = 1 - ssresid/sstotal
    else:
        razao = 0
    return razao

def raizes_polimonio2(p2):
        if np.power(p2[1]*p2[1]-4*p2[2]*p2[0],1) > 0:
             r1 = (-p2[1] + np.power(p2[1]*p2[1]-4*p2[2]*p2[0],0.5))/(2*p2[0]) 
             r2 = (-p2[1] - np.power(p2[1]*p2[1]-4*p2[2]*p2[0],0.5))/(2*p2[0])
        else:
            r1 = -p2[1]/(2*p2[0])
            r2 = -p2[1]/(2*p2[0])
        p = [r1,r2]
        return p

def maximoy(p2):
        if np.power(p2[1]*p2[1]-4*p2[2]*p2[0],1) > 0:
                 m = (-p2[1]*p2[1]+4*p2[2]*p2[0])/(4*p2[0]) 
        else:
                 m = 0
        return m

def polinomio2(x,y):
    p = np.polyfit(x,y,2)  
    if p[0] > 0:
        p = polinomio2l(x,y)    
    return p

def funcao_logistica(k,r,pz,x): 
        if pz > 0:         
            pf = k / (1+ (k-pz)/pz * np.exp(-r*x))
        else:
            pf = k / (1+ (k-1) * np.exp(-r*x))
            
        return pf
# Agrega em (agrega) dias na estatistca
def ya(y,agrega):                       
    inicio = (len(x))%agrega 
    r = np.arange(inicio+agrega-1,len(y),agrega)  
    ys = np.zeros(len(r))
    for k in range(0, agrega,1):  
        ys = ys + y[r-k]  
    return ys

def xa(x,agrega):
    inicio = (len(x))%agrega  
    r = np.arange(inicio+agrega-1,len(x),agrega) 
    xs= x[r]
    return xs

def yq(x,p):
    y = p[0]*x*x + p[1]*x +p[2]
    return y

def yl(x,p):
    y = p[0]*x + p[1]
    return y

def defasagem_numero_mortes(kc,rc,pz,km,rm,pzm,dias):
    correlacao2 = -999999999
    s = 0
    dia = 0
    while s < dias: 
        xc = funcao_logistica(kc,rc,pz, range(0,dias,1))    
        xm = funcao_logistica(kc,rc,pz, range(dia,dias+dia,1))
        correlacao1 = correlacao(xc,xm)
        if correlacao1 <= correlacao2:
            print('dia '+ str(dia))
            print('1:'+ str(correlacao2)+ '2:' + str(correlacao2))
            s = dias
        else:
            s = s + 1
            correlacao2 = correlacao1
            print('1:'+ str(correlacao2)+ '2:' + str(correlacao2))
        dia = dia + 1
    #correlacaoc =  correlacao2
    return dia
    

def Condicao_inicial_funcao_Logistica(kc,rc,pz,x):
    correlacao2 = -999999999
    s = 10000
    eps = 0.5
    pza = pz
    while pz < s: 
        pz = pz + eps
        xl = funcao_logistica(kc,rc,pz, range(0,len(x),1))    
        correlacao1 = correlacao(x,xl)
        if correlacao1 <= correlacao2:
            pza = pz
            #print('eps'+ str(eps))
            pz = s
        else:
            correlacao2 = correlacao1
        #print('1:'+ str(correlacao2)+ '2:' + str(correlacao2))
    #correlacaoc =  correlacao2
    return pza

 
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

def yt(y,agrega):
    y = y + agrega
    return y

# Importa o Casos dos Estados do banco de dados COVID-19.
banco_dados = "C:\\Users\\ut0k\\Desktop\\Estudos\\PosGraducaoCienciaDeDados\\PosGraducaoUTFprCienciaDados\\ProjetoIntegrador1\\Covid19\\covid19.db"
sqlquery = "Select * from Casos_Estados_ordenados;"
conn = create_connection(banco_dados)
cur = conn.cursor()
Dfcasos = pd.read_sql_query(sqlquery, conn)
#Agrupo os Estados
estados = Dfcasos.groupby(Dfcasos['estado']).data.count()
estados = estados.reset_index() 
conn.commit()

import matplotlib.pyplot as plt
 
# Calcula o valor de r e K para cada estado
for a in estados['estado']:     
############ Calculo do numero de novos casos.
    print("Estado:" + str(a))
    b = Dfcasos[Dfcasos['estado'] == a] 
    datam = b['data'].tail(1)
    b = b[b['casosAcumulados'] > 0] 
    if a == 'PR':
        b = b[b['casosAcumulados'] > 2000]     
    x =  np.array(b['casosAcumulados'], dtype='Int64')
    y =  np.array(b['casosNovos'], dtype='Int64') 
    agrega = 7  
    yb = ya(y,agrega)     
    xb = xa(x,agrega) 
    p = polinomio2(xb,yb) 
    maxnovoc = int(maximoy(p)/agrega)
    yc = yq(xb,p)
    correlacaoc = correlacao(yb,yc)
    
#Populacao Final
    kc = -p[1]/p[0]
#Coeficiente de crescimento
    rc = p[1]/agrega   
#Calculo da Condicação Inicial
    pz = 0
    pz = Condicao_inicial_funcao_Logistica(kc,rc,pz,x)  
    xint = range(0,int((kc/max(x))*len(x)),1)  
    xint = range(0,int(300),1)      
    xl = funcao_logistica(kc,rc,pz, xint)
    
############ Calculo do numero de Obitos    
    xm =  np.array(b['obitosAcumulados'], dtype='Int64')
    y =  np.array(b['obitosNovos'], dtype='Int64') 
    yb = ya(y,agrega)     
    xb = xa(xm,agrega) 
    p = polinomio2(xb,yb) 
    maxnovom = int(maximoy(p)/agrega)
    yc = yq(xb,p)
    correlacaom = correlacao(yb,yc)    
 
#Populacao Final de Obitos
    km = -p[1]/p[0]
#Coeficiente de crescimento de Obitos
    rm = p[1]/agrega   
#Calculo da Condicação Inicial de Obitos
    pzm = 0
    pzm = Condicao_inicial_funcao_Logistica(km,rm,pzm,xm)  
    xint = range(0,int((km/max(xm))*len(xm)),1)        
    xl = funcao_logistica(km,rm,pzm, xint)
###################Calcula o coeficiente  do numero de mortes 
    p = np.polyfit(x,xm,1)
    xp = x*p[0] + p[1]
    correlacaocm = correlacao(xm,xp) 
    plt.scatter(x,xm , marker='o', label= 'Total de Casos', color = 'r')
    plt.plot(x,xp , color = 'b')
    
    #dias = 100
    #defasagem =  defasagem_numero_mortes(kc,rc,pz,km,rm,pzm,dias)

################### Cadastra no Banco de Dados
    datas = date.today()
    datam = datam.reset_index()
    datas =  datam['data'] 
    datat = datas[0]  
    datat = datat[0:10]
    
# Atualiza  dados calculos de Casos_Estado na Data 
    sqlquery = 'UPDATE Casos_Estados SET '
    sqlquery = sqlquery + 'kc = ' + str(kc) + ', '
    sqlquery = sqlquery + 'rc = ' + str(rc) + ', '
    sqlquery = sqlquery + 'correlacaoc =  '  + str(correlacaoc)   + ', '
    sqlquery = sqlquery + 'pzc =  '  + str(pz)   + ', '
    sqlquery = sqlquery + 'agregac =  '  + str(agrega)   + ', '
    sqlquery = sqlquery + 'km = ' + str(km) + ', '
    sqlquery = sqlquery + 'rm = ' + str(rm) + ', '
    sqlquery = sqlquery + 'correlacaom =  '  + str(correlacaom)   + ', '
    sqlquery = sqlquery + 'CasosPorMorte =  '  + str(p[0])   + ', '
    sqlquery = sqlquery + 'correlacaocm =  '  + str(correlacaocm)   + ', '
    sqlquery = sqlquery + 'maxnovoc =  '  + str(maxnovoc)   + ', '
    sqlquery = sqlquery + 'maxnovom =  '  + str(maxnovom)   + ', '
    sqlquery = sqlquery + 'pzm =  '  + str(pzm)   + ', '
    sqlquery = sqlquery + 'agregam =  '  + str(agrega)   + ' '
    sqlquery = sqlquery +  " WHERE estado = '" + a  + "' AND data > date('" + datat + "');"
         
    cur = conn.cursor()
    cur.execute(sqlquery)
    conn.commit()
   
# Atualiza os calculos de Estados na Ultima Data 

    sqlquery = 'UPDATE  Estados SET '
    sqlquery = sqlquery + 'kc = ' + str(kc) + ', '
    sqlquery = sqlquery + 'rc = ' + str(rc) + ', '
    sqlquery = sqlquery + 'correlacaoc =  '  + str(correlacaoc)   + ', '
    sqlquery = sqlquery + 'pzc =  '  + str(pz)   + ', '
    sqlquery = sqlquery + 'agregac =  '  + str(agrega)   + ', '
    sqlquery = sqlquery + 'km = ' + str(km) + ', '
    sqlquery = sqlquery + 'rm = ' + str(rm) + ', '
    sqlquery = sqlquery + 'correlacaom =  '  + str(correlacaom)   + ', '
    sqlquery = sqlquery + 'pzm =  '  + str(pzm)   + ', '
    sqlquery = sqlquery + 'CasosPorMorte =  '  + str(p[0])   + ', '
    sqlquery = sqlquery + 'correlacaocm =  '  + str(correlacaocm)   + ', '
    sqlquery = sqlquery + 'maxnovoc =  '  + str(maxnovoc)   + ', '
    sqlquery = sqlquery + 'maxnovom =  '  + str(maxnovom)   + ', ' 
    sqlquery = sqlquery + 'agregam =  '  + str(agrega)   + ' '
    sqlquery = sqlquery +  " WHERE estado = '" + a  + "' AND UltimaData > date('" + datat + "');"    
    
    cur = conn.cursor()
    cur.execute(sqlquery)
    conn.commit()  
    
    
    

############################## Testes das funcoes#################
#Dfcasos = Dfcasos.set_index(['estado', 'data'],drop=False).sort_index()
# Efetua o calculo do  K , r e agrega para todos os dias k = 0 para cada estado
#Dfcasos = Dfcasos.reset_index(['estado', 'data'])
