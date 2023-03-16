from collections import Counter
import copy
import csv
import json
import sys

import os

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录设置为起始路径
os.chdir(current_dir)

# 打印当前工作目录
print(os.getcwd())



#1.根据佣兵等级从低到高排。
#2.根据任务等级从低到高排。
#3.根据碎片数量从低到高排。
def sorted_mercenaries(mercenaries_dict,mercenaries_lst = [], prop_name = 'level'):
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


class HubbyConf:
    # team_name 队伍模板名。 “巴斯顿” “火焰队” “自然队” “御三家” 或者为空
    # mercenaries 替换模板最后几个的佣兵。
    # target_instance 目标副本。 比如 '1-1 普通' or '1-2 英雄' 
    # allow_task 是否允许做任务。

    def __init__(self):
        self.conf = {}
    
    def init(self, team_name, mercenaries, target_instance, allow_task = False, hit_way = '从左到右,各打各克制'):
        self.conf = {}
        self.conf['team_name'] = team_name
        self.conf['mercenaries'] = copy.deepcopy(mercenaries)
        self.conf['target_instance'] = target_instance
        self.conf['allow_task'] = allow_task
        self.conf['hit_way'] = hit_way

    def __str__(self):
        return json.dumps(self.conf, ensure_ascii=False)

    def __deepcopy__(self, memo):
        return HubbyConf(copy.deepcopy(self.team_name, memo), copy.deepcopy(self.mercenaries, memo), copy.deepcopy(self.target_instance, memo), copy.deepcopy(self.allow_task, memo))


class MercenariesInfo:
    def __init__(self, mercenaries_dict):
        self.mercenaries_dict = copy.deepcopy(mercenaries_dict)
        self.level_pro_mercenaries_lst = sorted_mercenaries(self.mercenaries_dict,prop_name='level')
        self.task_pro_mercenaries_lst = sorted_mercenaries({k:v for k,v in self.mercenaries_dict.items() if k not in set(self.level_pro_mercenaries_lst)},prop_name='task')
        self.fragment_pro_mercenaries_lst = sorted_mercenaries({k:v for k,v in self.mercenaries_dict.items() if k not in set(self.level_pro_mercenaries_lst + self.task_pro_mercenaries_lst)},prop_name='fragment')
        
    
    def get_no_mercenaries(self):
        # TODO:
        return []
        return [x for x in self.level_pro_mercenaries_lst if self.mercenaries_dict[x]['level'] <= 0 and self.mercenaries_dict[x]['fragment'] < 500]
    
    def get_less30_mercenaries(self):
        # TODO:
        return []
        return [x for x in self.level_pro_mercenaries_lst if self.mercenaries_dict[x]['level'] > 0 and self.mercenaries_dict[x]['level'] < 30]
    
    def get_task_mercenaries(self):
        return [x for x in self.task_pro_mercenaries_lst if self.mercenaries_dict[x]['task'] <= 7]
    
    def get_fragment_mercenaries(self):
        return [x for x in self.fragment_pro_mercenaries_lst if self.mercenaries_dict[x]['fragment'] <= 2700]
    
    def get_min_level(self, mercenaries_lst):
        return min([self.mercenaries_dict[x]['level'] for x in mercenaries_lst])
    
    def get_min_task(self, mercenaries_lst):
        return min([self.mercenaries_dict[x]['task'] for x in mercenaries_lst])
    
    # 队伍是否ready了（1.是否全满级；2.任务7是否已完成。暂时不看 全+1+5）
    def is_team_ready(self, team_name_lst):
        mer_lst = get_mercenaries_from_team_name(team_name_lst)
        return self.get_min_level(mer_lst) >= 30 and self.get_min_task(mer_lst) > 7
    

    # 根据佣兵名字 获取 解锁佣兵要打的副本。
    def get_mercenaryies_instances(self, mercenaries_names):
        ins_lst = []
        for mer_name in mercenaries_names:
            if '玛法里奥·怒风' in mer_name:
                ins_lst += ['2-3']
            if '古夫·符文图腾' in mer_name:
                ins_lst += ['1-3']
            if '布鲁坎' in mer_name:
                ins_lst += ['1-4']
            if '拉格纳罗斯' in mer_name:
                ins_lst += ['3-3']
            if '巴琳达·斯通赫尔斯' in mer_name:
                ins_lst += ['5-4']
            if '迦顿男爵' in mer_name:
                ins_lst += ['3-2']
            """ 以及其他佣兵的碎片，都加进来 """
        # 按照副本重复度从高往低排序，尽量1个副本多刷几个碎片。
        counter = Counter(ins_lst)
        sorted_list = sorted(set(ins_lst),key=lambda x: counter[x], reverse=True)
        return sorted_list
    
    #如果用户没有解锁目标副本，则先打目标副本的前置副本。
    def get_first_instance_by_target_instance(target_instances_lst):
        # TODO: 这里要导入用户还未解锁的副本，以及所有副本的前置副本。 如果用户已经解锁 target_instance，则 first_instance 就等于 target_instance
        first_instance_lst = target_instances_lst
        return first_instance_lst
    
    def get_team_conf_from_instances(self, instance_name):
        if instance_name in ['1-3', '1-4','2-3']:  
            # 自然队还没准备好的情况下，用御三家打 instance_name 副本
            if not self.is_team_ready('自然队'):
                return '御三家'
        if instance_name in ['2-4', '2-5', '2-6', '8-1', '8-2']: ##等等 巴斯顿可以打的副本都加进来
            if self.is_team_ready('巴斯顿'):
                return '巴斯顿'
        # 其他情况，用通用的自然队兜底。
        return '自然队' 

    def __str__(self):
        return '\n'.join(self.mercenaries_dict)

    def __deepcopy__(self, memo):
        return HubbyConf(copy.deepcopy(self.team_code, memo), copy.deepcopy(self.instance_code, memo), copy.deepcopy(self.strategy_code, memo), copy.deepcopy(self.instance_method, memo))


