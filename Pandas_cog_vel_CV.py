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
df_cog_CC = None
df_cog_time_list=[]
df_vel_time_list=[]
df_cog_X_list=[]
df_cog_Y_list=[]
df_vel_X_list=[]
df_vel_Y_list=[]

bagfiles_path = '/home/fukuhara/catkin_ws/src/bag_files/'

def input_ct():
    global kaisu
    print("how many times")
    kaisu = int(input())

def make_dir():###今の時間が入った名前のディレクトリを作成
    global new_dir
    dt_now = datetime.datetime.now()
    new_dir =str(bagfiles_path) + "cc" + str(dt_now.strftime('%m-%d-%H-%M'))+'/csv/'
    os.makedirs(new_dir , exist_ok=True)
    print(new_dir)

def bag_to_csv():
    global kaisu
    for i in range(kaisu):###回数分bagファイルを読み取り→cogposとcmd_velを並べる
        cmd_cog="rostopic echo -b "+ bagfiles_path +str(i)+".bag -p /wg/cogpos > " + str(new_dir) +str(i)+"_cog"+".csv"
        print(cmd_cog)
        cmd_vel="rostopic echo -b "+ bagfiles_path +str(i)+".bag -p /wg/cmd_vel > " + str(new_dir) +str(i)+"_vel"+".csv"
        proc1 = subprocess.Popen(cmd_cog, shell=True, stdout=PIPE, stderr=PIPE)
        proc2 = subprocess.Popen(cmd_vel, shell=True, stdout=PIPE, stderr=PIPE)
        ###0_cog.csv 0_vel.csv created
        result1 = proc1.communicate()
        result2 = proc2.communicate()
        (stdout1, stderr1) = (result1[0], result1[1])
        (stdout2, stderr2) = (result2[0], result2[1])
    print("_done_csv_make")

def pandas_group():
    global kaisu , new_dir,df_cog_time_list, df_cog_CC
    for i in range(kaisu):
        cogcsv = str(new_dir)+str(i)+"_cog.csv" 
        velcsv = str(new_dir)+str(i)+"_vel.csv" 
        df_cog = pd.read_csv(cogcsv)###0_cog.csv 0_vel.csvを読み込み
        df_vel = pd.read_csv(velcsv)###0_cog.csv 0_vel.csvを読み込み
        
        vel_f0_name = 'X_'+str(i)+'_vel'
        cog_f0_name = 'X_'+str(i)+'_cog'
        #cog_f1_name = 'Y_'+str(i)+'_cog'
        time_cog_name = 'Time_'+str(i)+'_cog'
        time_vel_name = 'Time_'+str(i)+'_vel'
        
        #df_cog = df_cog.rename({'field.data0':cog_f0_name,'field.data1':cog_f1_name,'%time':time_cog_name},axis='columns')
        #df_vel = df_vel.rename({'field.data0':vel_f0_name,'field.data1':cog_f1_name,'%time':time_vel_name},axis='columns')
        df_cog = df_cog.rename({'field.data0':cog_f0_name,'%time':time_cog_name},axis='columns')
        df_cog_X = df_cog[cog_f0_name]
        df_cog_time = df_cog[time_cog_name]###タイムスタンプの列を抽出
        
        df_vel = df_vel.rename({'field.linear.x':vel_f0_name,'%time':time_vel_name},axis='columns')
        df_vel_time = df_vel[time_vel_name]
        df_vel_X = df_vel[vel_f0_name]

        #df_cog_time = df_cog_time.rename(columns={'%time': 'Col_1'})
        #A_r_df=A_df.map(lambda x: int(Decimal(str(x)).quantize(Decimal('1E6'), rounding=ROUND_HALF_UP))) ###pandas.Seriesの各要素に適用するにはmap() ,decimalモジュールのquantize()で四捨五入.ここでは整数の6桁目を四捨五入し見やすくしただけ。余り意味は無い
        df_cog_time_m = (df_cog_time - 1651330800000000000 - 1550000000000000).astype(float) * 0.000000001

        df_vel_time_m = (df_vel_time - 1651330800000000000 - 1550000000000000).astype(float) * 0.000000001##unixtimeを見やすくするために無理やり小さく、そして0.1^9で小数点が無かったunixtimeを正確な秒へ
        df_cog_time_list.append(df_cog_time_m)
        df_cog_X_list.append(df_cog_X)

        df_vel_time_list.append(df_vel_time_m)
        df_vel_X_list.append(df_vel_X)
        #df_cog_y_list.append(df_cog_Y)
        
        
    
    for i in range(kaisu):
        if i == 0 :
            #df_cc = pd.concat([df_cog_time_list[0],df_cog_X_list[0],df_cog_Y_list[0]], axis=1)
            df_cc_cog = pd.concat([df_cog_time_list[0],df_cog_X_list[0]], axis=1)

            df_cc_vel = pd.concat([df_vel_time_list[0],df_vel_X_list[0]], axis=1)
            
        else:
            df_cc_cog = pd.concat([df_cc_cog,df_cog_time_list[i]], axis=1)
            df_cc_cog = pd.concat([df_cc_cog,df_cog_X_list[i]], axis=1)

            df_cc_vel = pd.concat([df_cc_vel,df_vel_time_list[i]], axis=1)
            df_cc_vel = pd.concat([df_cc_vel,df_vel_X_list[i]], axis=1)
            #df_cc = pd.concat([df_cc,df_cog_Y_list[i]], axis=1)
    #df_cc_cog = df_cc_cog.reset_index()
    #df_cc_vel = df_cc_vel.reset_index()

    print(df_cc_vel)
    print(df_cc_cog)
    csv_path1 =str(new_dir.rstrip('csv/'))+'/CC'+str(i)+'cog.csv'
    csv_path2 =str(new_dir.rstrip('csv/'))+'/CC'+str(i)+'vel.csv'
    #csv_path =str(new_dir.rstrip('csv/'))+'/CC'+str(i)+'vel.csv'
     #'SaveFolder/addData2.csv'/cc09-14-20-52/cogvel1.csv
    print(csv_path1)
    print(csv_path2)
    df_cc_cog.to_csv(csv_path1, index=False,header=True, float_format='%.4f' )

    df_cc_vel.to_csv(csv_path2, index=False,header=True, float_format='%.4f' )
    

def main():
    
    inputs = input_ct()
    make_dir()
    bag_to = bag_to_csv()
    pandas_group()

if __name__ == "__main__":
    main()