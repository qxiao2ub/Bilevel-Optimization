#pandas is for using reading functions
import pandas as pd

#numpy for n-dimensional array obj
import numpy as np


#------------------------step 1-assign parameters----------------------------------

#1.1-assign for Dijcst expression
#service level is 1
q = 1

#to make it easy, set a=b=m=n=1 for utility function and T=3 (0,1,2,3 totally 4 time periods)
a=b=m=n=1
T=3

#test parameters setting
print ('q,a,b,m,n,T:',q,a,b,m,n,T)

#1.2-assign dijt

#read original test data test 1 period 0,2,5,8 (others btw 0-8 are same), separated with ' '
d1p0=[[float(i) for i in line.strip().split(' ')] for line in open('Test Data_Data1_Period0.txt').readlines()]
d1p2=[[float(i) for i in line.strip().split(' ')] for line in open('Test Data_Data1_Period2.txt').readlines()]
d1p5=[[float(i) for i in line.strip().split(' ')] for line in open('Test Data_Data1_Period5.txt').readlines()]
d1p8=[[float(i) for i in line.strip().split(' ')] for line in open('Test Data_Data1_Period8.txt').readlines()]

#assign dijt-(i=4,j=4,t=4), total 20 o/d, only use 4 for o and 4 for d
#total 40 time periods but now only use 4 periods
d = np.zeros((4,4,4), dtype = np.float )

#assign read dijt to list
for i in range (0,4):
  for j in range (0,4):
    d[i,j,0] = d1p0[i][j]
    d[i,j,1] = d1p2[i][j]
    d[i,j,2] = d1p5[i][j]
    d[i,j,3] = d1p8[i][j]

#test dijt assign correctly
print("Print demand input:") 
print(d[0,0,0],d[3,3,0])
print(d[0,0,1],d[3,3,1])
print(d[0,0,2],d[3,3,2])
print(d[0,0,3],d[3,3,3])

#1.3-assign cijt as parameter
c = np.zeros((4,4,4), dtype = np.float)

c_ori = [78,3,10,39,43,10,19,2,78,3,10,39,43,10,19,2,78,3,10,39,43,10,19,2,78,3,10,39,43,10,19,2,
         78,3,10,39,43,10,19,2,78,3,10,39,43,10,19,2,78,3,10,39,43,10,19,2,78,3,10,39,43,10,19,2]

#cijt reference
#c[0,0,0]=78
#c[0,0,1]=3
#c[0,1,0]=10
#c[0,1,1]=39
#c[1,0,0]=43
#c[1,0,1]=10
#c[1,1,0]=19
#c[1,1,1]=2

#pointer to read c_ori
k = 0

for i in range (0,4):
  for j in range (0,4):
    for t in range (0,4):
      c[i,j,t] = c_ori[k]
      k=k+1

#test cijt
print ('Test cijt:', c[0,0,0], c[0,1,0], c[3,3,3])

#1.4-assign pijt (penalty) as parameter, use p_ori but 0.5 times it as penalty

p_ori = [10,2,3,4,9,5,9,6,10,2,3,4,9,5,9,6,10,2,3,4,9,5,9,6,10,2,3,4,9,5,9,6,
         10,2,3,4,9,5,9,6,10,2,3,4,9,5,9,6,10,2,3,4,9,5,9,6,10,2,3,4,9,5,9,6]

p = np.zeros((4,4,4), dtype = np.float)

#pointer to read P_ori
k = 0

for i in range (0,4):
  for j in range (0,4):
    for t in range (0,4):
      #Price is 0.5 times as P_ori to make penalty small
      p[i,j,t] = p_ori[k] * 0.5
      k=k+1

#test pijt
print ('Test pijt:', p[0,0,0], p[0,1,0], p[3,3,3])

#1.5-assign inventory cost hit
h = np.zeros((4,4), dtype = np.float )

#reference for hit
#h[0,0]=3
#h[0,1]=8
#h[1,0]=3 
#h[1,1]=10

h_ori = [3,8,3,10,3,8,3,10,3,8,3,10,3,8,3,10]

#pointer to read h_ori
k = 0

for i in range (0,4):
  for t in range (0,4):
    h[i,t] = h_ori[k]
    k=k+1

#test hit
print ('Test hit:', h[0,0], h[0,0], h[3,3])

#1.6-assign alpha: percentage Xji\tao will stay in inventory until t
#alpha [j,i,tao,t]
alpha = np.zeros((4,4,4,4), dtype = np.float )

#if i!=j, tao<t, assign alpha=0.5
for j in range (0,4):
  for i in range (0,4):
    for tao in range (0,4):
      for t in range (0,4):
        if j != i and tao < t:
          alpha[j,i,tao,t] = 0.5
        
#test alpha
print ('Test alpha:',alpha[0,0,0,0],alpha[0,1,0,1],alpha[2,3,2,3],alpha[3,3,3,3])

#---------------------------------step 2: add variables-------------------------------

#2.1-python calls cplex
from docplex.mp.model import Model
mdl = Model(name='Xiao Bilevel Heuristic Model')

#2.2-define variables
#define 3 types decision variables: Uijt-4*4*4, Xijt-4*4*4, Vit-4*4, Pijt
#X/U/V/P variables in 4 dimensions
X = {(i,j,t): mdl.integer_var(lb=0, name="X[{0}][{1}][{2}]".format(i,j,t)) 
for i in range(0,4) for j in range(0,4) for t in range(0,4) }

U = {(i,j,t): mdl.integer_var(lb=0, name="U[{0}][{1}][{2}]".format(i,j,t)) 
for i in range(0,4) for j in range(0,4) for t in range(0,4) }

V = {(i,t): mdl.integer_var(lb=0, name="V[{0}][{1}]".format(i,t)) 
for i in range(0,4)  for t in range(0,4) }

#P = {(i,j,t): mdl.integer_var(lb=0, name="P[{0}][{1}][{2}]".format(i,j,t)) 
#for i in range(0,4) for j in range(0,4) for t in range(0,4) }

#----------------------step 3: now only use 1 pair of variables(i=0,j=1,t=2), do iterative------------------
#4 variables: X/U/V/P[0,1,2]
i=0
j=1
t=2

#3.1-lower level (operational level)

#initially set Pijt=100

P = np.zeros((4,4,4), dtype = np.float )
P[i,j,t] = 100

#test P[0,1,0]
print ('Test P[0,1,2]:', P[i,j,t])

#lower obj
sub_obj = c[i,j,t] * X[i,j,t] + p[i,j,t] * U[i,j,t] + h[i,t] * V[i,t]

#test sub_obj
print ('Test sub_obj:',sub_obj)

#lower 1st constr
mdl.add_constraint( U[i,j,t] >= U[i,j,t-1] + ( (b*d[i,j,t]+c[i,j,t]*d[i,j,t]*m-n*T*U[i,j,t]) / (a+b+m*(c[i,j,t]+P[i,j,t])) ) - X[i,j,t])

#lower 2nd constr
mdl.add_constraint( X[i,j,t] + X[i,j,t+1] >= U[i,j,t-1] + ( (b*d[i,j,t]+c[i,j,t]*d[i,j,t]*m-n*T*U[i,j,t]) / (a+b+m*(c[i,j,t]+P[i,j,t])) )) 

#lower 3rd constr
V[i,t] == V[i,t-1] + mdl.sum( alpha[j,i,tao,t] * X[i,j,tao] for tao in range(0,2)) - X[i,j,t]

#lower 4th constr
V[i,0] = V[i,T]
