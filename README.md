# vita

## 开发须知

为了避免冲突，请不要直接提交 commit 到 main 分支

正确做法：
 - 自己新建 branch 然后 push。需要合并到主分支的时候发起 `pull request`
 - 合并成功后需要建立新的 branch 来同步主分支更改（推荐每个改动都分branch）

## 规则 yaml 文件格式

```yaml
language: python # 此规则对应的语言

rules:
  - id: 1 # id 可以随便写
    name: test # 规则名称
    description: 测试 # 规则描述
    type: regex # 类型 1. regex 直接正则匹配 2. ast ast分析后函数匹配
    danger: 10 # 危险程度打分 （0-10）
    weight: 0.4 # 置信计算用权重 #TODO: 待定, 可选confidence: low,high,medium形式 
    patterns: # 正则规则（数组）
      - e.+?x
  - id: 2
    name: test2
    description: 测试2
    type: regex
    patterns:
      - e.+?x
      - "http://.*"
  - id: 3
    name: test2
    description: 测试2
    type: ast
    patterns:
      - e.+?x
      - "http://.*"
```