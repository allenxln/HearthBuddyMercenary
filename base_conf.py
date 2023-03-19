# coding=utf-8
# by allen.xu
# 解析配置文件的库

from collections import Counter
import csv
import os
import copy
import json
import yaml
import sys

class BaseConf:
    def __init__(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)

        with open('base_conf.yml') as f:
            self.base_conf = yaml.safe_load(f)


    def get_mer_conf(self,mer_name):
        return copy.deepcopy(self.base_conf['佣兵'][mer_name])
    
    # 获取 未解锁佣兵mer_names中 交叉碎片最多的副本名称
    def get_max_instance_by_mers(self, mer_names):
        ins_lst = []
        for mer_name in mer_names:
            ins_lst += self.get_mer_conf(mer_name)['碎片来源']
        
        counter = Counter(ins_lst)
        sorted_list = sorted(set(ins_lst),key=lambda x: counter[x], reverse=True)
        return sorted_list[0]
    
    def get_mer_names_by_team_name(self, team_name):
        if  'ALL' == team_name:
            return [x for x in (self.base_conf['佣兵'].keys())]
        return copy.deepcopy(self.base_conf['队伍'][team_name])
    
    def get_teamnames(self):
        return [x for x in self.base_conf['队伍'].keys()]
    
    def get_teamname_by_instance(self,instance):
        return copy.deepcopy(self.base_conf['地图'][instance])



#1.根据佣兵等级从低到高排。
#2.根据任务等级从低到高排。
#3.根据碎片数量从低到高排。
def sorted_mercenaries(mercenaries_dict, mercenaries_lst = [], prop_name = 'level'):
    if len(mercenaries_lst) <= 0:
        mercenaries_lst = list(mercenaries_dict.keys())
    if prop_name == 'level':
        mercenaries_lst = [x for x in mercenaries_lst if mercenaries_dict[x]['level'] < 30]
        return sorted(mercenaries_lst, key= lambda x: mercenaries_dict[x]['level'])
    if prop_name == 'task':
        mercenaries_lst = [x for x in mercenaries_lst if mercenaries_dict[x]['task'] <= 7]
        return sorted(mercenaries_lst, key= lambda x: mercenaries_dict[x]['task'])
    if prop_name == 'fragment':
        return sorted(mercenaries_lst, key= lambda x: mercenaries_dict[x]['fragment'])

    sorted_array = sorted(mercenaries_lst, key=lambda x: (
                            mercenaries_dict[x]['level'],
                            mercenaries_dict[x]['task'] if mercenaries_dict[x]['task'] <= 7 else 99999,
                            mercenaries_dict[x]['fragment'] if mercenaries_dict[x]['fragment'] <= 2700 else 99999)
                            )
    return sorted_array


