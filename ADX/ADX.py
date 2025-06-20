from tqdm import tqdm
import os
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt


def caculate_adx(df, length=14):
    """

    :param df:传入的参数
    :param length: 时间周期长度
    :return: df['g1.ADX']
    """
    df = df.copy()
    # 计算真实波幅(TR)
    df['H-L'] = df['h'] - df['l']
    df['H-PreClose'] = np.abs(df['h'] - df['c'].shift(1))
    df['L-PreClose'] = np.abs(df['l'] - df['c'].shift(1))
    df['TR'] = df[['H-L', 'H-PreClose', 'L-PreClose']].max(axis=1)

    # 计算+DM和-DM
    df['H-PreH'] = df['h'] - df['h'].shift(1)
    df['L-PreL'] = df['l'].shift(1) - df['l']
    df['+DM'] = np.where((df['H-PreH'] > df['L-PreL']) & (df['H-PreH'] > 0), df['H-PreH'], 0)
    df['-DM'] = np.where((df['L-PreL'] > df['H-PreH']) & (df['L-PreL'] > 0), df['L-PreL'], 0)

    # 计算TR、+DM、-DM的N日移动平均
    # 使用Wilder的平滑方法
    df['TR_SMA'] = df['TR'].rolling(window=length).mean()
    df['+DM_SMA'] = df['+DM'].rolling(window=length).mean()
    df['-DM_SMA'] = df['-DM'].rolling(window=length).mean()


    # for i in range(length, len(df)):
    #     df.loc[df.index[i], 'TR_SMA'] = (df.loc[df.index[i - 1], 'TR_SMA'] * (length - 1) + df.loc[
    #         df.index[i], 'TR']) / length
    #     df.loc[df.index[i], '+DM_SMA'] = (df.loc[df.index[i - 1], '+DM_SMA'] * (length - 1) + df.loc[
    #         df.index[i], '+DM']) / length
    #     df.loc[df.index[i], '-DM_SMA'] = (df.loc[df.index[i - 1], '-DM_SMA'] * (length - 1) + df.loc[
    #         df.index[i], '-DM']) / length
    # 计算+DI和-DI
    df['+DI'] = (df['+DM_SMA'] / df['TR_SMA']) * 100
    df['-DI'] = (df['-DM_SMA'] / df['TR_SMA']) * 100

    # 计算DX
    df['DX'] = (np.abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])) * 100

    # 计算ADX (DX的N日移动平均)
    # df['ADX'] = df['DX'].rolling(window=length).mean()
    df['ADX']=0

    for i in range(length-1, len(df)):
        df.loc[df.index[i], 'ADX'] = (df.loc[df.index[i - 1], 'ADX'] * (length - 1) + df.loc[
            df.index[i], 'DX']) / length
    df = df.reset_index(drop=True)  # 在关键步骤重置索引
    return df['ADX']


if __name__ == '__main__':
    df1 = pd.read_csv('./ADXH.csv')
    length = 14  # 默认交易周期为14
    df1['g1.ADX'] = 0
    df1['g1.ADX'] = df1['g1.ADX'].astype(np.float64)
    df1['g1.ADX'] = caculate_adx(df=df1, length=length)
    print(df1)
