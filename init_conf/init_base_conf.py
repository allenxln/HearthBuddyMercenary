import copy
import csv
import json
import sys

import os

import yaml

# 最长公共子序列
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n], get_lcs(dp, s1, s2, m, n)

def get_lcs(dp, s1, s2, i, j):
    if i == 0 or j == 0:
        return ''
    elif s1[i - 1] == s2[j - 1]:
        return get_lcs(dp, s1, s2, i - 1, j - 1) + s1[i - 1]
    else:
        if dp[i - 1][j] > dp[i][j - 1]:
            return get_lcs(dp, s1, s2, i - 1, j)
        else:
            return get_lcs(dp, s1, s2, i, j - 1)




class InitConf():
    def __init__(self) -> None:
        self.all_mer_dict = {}  # 标准佣兵名称
        self.full_mer_name_dict = {}  # 存储佣兵名对应的真实名称
        self.out_dict = {}  # 存储输出的yml文件
        self.out_dict['队伍'] = {}
        self.out_dict['队伍']['御三家'] = ['凯瑞尔·罗姆', '剑圣萨穆罗', '泽瑞拉']
        self.out_dict['队伍']['自然队'] = ['玛法里奥·怒风', '古夫·符文图腾', '布鲁坎']
        self.out_dict['队伍']['巴斯顿'] = ['巴琳达·斯通赫尔斯', '迦顿男爵', '拉格纳罗斯']
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)


    def analysis_csv(self, path):
        with open(path, 'r') as file:
            csv_reader = csv.reader(file)
            total_line = 0
            for row in csv_reader:
                if ('等级' in row[1]):
                    continue
                total_line += 1
                # print(row)
                self.all_mer_dict[row[0]] = {'level': int(
                    row[1]), 'fragment': int(row[2]), 'task': int(row[3])}
            print('analysis_csv succ. {}->{}'.format(total_line,len(self.all_mer_dict)))
    
    def update_mer(self, s_name, baozang_list = [], frag_lst = [], frag_instance = '', 
                   zhuangbei_instanse = {}, skill_pri='123', skill_circle='', sequence = 9):
        if '佣兵' not in  self.out_dict:
            self.out_dict['佣兵'] = {}
        mer_name = self.get_mername_by_sname(s_name)
        if len(s_name) <= 0:
            return 
        baozang_list = [x for x in baozang_list if len(x) > 0]
        frag_lst = [x for x in frag_lst if len(x) > 0]
        # if '莉莉安' in mer_name:
        #     print('{}->{}, {}'.format(s_name,mer_name,zhuangbei_instanse))
        if mer_name not in self.out_dict['佣兵']:
            self.out_dict['佣兵'][mer_name] = {}
            self.out_dict['佣兵'][mer_name]['宝藏优选'] = copy.deepcopy(baozang_list)
            self.out_dict['佣兵'][mer_name]['默认出场顺序'] = sequence
            self.out_dict['佣兵'][mer_name]['技能优先级'] = skill_pri
            self.out_dict['佣兵'][mer_name]['技能流'] = skill_circle
            self.out_dict['佣兵'][mer_name]['解锁所需碎片数'] = 500
            self.out_dict['佣兵'][mer_name]['碎片来源'] = copy.deepcopy(frag_lst)
            self.out_dict['佣兵'][mer_name]['装备解锁'] = copy.deepcopy(zhuangbei_instanse)
        else:
            if len(baozang_list) > 0 :
                self.out_dict['佣兵'][mer_name]['宝藏优选'] = copy.deepcopy(baozang_list)
            if len(frag_lst) > 0 :
                self.out_dict['佣兵'][mer_name]['碎片来源'] = copy.deepcopy(frag_lst)
            if len(frag_instance) > 0 and frag_instance not in self.out_dict['佣兵'][mer_name]['碎片来源']:
                self.out_dict['佣兵'][mer_name]['碎片来源'].append(frag_instance)
            if len(zhuangbei_instanse) > 0 :
                self.out_dict['佣兵'][mer_name]['装备解锁'] = copy.deepcopy(zhuangbei_instanse)
            if '123' not in skill_pri:
                self.out_dict['佣兵'][mer_name]['技能优先级'] = copy.deepcopy(skill_pri)
            if len(skill_circle) > 0 :
                self.out_dict['佣兵'][mer_name]['技能流'] = copy.deepcopy(skill_circle)
            if sequence < 9:
                self.out_dict['佣兵'][mer_name]['默认出场顺序'] = sequence
        # if '莉莉安' in mer_name:
        #     print(self.out_dict['佣兵'][mer_name]['装备解锁'])

    def update_instance(self, instance):
        if '地图' not in self.out_dict:
            self.out_dict['地图'] = {}
        if instance in self.out_dict['地图']:
            return
        if '1-' in instance or '2-' in instance:
            self.out_dict['地图'][instance] = ['巴斯顿', '自然队', '御三家']
        elif '4-' in instance :
            self.out_dict['地图'][instance] = ['自然队']
        else:
            self.out_dict['地图'][instance] = ['巴斯顿','自然队']

    def get_mername_by_sname(self, s_name):
        if s_name in self.full_mer_name_dict:
            return copy.deepcopy(self.full_mer_name_dict[s_name])
        if s_name in self.all_mer_dict:
            self.full_mer_name_dict[s_name] = copy.deepcopy(s_name)
            return copy.deepcopy(s_name)
        len_s = len(s_name)
        max_comm = -1
        max_comm_name = str()
        for f_name in self.all_mer_dict.keys():
            if s_name in f_name:
                max_comm_name = f_name
                max_comm = len_s
            len_comm ,_ = lcs(s_name,f_name)
            if len_comm > max_comm:
                max_comm = len_comm
                max_comm_name = f_name
        # if '乌瑟尔' in s_name:
        #     print('{} -> {}, s_len:{}, max_len:{}'.format(s_name,max_comm_name,len_s,max_comm))
        if max_comm >= 0.5*(len_s):
            self.full_mer_name_dict[s_name] = copy.deepcopy(max_comm_name)
            return copy.deepcopy(max_comm_name)
        else:
            print('{} NOT FOUND'.format(s_name))
            return None
    # 解析宝藏优先
    def insert_baozang(self, path):
        if '佣兵' not in  self.out_dict:
            self.out_dict['佣兵'] = {}
        with open(path, 'r') as file:
            for line in file.readlines():
                if ':' not in line :
                    continue
                line = line.rstrip()
                mer_name = self.get_mername_by_sname(line.split(':')[0])
                self.update_mer(mer_name, baozang_list=line.split(':')[1].split(' '))
        print('baozang succ.{}'.format(len(self.out_dict['佣兵'])))
        return self.out_dict
    
    # 解析 碎片来源
    def insert_frags(self, frag_path):
        first_num = 0
        with open(frag_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if '--' in row[0]:
                    first_num += 1
                    continue
                for i in range(len(row)):
                    self.update_mer(row[i], frag_instance=("{}-{}".format(first_num,i+1)))
                    self.update_instance("{}-{}".format(first_num, i+1))
    # 解析英雄装备
    def insert_yingxiongzhuangbei(self, path):
        with open(path, 'r') as file:
            csv_reader = csv.reader(file)
            total_line = 0
            for row in csv_reader:
                if '-' not in row[0]:
                    continue

                total_line += 1
                second_num = row[0].split('-')[-1]
                first_num = row[0].split(' ')[-1].split('-')[0]
                zhuangbei_ins = {"副本":"{}-{}".format(first_num,second_num),
                                 "难度":"英雄"} 
                # print('{}:{}'.format(zhuangbei_ins, row))
                for s_name in row[1].split(' '):
                    self.update_mer(s_name,zhuangbei_instanse=zhuangbei_ins)
    # 最后的微调
    def end_just(self):
        self.update_mer('凯瑞尔·罗姆',skill_circle='231',sequence=1)
        self.update_mer('剑圣萨穆罗',skill_pri='123',sequence=2)
        self.update_mer('泽瑞拉',skill_pri='123',sequence=3)
        self.update_mer('巴琳达·斯通赫尔斯',skill_circle='132',sequence=1)
        self.update_mer('迦顿男爵',skill_pri='231',sequence=2)
        self.update_mer('拉格纳罗斯',skill_pri='231',sequence=3)
        self.update_mer('玛法里奥·怒风',skill_circle='132',sequence=1)
        self.update_mer('古夫·符文图腾',skill_pri='231',sequence=2)
        self.update_mer('布鲁坎',skill_circle='113',sequence=3)
        # self.update_mer('莉莉安·沃斯',zhuangbei_instanse= copy.deepcopy({'副本':'2-2','难度':'普通'}))
        self.out_dict['佣兵']['莉莉安·沃斯']['装备解锁']['难度'] = '普通'



    # 输出基础配置
    def out_yml(self,path):
        with open(path, 'w') as f:
            yaml.dump(self.out_dict, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)


if __name__ == '__main__':
    in_mer_path = '/Users/allen/code/ws_py/mercenary/mercenaries_sailing181#3954_2023_03_11_11_50_23.csv'
    baozhang_path = '/Users/allen/code/ws_py/mercenary/init_conf/baozang.txt'
    frag_path = '/Users/allen/code/ws_py/mercenary/init_conf/frag.csv'
    yingxiongzhuangbei_path = '/Users/allen/code/ws_py/mercenary/init_conf/yingxiongzhuangbei.csv'
    init_conf = InitConf()
    init_conf.analysis_csv(in_mer_path)
    # 解析 宝藏来源
    init_conf.insert_baozang(baozhang_path)
    # 解析 碎片来源
    init_conf.insert_frags(frag_path)
    # TODO:解析 英雄本装备
    init_conf.insert_yingxiongzhuangbei(yingxiongzhuangbei_path)
    # 最后微调
    init_conf.end_just()
    init_conf.out_yml('/Users/allen/code/ws_py/mercenary/init_conf/base_conf.yml')
    