class MercenariesInfo:
    def __init__(self, mer_stat_path):
        self.mer_stat_path = mer_stat_path
        self.all_mer_stat = {}
        self.analysis_csv(mer_stat_path)

        self.level_pro_mercenaries_lst = sorted_mercenaries(self.all_mer_stat,prop_name='level')
        self.task_pro_mercenaries_lst = sorted_mercenaries({k:v for k,v in self.all_mer_stat.items() if k not in set(self.level_pro_mercenaries_lst)},prop_name='task')
        self.fragment_pro_mercenaries_lst = sorted_mercenaries({k:v for k,v in self.all_mer_stat.items() if k not in set(self.level_pro_mercenaries_lst + self.task_pro_mercenaries_lst)},prop_name='fragment')
        
    def analysis_csv(self, path):
        with open(path, 'r') as file:
            csv_reader = csv.reader(file)
            total_line = 0
            for row in csv_reader:
                if ('等级' in row[1]):
                    continue
                total_line += 1
                # print(row)
                self.all_mer_stat[row[0]] = {'level': int(
                    row[1]), 'fragment': int(row[2]), 'task': int(row[3])}
            print('analysis_csv succ. {}->{}'.format(total_line,len(self.all_mer_stat)))

    # 获取还没生成的佣兵
    def get_no_mercenaries(self, orig_mers = []):
        if  len(orig_mers) <= 0:
            orig_mers = self.level_pro_mercenaries_lst
        return [x for x in orig_mers if self.all_mer_stat[x]['level'] <= 0 and self.all_mer_stat[x]['fragment'] < 500]
    
    def get_less30_mercenaries(self, orig_mers = []):
        if len(orig_mers) <= 0:
            orig_mers = self.level_pro_mercenaries_lst
        return [x for x in orig_mers if self.all_mer_stat[x]['level'] > 0 and self.all_mer_stat[x]['level'] < 30]
    
    def get_task_mercenaries(self, orig_mers = []):
        if len(orig_mers) <= 0:
            orig_mers = self.task_pro_mercenaries_lst
        return [x for x in orig_mers if self.all_mer_stat[x]['task'] <= 7]
    
    def get_fragment_mercenaries(self, orig_mers = []):
        if len(orig_mers) <= 0:
            orig_mers = self.fragment_pro_mercenaries_lst
        return [x for x in orig_mers if self.all_mer_stat[x]['fragment'] <= 2700]
    
    def get_min_level(self, mercenaries_lst):
        return min([self.all_mer_stat[x]['level'] for x in mercenaries_lst])
    
    def get_min_task(self, mercenaries_lst):
        return min([self.all_mer_stat[x]['task'] for x in mercenaries_lst])
    
    #如果用户没有解锁目标副本，则先打目标副本的前置副本。
    # TODO: 当前按照默认全部解锁计算。需要用户可以打的副本
    def get_first_instance_by_target_instance(self, target_instances_lst):
        # TODO: 这里要导入用户还未解锁的副本，以及所有副本的前置副本。 如果用户已经解锁 target_instance，则 first_instance 就等于 target_instance
        first_instance_lst = target_instances_lst
        return first_instance_lst
    
    # 获取不存在的佣兵
    def not_exist_mers(self, mer_names = []):
        if len(mer_names) <= 0:
            mer_names = [x for x in  self.all_mer_stat.keys()]
        return [x for x in mer_names if self.get_min_level([x]) <= 0]
    
    # 佣兵们是否ready了（1.是否全满级；2.任务7是否已完成。不关心是否 全+1+5）
    def not_ready_mers(self, mer_names = []):
        if len(mer_names) <= 0:
            mer_names = [x for x in  self.all_mer_stat.keys()]
        return [x for x in mer_names if self.get_min_level([x]) >= 30 and self.get_min_task([x]) > 7]
    

    def __str__(self):
        return '\n'.join(self.all_mer_stat)

    def __deepcopy__(self):
        new_mer_info = MercenariesInfo(self.mer_stat_path)
        return new_mer_info

class InstanceInfo:
    def __init__(self, instance_path = '') -> None:
        self

