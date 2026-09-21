# AI Practice Plan

面向 AI 应用开发的学习实践仓库。当前主项目是一个基于 FastAPI 和 SQLite 的学习资料助手。

## 当前项目

[学习资料助手：功能、配置与运行说明](projects/study-assistant/README.md)

支持 TXT/PDF 上传、PDF 文字提取与 OCR、资料保存和查询，以及 AI 摘要和知识点生成；同时保留早期实现的任务管理接口。

这是本地学习原型，目前通过 Swagger 页面操作。尚未实现独立前端、用户登录、资料问答或生产部署。

## 仓库结构

```text
ai_practice_plan/
  README.md                    # 学习进度和项目入口
  projects/
    study-assistant/           # 唯一的当前项目代码
      README.md                # 安装、配置、接口和限制
      .env.example             # AI 配置占位示例，不含密钥
      app.py                   # FastAPI 接口
      tests/                   # 自动化测试
      output/pdf/              # 测试使用的两份示例 PDF
```

## 学习进度

| 阶段 | 已完成内容 |
| --- | --- |
| 第二周 | FastAPI 任务 CRUD、参数校验、SQLite、日志和隔离数据库的接口测试 |
| 第三周 | AI API 调用、TXT/PDF 上传、OCR、资料存取、摘要、知识点及完整流程验收 |
| 下一阶段（未实现） | 文字分块、资料检索和根据资料回答问题 |

第三周是在第二周项目上继续开发，因此当前代码统一放在 `projects/study-assistant`，不按周复制整套代码。原来的 `week2/fastapi-week2` 已迁入此目录。

[查看第二周结束时的完整版本](https://github.com/ZZZboyyu/ai_practice_plan/tree/6c8798f86d302e9f8b18b405b59a7029c6ea6a13/week2/fastapi-week2)。后续修改也可以通过 Git 提交记录查看。

## 从哪里开始

克隆仓库后进入项目目录，再按项目 README 完成安装和配置：

```powershell
git clone https://github.com/ZZZboyyu/ai_practice_plan.git
cd ai_practice_plan\projects\study-assistant
```

不要提交 `.env`、个人上传资料、数据库、运行日志或虚拟环境。仓库包含的 PDF 是接口测试所需的示例，不是个人资料库。
