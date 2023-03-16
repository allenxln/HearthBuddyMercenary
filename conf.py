# coding=utf-8
# by allen.xu
# 解析配置文件的库

import json
import yaml

class Conf:
    def __init__(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)

        with open('./conf/mercenary.yml') as f:
            self.mer_conf = yaml.safe_load(f)
        with open('./conf/instance.yml') as f:
            self.instance_conf = yaml.safe_load(f)
    
    def get_mer_team_conf(self,mer_name):
        return self.mer_conf['佣兵'][mer_name]
    
    def print_mer(self):
        print(type(self.mer_conf['佣兵']['拉格纳罗斯']['碎片来源']))
        print(len(self.mer_conf['佣兵']['拉格纳罗斯']['碎片来源']))
        print(self.mer_conf['佣兵']['拉格纳罗斯']['碎片来源'])
    
#获取佣兵在队伍里面的配置
def get_mer_team_conf(mer_name):
    pass



if __name__ == '__main__':
    import os
    # 获取当前文件所在目录
    # 打印当前工作目录
    print(os.getcwd())

    base_conf = Conf()
    base_conf.print_mer()
    print(base_conf.get_mer_team_conf('拉格纳罗斯'))
    