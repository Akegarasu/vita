# Project Vita

***Via et veritas et vita***
```

 ______   ______     ______       __     ______     ______     ______  
/\  == \ /\  == \   /\  __ \     /\ \   /\  ___\   /\  ___\   /\__  _\ 
\ \  _-/ \ \  __<   \ \ \/\ \   _\_\ \  \ \  __\   \ \ \____  \/_/\ \/ 
 \ \_\    \ \_\ \_\  \ \_____\ /\_____\  \ \_____\  \ \_____\    \ \_\ 
  \/_/     \/_/ /_/   \/_____/ \/_____/   \/_____/   \/_____/     \/_/ 
                                                                       
 __   __   __     ______   ______                                      
/\ \ / /  /\ \   /\__  _\ /\  __ \                                     
\ \ \'/   \ \ \  \/_/\ \/ \ \  __ \                                    
 \ \__|    \ \_\    \ \_\  \ \_\ \_\                                   
  \/_/      \/_/     \/_/   \/_/\/_/                                                                                                       

GitHub: https://github.com/Akegarasu/vita/tree/main/core                         


"Via et veritas et vita" is a Latin phrase meaning "the way and the truth and the life".
The words are taken from Vulgate version of John 14:6  

"The project name is come from The Bible, not something else, like lemon tea."
                                                                   --Ibukifalling
```

## introduction

Vita是一款**白盒代码审计**工具，支持检测源代码中的安全问题和漏洞，可以帮助开发人员和安全研究人员快速发现项目中的安全风险

Vita使用AST进行源码分析，并且针对每个风险点给出危险等级和危险描述，以帮助使用者快速了解风险点出现的原因与影响程度

Vita支持**Java**、**Python**、**Go**的源码自动化审计，并生成分析报告

项目名称取自拉丁语“生命”

## 安装

使用以下命令安装Vita
```
git clone https://github.com/Akegarasu/vita
```

安装依赖
```
pip install -r requirements.txt
```

## Usage

```
python ./main.py -t [目标文件目录] -r [规则文件目录]
```

目标文件目录即为待检测的项目根目录

如果要使用Vita的默认规则库，请使用以下命令

```
python ./main.py -t [目标文件目录] -r ./data/
```

## 特点

- 支持静态分析与语义分析的双重分析方式
    - 静态分析速度快，稳定性高，适用于快速发现显著的安全风险
    - 语义分析支持复杂漏洞的发现，适用于发现一些逻辑较深的风险场景
    - Vita结合两种分析模式，对风险场景拥有广而深的发现能力

- 以Python为Base语言实现了整体的功能框架，在设计上预留二次开发空间

- 风险分级和风险概述，帮助使用者快速了解重点安全问题

- 支持生成html形式的报告



## Documents

### 目录结构

```
├─core #核心框架部分
│  └─ast_gen #各语言的ast生成逻辑
│
├─data #数据目录
│  └─rules #规则目录，用于存放匹配规则
│
└─templates #生成html报告的模板
   ├─css #样式表
   └─lib #库依赖
```




### 规则文件示例
```yaml
language: python # 此规则对应的语言

rules:
  - id: 1 # id 可以随便写
    name: test # 规则名称
    description: 测试 # 规则描述
    ptype: vuln # 风险类型 vuln--漏洞 backdoor--后门 danger--危险
    type: regex # 匹配类型 regex--直接正则匹配 ast--ast分析后函数匹配
    danger: 10 # 危险程度打分 （0-10）
    weight: 0.4 # 置信计算用权重
    patterns: # 正则规则（数组）
      - e.+?x
```


### 各语言的AST实现

#### java

通过引入第三方库实现
https://github.com/c2nes/javalang

#### go

[《Go语言定制指南》](https://chai2010.cn/go-ast-book/ch4/index.html)
参考go语言原生的ast构建方式，最后使用python实现对go语言的词法与语法分析，运用NFA,DFA等知识，使用LEX进行词法分析，运用创建的ACTION与GOTO表，使用YACC进行语法分析，最终生成AST。
![](https://md.buptmerak.cn/uploads/upload_bbd464c170c5bba7a287a88771cef343.png)



#### python

使用python内置的编译函数实现

```python=
import ast

a = ast.dump(ast.parse('''
eval("")#teststsst
def test():
    return "1"
test()
'''))

print(a)
```

