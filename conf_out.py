# coding=utf-8
# by allen.xu
# 解析配置文件的库

import copy
import json
import yaml

from base_conf import BaseConf

class ConfOut:
    def __init__(self,default_team_name = '', 
                 is_task = False, 
                 instance_method = '依队伍设置按顺序打',
                 hit_method = '各打各克制，从左到右',
                 all_target = [],
                 events = {'复活无阵亡': 3,
                           '复活有阵亡': 10},
                 extra_mer = {'绝命':1},
                 ) -> None:
        self.base_conf = BaseConf()  #佣兵基础配置
        self.mer_team_conf = {}  #佣兵队伍设置。key是佣兵名
        self.is_task = is_task #是否允许做任务
        self.instance_method = instance_method #“关卡”这个位置的字段。
        self.events = events  #事件和分值
        self.hit_method = hit_method #选怪模式
        self.all_target = all_target #集火目标，list格式
        self.team_target_instances = [] #队伍设置内设置的目标关卡
        self.extra_mer = extra_mer
        self.add_mercenaries(self.base_conf.get_mer_names_by_team_name(default_team_name))

    # 新增佣兵
    def add_mercenaries(self,mer_names) -> None:
        # 过滤已有佣兵
        mer_names = [x for x in mer_names if x not in self.mer_team_conf]
        if len(mer_names) + len(self.mer_team_conf) > 6:
            print('ERR 总佣兵超过6个。当前：{} ，新加：{}'.format(self.get_mer_names(), mer_names))
            return None
        for name in mer_names:
            add_mer = self.base_conf.get_mer_team_conf(name)
            add_mer['默认出场顺序'] = len(self.mer_team_conf) + 1
            self.mer_team_conf[name] = copy.deepcopy(add_mer)

    # 替换备用佣兵
    def replace_mercenaries(self,mer_names) -> None:
        # 过滤已有佣兵
        mer_names = [x for x in mer_names if x not in self.mer_team_conf]
        add_num = len(mer_names)
        if add_num > 6:
            print('新加佣兵超过6个。{}'.format(mer_names))
            return
        now_mer_num = len(self.mer_team_conf)
        if now_mer_num + add_num > 6:
            # 只保留未超出的部分
            self.mer_team_conf = {k: copy.deepcopy(v) for k,v in self.mer_team_conf.items() if v['默认出场顺序'] <= 6 - add_num}
        #重新加进来
        self.add_mercenaries(mer_names)
            
    def get_mer_names(self):
        return [x for x in self.mer_team_conf.keys()]
    def yaml_output(self, outpath):
        # 将字典转换为 YAML 格式的字符串
        all_dict = {'允许交任务':self.is_task,
                    '关卡方式':self.instance_method,
                    '队伍设置':{'佣兵配置':copy.deepcopy(self.mer_team_conf),
                                '事件':copy.deepcopy(self.events),
                                '选怪模式':self.hit_method,
                                '集火目标': copy.deepcopy(self.all_target),
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

if __name__ == '__main__':
    import os
    # 获取当前文件所在目录
    # 打印当前工作目录
    print(os.getcwd())

    conf_out = ConfOut(default_team_name='御三家')
    conf_out.add_mercenaries(['巴琳达·斯通赫尔斯'])
    conf_out.replace_mercenaries(['玛法里奥·怒风', '古夫·符文图腾', '布鲁坎'])
    conf_out.yaml_output('./mer_conf.yml')

    