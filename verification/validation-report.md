# 示例验证记录

文档核对日期：2026-10-15。

## 本次实际运行

引擎：RDFLib 7.5.0；Python 3.13.5。

执行 `python verification/verify_examples.py`：**15 项检查，0 项失败，0 项错误**。

验证内容：Turtle 解析、SPARQL 聚合结果、3 条装配行证据、草稿/过期/新版本筛选、普通图与显式子类路径的区别、一个最小子类规则的独立演示、相同三元组去重、Shapes 内一个 SPARQL 约束查询、币种冲突、生效时间边界、缺价和多价反例。

正常数据的结果为 V-A / STD / CNY / 用量1 / 单车增量20，V-B / PRO / CNY / 用量2 / 单车增量40。

## 未验证的内容

未在 Apache Jena 6.2.0 运行时执行；未编译 Java 示例；未运行完整 Jena SHACL Core；未部署 Fuseki HTTP 服务；未验证 TDB2 持久化、事务或生产性能。

原因：当前环境具备 Java 21，但无法连接下载 Jena 分发包。

RDFLib 检查不能替代 Jena 集成测试。脚本中的最小子类规则不是完整 RDFS/OWL 推理器；脚本对缺价、多价所做的前置条件检查也不是 SHACL 引擎。一个内嵌 SPARQL 约束查询单独执行成功，不代表完整 Shapes 已通过 SHACL 校验。

## 可复查文件

`test-log.txt`：每项检查结果。
`test-results.json`：引擎版本、汇总与预期结果。
`verify_examples.py`：实际执行的检查脚本。

所有测试数据均为合成教学数据。
