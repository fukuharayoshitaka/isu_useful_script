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
kaisu = 0
dt_now = None
new_dir = None



def input_ct():
    global kaisu
    print("how many times")
    kaisu = int(input())

def make_dir():###今の時間が入った名前のディレクトリを作成
    global new_dir
    dt_now = datetime.datetime.now()
    new_dir = "cc" + str(dt_now.strftime('%m-%d-%H-%M'))
    os.makedirs(new_dir , exist_ok=True)
    print(new_dir)

def bag_to_csv():
    global kaisu
    for i in range(kaisu):###回数分bagファイルを読み取り→cogposとcmd_velを並べる
        cmd_cog="rostopic echo -b "+str(i)+".bag -p /wg/cogpos > "+str(i)+"_cog"+".csv"
        cmd_vel="rostopic echo -b "+str(i)+".bag -p /wg/cmd_vel > "+str(i)+"_vel"+".csv"
        proc1 = subprocess.Popen(cmd_cog, shell=True, stdout=PIPE, stderr=PIPE)
        proc2 = subprocess.Popen(cmd_vel, shell=True, stdout=PIPE, stderr=PIPE)
        ###0_cog.csv 0_vel.csv created
        result1 = proc1.communicate()
        result2 = proc2.communicate()
        (stdout1, stderr1) = (result1[0], result1[1])
        (stdout2, stderr2) = (result2[0], result2[1])
    print("_done_csv_make")

def pandas_group():
    global kaisu , new_dir
    for i in range(kaisu):
        cogcsv = str(i)+"_cog.csv" 
        velcsv = str(i)+"_vel.csv"
        #stgcsv = str(i)+"_stg.csv"
        df_cog = pd.read_csv(cogcsv)###0_cog.csv 0_vel.csvを読み込み
        df_vel = pd.read_csv(velcsv)
        df_cog_time = df_cog['%time']###タイムスタンプの列を抽出
        df_vel_time = df_vel['%time']
        #A_r_df=A_df.map(lambda x: int(Decimal(str(x)).quantize(Decimal('1E6'), rounding=ROUND_HALF_UP))) ###pandas.Seriesの各要素に適用するにはmap() ,decimalモジュールのquantize()で四捨五入.ここでは整数の6桁目を四捨五入し見やすくしただけ。余り意味は無い
        

        df_cog_time_m = (df_cog_time - 1651330800000000000 - 1550000000000000).astype(float) * 0.000000001 ##unixtimeを見やすくするために無理やり小さく、そして0.1^9で小数点が無かったunixtimeを正確な秒へ
        df_vel_time_m = (df_cog_time - 1651330800000000000 - 1550000000000000).astype(float) * 0.000000001 ##unixtimeを見やすくするために無理やり小さく、そして0.1^9で小数点が無かったunixtimeを正確な秒へ
        df_cog_f0 = df_cog['field.data0']
        df_cog_f1 = df_cog['field.data1']
        df_vel_fx = df_vel['field.linear.x']
        df_vel_fy = df_vel ['field.linear.y']
        df_cc = pd.concat([df_cog_time_m, df_cog_f0, df_cog_f1, df_cog_time_m, df_vel_fx, df_vel_fy], axis=1)
        print(df_cc.head())
        
        csv_path = str(new_dir)+'/CC'+str(i)+'cog_vel.csv' #'SaveFolder/addData2.csv'/cc09-14-20-52/cogvel1.csv
        print(csv_path)
        df_cc.to_csv(csv_path, index=False,header=['TIME_VEL', 'cog_X', 'cog_Y','TIME_VEL','vel_X','vel_Y'], float_format='%.4f' )

def main():
    
    inputs = input_ct()
    make_dir()
    bag_to = bag_to_csv()
    pandas_group()

if __name__ == "__main__":
    main()