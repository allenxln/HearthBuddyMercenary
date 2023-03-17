# coding=utf-8
# by allen.xu
# 解析配置文件的库

import os
import copy
import json
import yaml

class BaseConf:
    def __init__(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)

        with open('./base_conf.yml') as f:
            self.base_conf = yaml.safe_load(f)
    
    def get_mer_team_conf(self,mer_name):
        return copy.deepcopy(self.base_conf['佣兵'][mer_name])
    
    def get_mer_names_by_team_name(self, team_name):
        return copy.deepcopy(self.base_conf['队伍'][team_name])
    def print_mer(self):
        print(type(self.base_conf['佣兵']['拉格纳罗斯']['碎片来源']))
        print(len(self.base_conf['佣兵']['拉格纳罗斯']['碎片来源']))
        print(self.base_conf['佣兵']['拉格纳罗斯']['碎片来源'])
    
#获取佣兵在队伍里面的配置
def get_mer_team_conf(mer_name):
    pass



if __name__ == '__main__':
    import os
    # 获取当前文件所在目录
    # 打印当前工作目录
    print(os.getcwd())

    base_conf = BaseConf()
    base_conf.print_mer()
    print(base_conf.get_mer_team_conf('拉格纳罗斯'))
    