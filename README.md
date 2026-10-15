# Apache Jena 介绍与实践指南

主文档：[Apache-Jena-介绍与实践指南.md](Apache-Jena-介绍与实践指南.md)

内容覆盖 Jena 的定位、历史、标准关系、核心概念、组件、架构、数据准备、用户问题处理流程、推理与校验、部署、生态与 Agent 集成。主文档内含 4 张 Mermaid 图和 40 项官方资料索引。

## 阅读与使用

先阅读主文档即可，不需要安装软件或运行示例。支持 Mermaid 的 Markdown 阅读器可渲染图，其他阅读器会显示图源码；正文与文本示意可独立阅读。

`examples/` 是与正文一致的自建汽车研发教学数据，不是企业真实数据，不包含自然语言自动转换，也不是完整生产级多层 BOM 计价软件。

## 示例文件

| 文件 | 作用 |
|---|---|
| `ontology.ttl` | 最小本体，含 RadarBracket → Part 子类关系 |
| `data.ttl` | 零件版本、变更单、BOM、装配行及状态/日期反例 |
| `shapes.ttl` | 单价、用量、状态、日期、版本、币种等示例约束 |
| `impact.rq` | 成本聚合查询；必须先通过约束和业务检查 |
| `evidence.rq` | 逐装配行证据查询 |
| `parts.rq` | 直接查询 Part 类型，用于和推理结果对照 |
| `parts-path.rq` | 显式沿子类路径查询；不是完整推理器 |
| `expected-results.json` | 预期 20 / 40 CNY 与范围说明 |
| `Demo.java` | 读入 → SHACL → 查询的最小 Java 示例 |

## 在本地使用 Jena（待您本地执行）

资料基线为 Jena 6.2.0 / Java 21+。官方下载页与 API 依据在主文档来源索引中。

下载并解压 Apache Jena 二进制发行包后，检查 `lib/` 中存在 `jena-shacl` 等所需模块。以下为 macOS/Linux 的示例操作；路径需要替换为本地实际路径：

```bash
cd jena-guide/examples
export JENA_HOME="/absolute/path/apache-jena-6.2.0"
java -version
java --class-path "$JENA_HOME/lib/*" Demo.java
```

预期由 Java 示例先执行 SHACL 校验，再输出两个 BOM 的聚合结果。若未通过校验，示例直接终止，不把缺失数据当成零成本。

**上述 Java/Jena 命令未在本次环境中执行验证。** 当前环境无法下载 Jena 分发包。不要把独立 RDFLib 检查通过等同于 Jena、SHACL、Fuseki 或 TDB2 的集成测试通过。

## 已完成的独立检查

查看 `verification/validation-report.md` 与 `verification/test-log.txt`。

在已经安装 Python 和 RDFLib 的环境中，可于项目根目录重新执行：

```bash
python verification/verify_examples.py
```

检查涵盖正常查询、状态/版本/日期筛选、币种冲突，以及缺价和多价的反例。该脚本不是完整 SHACL 校验器，也不会冒充 Jena 推理器。

## 反例练习

复制数据文件后再练习：删除新版本单价，观察为什么空查询结果不等于无影响；加入第二个单价，观察连接倍增；把新版本币种改为 USD，观察数据契约冲突；改变有效期，观察左闭右开边界。

这些反例的价值是理解“查询成功”和“业务答案正确”之间的区别。
