#!/usr/bin/python
# -*- coding: utf-8 -*-
import pypinyin
f=open('pinyin_library.txt','w',encoding='gbk')
for i in range(0x4e00,0x9fa6):
    if pypinyin.lazy_pinyin(chr(i), style=pypinyin.Style.TONE2)[0][-1]=='1':
        f.write(chr(i)+pypinyin.lazy_pinyin(chr(i), style=pypinyin.Style.TONE2)[0][:-1]+'\n')
    # print(pypinyin.lazy_pinyin(chr(i))[0][-1], style=Style.TONE2)
f.close()