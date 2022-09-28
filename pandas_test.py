#!/usr/bin/env python3
# coding: UTF-8

###1640962800は2022年5月1日0秒のunixtime

import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import os
import subprocess
from subprocess import PIPE
import datetime
# pd.options.display.float_format = '{:.4f}'.format #4keta
kaisu = None

print("HOW many ")
kaisu= int (input())
for i in range(kaisu):
    dt_now = datetime.datetime.now()
    #cmd="rostopic echo -b "+str(i)+".bag -p /wg/cogpos > "+str(i)+"_cog"+str(dt_now.strftime('%Y-%m-%d-%H-%M-%S'))+".csv"
    cmd="rostopic echo -b "+str(i)+".bag -p /wg/cogpos > "+str(i)+"_cog"+".csv"
    proc = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    ###1_cog.csv created
    result = proc.communicate()
    (stdout, stderr) = (result[0], result[1])
print("done_cog")

proc.wait()

cogcsv = str(i)+"_cog.csv"
velcsv = str(i)+"_vel.csv"
stgcsv = str(i)+"_stg.csv"

df = pd.read_csv(cogcsv)

A_df = df['%time']
print(A_df.head())


#A_r_df=A_df.map(lambda x: int(Decimal(str(x)).quantize(Decimal('1E6'), rounding=ROUND_HALF_UP)))
#print(A_r_df.head())
print("map")
A_rs_df = (A_df - 1651330800000000000 - 1550000000000000).astype(float) * 0.000000001 ##unixtimeを見やすくするために無理やり小さく、そして0.1^9で小数点が無かったunixtimeを正確な秒へ
print(A_rs_df.head())
f0_df = df['field.data0']
f1_df = df['field.data1']
print(f0_df.head())
#df_h = pd.concat([A_rs_df, f0_df], axis=1)
df_h = pd.concat([A_rs_df, f0_df, f1_df], axis=1)
print(df_h.head())
os.makedirs('SaveFolder', exist_ok=True)
df_h.to_csv('SaveFolder/addData2.csv',index=False,header=['TIME', 'cog_x', 'cog_y'], float_format='%.4f' )