# 解析佣兵文件
def analysis_csv(path):
    all_dict = {}
    with open(path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if ('等级' in row[1]):
                continue
            # print(row)
            all_dict[row[0]] = {'level': int(
                row[1]), 'fragment': int(row[2]), 'task': int(row[3])}
    return all_dict



# TODO:慢慢加佣兵的宝藏和配置
# 获取 某个佣兵的技能顺序 和 宝藏列表。 key = 佣兵名，skill_seq = 技能顺序, treasure_lst = 宝物优先级列表
def add_mercenaries_conf(mercenaries_names, mer_conf_dict = {}):
    for mer_name in mercenaries_names:
        mer_conf_dict[mer_name] = {'skill_seq':[1], 'treasure_lst':[]}   # 没有囊括进来的佣兵，取默认配置
        if '拉格纳罗斯' in mer_name:
            mer_conf_dict['拉格纳罗斯'] = {'skill_seq':[2], 'treasure_lst':'研究 齐射 火焰 炸弹 铁管 强韧 怪异 萨隆 元素 狱火 火舌'.split(' ')}
        if '巴琳达·斯通赫尔斯' in mer_name:
            mer_conf_dict['巴琳达·斯通赫尔斯'] = {'skill_seq':[1], 'treasure_lst':'埃提 研究 齐射 救援 强化 之杖 铁管 联盟 暴风 急速 吃饱'.split(' ')}
        if '迦顿男爵' in mer_name:
            mer_conf_dict['迦顿男爵'] = {'skill_seq':[2], 'treasure_lst':'研究 齐射 炸弹 火焰 铁管 狱火 元素 火舌 萨隆 吃饱 -诅咒'.split(' ')}
        if '安东尼达斯' in mer_name:
            mer_conf_dict['安东尼达斯'] = {'skill_seq':[1], 'treasure_lst':'研究 火焰 齐射 强化 狱火 埃提 魔杖 萨隆 暴风 吃饱'.split(' ')}
        if '玛法里奥·怒风' in mer_name:
            mer_conf_dict['玛法里奥·怒风'] = {'skill_seq':[1], 'treasure_lst':'之噬 月下 祝福 强韧 之杖 萨隆 联盟 精灵 超凡 吃饱'.split(' ')}
        if '古夫·符文图腾' in mer_name:
            mer_conf_dict['古夫·符文图腾'] = {'skill_seq':[2], 'treasure_lst':'之噬 月下 祝福 强韧 之杖 大军 超凡 部落 萨隆 防护 尖刺 平衡 图腾'.split(' ')}
        if '布鲁坎' in mer_name:
            mer_conf_dict['布鲁坎'] = {'skill_seq':[1, 1, 3], 'treasure_lst':'雷暴 之噬 月下 祝福 强韧 之杖 野性 防护 强化 部落 萨隆 妖术'.split(' ')}
        if '泽瑞拉' in mer_name:
            mer_conf_dict['泽瑞拉'] = {'skill_seq':[1], 'treasure_lst':'制伏 齐射 之杖 联盟 治疗 乔丹 防护 萨隆 救赎 罪罚'.split(' ')}
        if '凯瑞尔·罗姆' in mer_name:
            mer_conf_dict['凯瑞尔·罗姆'] = {'skill_seq':[1], 'treasure_lst':'联盟 还眼 保护 正义 暴风 萨隆 治疗 防护 胸甲 吃饱'.split(' ')}
        if '剑圣萨穆罗' in mer_name:
            mer_conf_dict['剑圣萨穆罗'] = {'skill_seq':[1], 'treasure_lst':'风怒 免疫 部落 收割 冰霜 之刃 炸弹 萨隆 -诅咒 -急速'.split(' ')}
        if '迪亚波罗' in mer_name:
             mer_conf_dict['迪亚波罗'] = {'skill_seq':[2,3], 'treasure_lst':'灵魂 狱火 收割 战袍 急速 血怒 萨隆 吃饱 烈焰'.split(' ')}
        if '凯恩·血蹄' in mer_name:
             mer_conf_dict['凯恩·血蹄'] = {'skill_seq':[3,2], 'treasure_lst':'强韧 部落 收割 急速 祝福 胸甲 风怒 血怒 萨隆 月下'.split(' ')}
        if '厨师曲奇' in mer_name:
             mer_conf_dict['厨师曲奇'] = {'skill_seq':[2,3], 'treasure_lst':'杂烩 之噬 月下 小鱼 治疗 泡泡 感染 图腾 萨隆 防护 为了 急速 妖术 心能 吃饱'.split(' ')}
    # print(mer_conf_dict)
    return mer_conf_dict



def get_mercenaries_from_team_name(team_name_lst):
    mercenaries_lst = []
    if '御三家' in team_name_lst:
        mercenaries_lst = mercenaries_lst + ['泽瑞拉', '剑圣萨穆罗', '凯瑞尔·罗姆']
    if '自然队' in team_name_lst:
        mercenaries_lst = mercenaries_lst + ['玛法里奥·怒风', '古夫·符文图腾', '布鲁坎']
    if '火焰队' in team_name_lst:
        mercenaries_lst = mercenaries_lst + ['迦顿男爵', '拉格纳罗斯', '安东尼达斯']
    if '巴斯顿' in team_name_lst:
        mercenaries_lst = mercenaries_lst + ['迦顿男爵', '拉格纳罗斯', '巴琳达·斯通赫尔斯']
    return list(set(mercenaries_lst))

def need_frag_from_mercenary(mercenary_name):
    if mercenary_name in ['玛法里奥·怒风', '拉格纳罗斯', '巴琳达·斯通赫尔斯']:
        return 500
    else:
        return 300


# python3 main.py 佣兵数据的输入路径 地图解锁情况的输入路径 输出的配置文件
# 注意 当前没有 地图解锁情况的输入路径 的文件，直接设置为 '' 空字符即可
if __name__ == '__main__':
    in_mer_path = '/Users/allen/code/ws_py/mercenary/佣兵数据_sailing181#3954_2023_03_11_11_50_23.csv'
    out_conf_file = '/Users/allen/code/ws_py/mercenary/mercenary_conf.json'
    if len(sys.argv) >= 4:
        in_mer_path = sys.argv[1]
        out_conf_file = sys.argv[3]
    all_mercenary_dict = analysis_csv(in_mer_path)

    mer_info = MercenariesInfo(all_mercenary_dict)
    hubby_conf = HubbyConf()

    #优先保证 御三家、自然队、巴斯顿 的队伍全满
    #如果 御三家、自然队、巴斯顿 没有 ready，优先刷着三个队伍
    orig_team_name_lst = ['御三家', '自然队', '巴斯顿']
    orig_mercenary_lst = get_mercenaries_from_team_name(orig_team_name_lst)
    orig_mercenary_dict = {k: copy.deepcopy(all_mercenary_dict[k]) for k in set(all_mercenary_dict) & set(orig_mercenary_lst)}
    orig_mer_info = MercenariesInfo(orig_mercenary_dict)

    if not orig_mer_info.is_team_ready(orig_team_name_lst):
        print('{} 有队伍未ready, 优先刷'.format(' '.join(orig_team_name_lst)))
        mer_info = orig_mer_info

    mer_lst = mer_info.get_no_mercenaries()
    if len(mer_lst) >= 1:
        # 先获取 需要打佣兵碎片 的 目标副本
        target_instances = mer_info.get_mercenaryies_instances(mer_lst)
        # 再根据用户当前解锁的情况，找到需要打的副本的前置副本
        first_instances = mer_info.get_first_instance_by_target_instance(target_instances)
        # 最后 根据需要打的副本，选取合适的队伍去攻打
        target_team = mer_info.get_team_conf_from_instances(first_instances[0])
        print('【解锁英雄】 {} 缺碎片，{} 打 {}, 最终目标打{}'.format( mer_lst[0:2], target_team, first_instances[0], target_instances))
        hubby_conf.init(target_team, add_mercenaries_conf(["TODO:这里可以补充2-3个未满级的佣兵，顺便升级用"]), first_instances[0])
    else:
        mer_lst = mer_info.get_less30_mercenaries()
        if len(mer_lst) >= 1:
            print('【刷级别】 {} 未满级, {} 带队刷 {}'.format(mer_lst[0:2], '自然队', 'TODO: 刷其他碎片或者佣兵英雄装备的本'))
            hubby_conf.init('自然队', mer_lst[0:2], 'TODO:这里可以设置 打没有通关的副本，方便后面刷各个佣兵的碎片', True)
        else:
            mer_lst = mer_info.get_task_mercenaries()
            if len(mer_lst) >= 1:
                print('【任务解装备】 {} 刷 英雄本 1-2 解锁 7级之前的装备'.format(mer_lst[0:3]))
                hubby_conf.init('', add_mercenaries_conf(mer_lst[0:3]), '1-2 英雄', True)
            else:
                mer_lst = mer_info.get_fragment_mercenaries()
                if len(mer_lst) >= 1:
                    print('【刷佣兵碎片】 {} 刷 英雄本 1-1 补碎片'.format(mer_lst[0:3]))
                    hubby_conf.init('', add_mercenaries_conf(mer_lst[0:3]), '1-1 英雄', True)
                else:
                    print('【刷荣誉碎片】 恭喜, 全佣兵+1+5, 大螺丝 单刷1-1打荣誉碎片')
                    hubby_conf.init('', add_mercenaries_conf('拉格纳罗斯'), '1-1 普通', False)
    print(hubby_conf)
    with open(out_conf_file, "w") as f:
        f.write(str(hubby_conf))