class ConfOut:
    def __init__(self,
                 mer_stat_path,
                 default_team_name = '', 
                 is_task = False, 
                 instance_method = '依队伍设置按顺序打',
                 hit_method = '各打各克制，从左到右'
                 ) -> None:
        self.mer_conf = MercenariesInfo(mer_stat_path)
        self.base_conf = BaseConf()
        self.mer_team_setting = {}  #佣兵队伍设置。key是佣兵名
        self.is_task = is_task #是否允许做任务
        self.instance_method = instance_method #“关卡”这个位置的字段。
        self.events = {'复活无阵亡': 3, '复活有阵亡': 10}  #事件和分值
        self.hit_method = hit_method #选怪模式
        self.all_target = '货车 冷饮 祝踏岚 尤格 克洛 盖斯 大帝 欧莫克 奥妮克希亚幼龙 恩佐斯的鱼 德雷 拉佐格尔 女皇 加尔 雪崩 冰吼 碎片 巫师 宝宝 图腾 猫头鹰 安度因 艾萨拉 拉格 占卜 瓦莉拉 猎手 巨兽 战斗法师 防御者幼龙 雷矛羊骑兵 瞎眼 复仇 船长 指挥官 食人鱼 龙王 古尔丹 罗杰斯 休息 螳螂塑像 火山幼龙 塞林 火焰领主 雷矛特种兵 傀儡 始祖龟 奥秘 走私 酒吧醉汉 迦顿 维伦 反射 恐吓 剑鱼 雷矛 巨人 虚空 猛犸 雕像 冰雪 军需官 老瞎眼 冰霜暴怒者 图腾 奶牛 瓦拉 雷矛狂战士 小丑 暗月 恩佐斯 牛怪 奴隶 火焰驱逐者 迦罗娜 守卫 毒心者 雷矛防御者 女妖 将军'.split(' ') #集火目标，list格式
        self.avoid_mer = '精灵龙 塔姆辛 古尔丹 安度因 晨拥 塞林 沃金 米尔 安东尼 老瞎眼 伊利丹 雷矛 刀油 瓦莉拉'.split(' ')
        self.team_target_instances = {} #队伍设置内设置的目标关卡
        self.extra_mer = {'绝命':1,'冰墙':0, '战棋':2,'黑棋':1,'宝珠':0,'冰块':0}
        if len(default_team_name) > 0:
            self.add_mercenaries(self.mer_conf.get_mernames_by_teamname(default_team_name))
    
    # 获取当前队伍还有多少空位
    def get_empty_mer_lst_cnt(self):
        return 6 - len(self.mer_team_setting)

    # 设置 未有佣兵的刷碎片模式
    def set_non_frag_model(self,need_mers):
        target_instance = self.base_conf.get_max_instance_by_mers(need_mers)
        first_instance = self.mer_conf.get_first_instance_by_target_instance(target_instance)
        team_names = self.base_conf.get_teamname_by_instance(first_instance)
        for team_name in team_names:
            mer_names = self.base_conf.get_mer_names_by_team_name(team_name)
            if self.mer_conf.get_min_level(mer_names) <= 0:
                print('{} 佣兵不全'.format(team_name))
                continue
            else:
                last_team = team_name
                break
        if len(last_team) <= 0 :
            print('{} need {}, no team exists'.format(first_instance, team_names))
            return
        mer_names = self.base_conf.get_mer_names_by_team_name(last_team)
        self.mer_team_setting.clear()
        self.add_mercenaries(mer_names)

        # 刷碎片的同时，升级未满级的佣兵
        rest_mers = self.mer_conf.get_less30_mercenaries()
        # if len(rest_mers) > self.get_empty_mer_lst_cnt():
        #     rest_mers = rest_mers[0:(self.get_empty_mer_lst_cnt())]
        if len(rest_mers) > 0:
            self.add_mercenaries(rest_mers)
        # 设置攻击副本
        self.team_target_instances = {'副本':first_instance,'难度':'普通'}

    # 设置 升级模式。
    def set_update_model(self, mer_names):
        self.instance_method = '随机打'
        self.mer_team_setting.clear()
        # 随机找个已经有了的队伍：
        for team_name in ['自然队','巴斯顿','御三家']:
            if len(self.mer_conf.not_exist_mers(self.base_conf.get_mer_names_by_team_name(team_name))) <= 0:
                self.add_mercenaries(self.base_conf.get_mer_names_by_team_name(team_name))
                break
        self.add_mercenaries(mer_names)
        # 如果还有空位，则补上其他未满级的佣兵
        rest_mers = self.mer_conf.get_less30_mercenaries()
        # if len(rest_mers) > self.get_empty_mer_lst_cnt():
        #     rest_mers = rest_mers[0:(self.get_empty_mer_lst_cnt())]
        if len(rest_mers) > 0:
            self.add_mercenaries(rest_mers)
        

    # 设置 任务1-7模式
    def set_task_model(self, mer_names):
        self.team_target_instances = {'副本':'1-2','难度':'英雄'}
        self.mer_team_setting.clear()
        self.add_mercenaries(mer_names)
        self.is_task = True
        self.events['赐福护卫'] = 5
        self.events['赐福斗士'] = 5
        self.events['赐福施法者'] = 5

        # 如果有其他的佣兵还没做完7级以前的任务，也一起加进来
        for mer_name in self.mer_conf.get_task_mercenaries():
            if len(self.mer_team_setting) >= 3:
                break
            self.add_mercenaries([mer_name])

    # 设置 +1+5 刷碎片毕业模式
    def set_frag_model(self, mer_names):
        self.team_target_instances = {'副本':'1-1','难度':'普通'}
        if len(mer_names) >= 3:
            self.team_target_instances['难度'] = {'英雄'}
        self.is_task = True
        self.mer_team_setting.clear()
        self.add_mercenaries(mer_names)
        if len(self.mer_team_setting) <= 3:
            # 刷普通1-1的利器
            for mer_name in ['拉格纳罗斯', '暴龙王克鲁什']:
                if self.mer_conf.get_min_level([mer_name]) > 0:
                    self.add_mercenaries([mer_name])
        # for mer_name in self.mer_conf.get_fragment_mercenaries():
        #     if len(self.mer_team_setting) >= 3:
        #         break


    
    # 设置 英雄本解锁装备模式
    def set_hero_instance_equip_model(self):
        # TODO: 
        pass


    # 新增佣兵
    def add_mercenaries(self,mer_names) -> None:
        # 过滤已有佣兵
        mer_names = [x for x in mer_names if x not in self.mer_team_setting]
        if len(mer_names) <= 0:
            return None
        # if len(mer_names) + len(self.mer_team_setting) > 6:
        #     print('ERR 总佣兵超过6个。当前:{} ，新加:{}'.format(self.get_mer_names(), mer_names))
        #     return None
        for name in mer_names:
            if len(self.mer_team_setting) >= 6:
                print('佣兵队伍已经满员:{}'.format(self.get_mer_names()))
                break
            add_mer = self.base_conf.get_mer_conf(name)
            add_mer['默认出场顺序'] = len(self.mer_team_setting) + 1
            self.mer_team_setting[name] = copy.deepcopy(add_mer)

    # 替换备用佣兵
    def replace_mercenaries(self,mer_names) -> None:
        # 过滤已有佣兵
        mer_names = [x for x in mer_names if x not in self.mer_team_setting]
        add_num = len(mer_names)
        if add_num > 6:
            print('新加佣兵超过6个。{}'.format(mer_names))
            return
        now_mer_num = len(self.mer_team_setting)
        if now_mer_num + add_num > 6:
            # 只保留未超出的部分
            self.mer_team_setting = {k: copy.deepcopy(v) for k,v in self.mer_team_setting.items() if v['默认出场顺序'] <= 6 - add_num}
        #重新加进来
        self.add_mercenaries(mer_names)
            
    def get_mer_names(self):
        return [x for x in self.mer_team_setting.keys()]
    
    def yaml_output(self, outpath):
        # 将字典转换为 YAML 格式的字符串
        all_dict = {'允许交任务':self.is_task,
                    '关卡方式':self.instance_method,
                    '队伍设置':{'佣兵配置':copy.deepcopy(self.mer_team_setting),
                                '事件':copy.deepcopy(self.events),
                                '选怪模式':self.hit_method,
                                '集火目标': copy.deepcopy(self.all_target),
                                '尽量不走': copy.deepcopy(self.avoid_mer),
                                '指定关卡': copy.deepcopy(self.team_target_instances),
                                '衍生佣兵': copy.deepcopy(self.extra_mer)}
        }

        # 将 YAML 字符串写入文件中
        with open(outpath, 'w') as f:
            yaml.dump(all_dict, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
            # f.write(yaml_str)
    def print_mer(self):
        print(type(self.mer_conf['佣兵']['拉格纳罗斯']['碎片来源']))
        print(len(self.mer_conf['佣兵']['拉格纳罗斯']['碎片来源']))
        print(self.mer_conf['佣兵']['拉格纳罗斯']['碎片来源'])


# python ./base_conf.py 该python文件将佣兵配置输出到哪个路径的哪个文件下面 脚本出来的佣兵文件的路径 ...
if __name__ == '__main__':
    import os
    # 获取当前文件所在目录
    # 打印当前工作目录
    print(os.getcwd())
    yml_out_path = './mer_conf.yml'
    mer_stat_path = '/Users/allen/code/ws_py/mercenary/mercenaries_sailing181#3954_2023_03_11_11_50_23.csv'
    if len(sys.argv) >= 3:
        yml_out_path = sys.argv[1]
        mer_stat_path = sys.argv[2]
    conf_out = ConfOut( mer_stat_path=mer_stat_path)
    for team_name in ['御三家', '自然队', '巴斯顿', 'ALL']:
        print('开始检测队伍 {}'.format(team_name))
        mers = conf_out.base_conf.get_mer_names_by_team_name(team_name)
        non_mers = conf_out.mer_conf.get_no_mercenaries(mers)
        if len( non_mers ) > 0:
            print("{} 存在未解锁的英雄. 尝试解锁英雄：{}".format(team_name,non_mers))
            if '御三家' in team_name:
                print(' ERROR, 御三家 有 {} 未解锁，请先手动做主线任务解锁'.format(non_mers))
                continue
            conf_out.set_non_frag_model(need_mers=non_mers)
            conf_out.yaml_output(yml_out_path)
            break
        else:
            #TODO: 刷英雄装备。前提是需要先知道哪些英雄的装备没解锁，哪些英雄的装备解锁了
            less_30_mers = conf_out.mer_conf.get_less30_mercenaries(mers)
            if len(less_30_mers) > 0:
                print('{} 存在未满级的英雄: {}, 开始升级'.format(team_name,less_30_mers))
                conf_out.set_update_model(mer_names=less_30_mers)
                conf_out.yaml_output(yml_out_path)
                break
            else:
                less_task_7_mers = conf_out.mer_conf.get_task_mercenaries(mers)
                if len(less_task_7_mers) > 0:
                    print('{} 存在任务不到7的英雄:{}, 开始做任务'.format(team_name,less_task_7_mers))
                    conf_out.set_task_model(less_task_7_mers)
                    conf_out.yaml_output(yml_out_path)
                    break
                else:
                    less_frag_mers = conf_out.mer_conf.get_fragment_mercenaries(mers)
                    if len(less_frag_mers) > 0:
                        print('{} 中{}没有+1+5,开始刷'.format(team_name,less_frag_mers))
                        conf_out.set_frag_model(less_frag_mers)
                        conf_out.yaml_output(yml_out_path)
                        break
        
        