# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:02:43 2020

@author: UT0K
"""
import numpy as np 
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import csv 
from datetime import timedelta  
from datetime import date

############### Funcões para plotar
# k - Populacaçao final
# r - 
#
###############################
 

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

def max_tempo(k,r,pz):
    m = int((np.log(np.int64(99*(k/pz-1))))/r)
    return m

def raizes_polimonio2(p2):
        if np.power(p2[1]*p2[1]-4*p2[2]*p2[0],1) > 0:
             r1 = (-p2[1] + np.power(p2[1]*p2[1]-4*p2[2]*p2[0],0.5))/(2*p2[0]) 
             r2 = (-p2[1] - np.power(p2[1]*p2[1]-4*p2[2]*p2[0],0.5))/(2*p2[0])
        else:
            r1 = -p2[1]/(2*p2[0])
            r2 = -p2[1]/(2*p2[0])
        p = [r1,r2]
        return p

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
    
#Conecta o banco de dados de trabalho
def create_connection(db_file):     
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print("Erro ao conectar")
    return conn

def Plota_comparativo_novos_casos(titulo,x,y,k,ymaximo,correlacao): 
        print(titulo)
        p = polinomio2(x,y)
        r = raizes_polimonio2(p)
        xp = range(0,int(max(r)),1) 
        yp = p[0] * xp * xp + p[1] * xp + p[2]
        
        #plt.axis([x.min()*0.9, abs(k*1.1), y.min()*0.9,ymaximo*1.1]) 
        plt.scatter(x,y , marker='o', label= 'Total de Casos', color = 'r')
        plt.plot(xp,yp, color = 'b') 
        
        plt.title(titulo+'-'+ str(int(k))+ '-'+ str(int(100*correlacao)))
        plt.xlabel('Total Casos Positivos(P)') 
        plt.ylabel('Casos dia (dP/dt)')
        plt.grid(True)
        plt.show()  
  
 
def Plota_comparativo_logistica(titulo,k,r,pz,x,correlacao,m):  
    
        #m = max_tempo(k,r,pz)
        xp = range(0,int((m)),1) 
        pz = pz*1
        print(pz)
        pf = funcao_logistica(k,r,pz,xp)  
        
        plt.axis([0, m, x.min()*0.9,pf.max()*1.1]) 
        plt.plot(x , marker='o', label= 'Total de Casos por dia', color = 'r')
        plt.plot(pf , color = 'b')   

        plt.title(titulo+'-'+ str(int(k)))
        plt.ylabel('Total Casos Positivos(P)') 
        plt.xlabel('Dias após primeiro caso')
        plt.grid(True)
        plt.show()  
   

# Importa o Casos dos Estados do banco de dados COVID-19.
banco_dados = "C:\\Users\\ut0k\\Desktop\\Estudos\\PosGraducaoCienciaDeDados\\PosGraducaoUTFprCienciaDados\\ProjetoIntegrador1\\Covid19\\covid19.db"
sqlquery = "Select * from Estados ORDER BY casosAcumulados DESC;"
conn = create_connection(banco_dados)
cur = conn.cursor()
Estados = pd.read_sql_query(sqlquery, conn)
conn.commit()

sqlquery = "Select * from Casos_Estados ORDER BY casosAcumulados;"
conn = create_connection(banco_dados)
cur = conn.cursor()
CasosEstados = pd.read_sql_query(sqlquery, conn)
conn.commit()

# Maximos dias da curva
Estados = Estados[Estados['casosAcumulados'] > 0]           
Estados['m'] = np.int64(99*(Estados['Kc']/Estados['pzc']-1))
Estados['m'] =  np.int64(np.log((Estados['m']))/Estados['rc'])
 
#Agrupo os Estados
 
for a in Estados['estado']: 
 
    print("Estado:" + str(a))
    b = CasosEstados[CasosEstados['estado'] == a] 
    c = Estados[Estados['estado'] == a] 
    datam = b['data'].tail(1)
    b = b[b['casosAcumulados'] > 0]    
    x =  np.array(b['casosAcumulados'], dtype='Int64')
    y =  np.array(b['casosNovos'], dtype='Int64') 
 
################### Plota a curva Diferencial dos Casos
    Plota_comparativo_novos_casos(a,x,y,c['Kc'],c['maxnovoc'],c['correlacaocm'])
################### Plota a curva dos Casos
    #Plota_comparativo_logistica(a,c['Kc'],c['rc'],c['pzc'],x,c['correlacaocm'],c['m']) 
    c.reset_index()
    xp = np.array(range(0,int((c['m'])),1))
    k = int(c['Kc'])
    rc =  float(c['rc']) 
    pz = int(c['pzc'])  
    pf = funcao_logistica(k,rc,pz,xp)  
        
    #plt.axis([0, m, 0 ,pf.max()*1.1]) 
    plt.plot(x , marker='o', label= 'Total de Casos por dia', color = 'r')
    plt.plot(pf , color = 'b')   

    plt.title(a+'-'+ str(int(c['Kc'])))
    plt.ylabel('Total Casos Positivos(P)') 
    plt.xlabel('Dias após primeiro caso')
    plt.grid(True)
    plt.show()  
  
 
    
################# Plota a curva diferencia dos Obitos


############# Plota a curva do Obitos


#########################3 Plota a curva de Casos X  Obitos   
    
    
###################Calcula relacao numero de Mortes X Casos
 
    p = np.polyfit(xm,x,1) 
    plt.plot(xm,x,marker='o', label= 'Original', color = 'r')  
    xp = yl(xm,p)
    plt.plot(xm,xp, color = 'b')  
    plt.grid(True)
    print('correlacao:'+ str(correlacao(xm,xp)))
 
    dias = 100
    defasagem =  defasagem_numero_mortes(kc,rc,pz,km,rm,pzm,dias)


  

# Grafico Estados    ]  
banco_dados = "C:\\Users\\ut0k\\Desktop\\Estudos\\PosGraducaoCienciaDeDados\\PosGraducaoUTFprCienciaDados\\ProjetoIntegrador1\\Covid19\\covid19.db"
sqlquery = "Select * from Estados;"
conn = create_connection(banco_dados)
cur = conn.cursor()
Estados = pd.read_sql_query(sqlquery, conn)
conn.commit()  
Estados = Estados[Estados['ObitosAcumulados'] > 0]
 
    
Estados['x'] = (Estados['ObitosAcumulados']*pow(10,6)/Estados['Populacao'] * (Estados['Kc']/Estados['casosAcumulados'])) 
Estados['y'] = (Estados['Kc']*pow(10,6)/Estados['Populacao']) 

maximox = Estados['x'].max()
maximoy = Estados['y'].max()          

maximox = 2000
maximoy = 25000
Estados = Estados[Estados['x'] <=  maximox]
Estados = Estados[Estados['y'] <=  maximoy]
names = np.array(Estados['estado'])
x = np.array((Estados['x']),dtype='int64')
y = np.array(Estados['y'],dtype='int64') 
xs=  range(1,int(max(x)),1)
 
p2 = np.polyfit(x,y,1)   
print(p2)
yp = p2[0] * xs  + p2[1]  

b = Estados[Estados['estado'] == 'PR']
yb = np.array(b['Kc']*pow(10,6)/b['Populacao'])
xb = np.array(b['ObitosAcumulados']*pow(10,6)/b['Populacao'] * (b['Kc']/b['casosAcumulados']))             
     
fig, ax = plt.subplots()
ax.axis([0, maximox, 0, maximoy])
ax.scatter(Estados['x'],Estados['y'] , marker='o', label= 'Total de Casos', color = 'r')  
plt.plot(xs,yp , color = 'g')
ax.plot([xb[0],xb[0]], [0,yb[0]] , color = 'b')  
ax.plot([0,xb[0]], [yb[0],yb[0]] , color = 'b')  
for i, n in enumerate(names):
            ax.annotate(n, (x[i], y[i]))           
plt.title('Estados do Brasil')
plt.xlabel('Mortes/Milhão Habitantes (projetado)') 
plt.ylabel('Casos/Milhão Habitantes (projetado)')
plt.grid(True)
local = 'EstadosComparacao1.png'
plt.savefig(local, dpi=300, quality=80, optimize=True, progressive=True)
plt.show()  