# 学习资料助手

基于 Python、FastAPI 和 SQLite 的学习项目。从任务管理接口逐步扩展为资料助手，支持上传 TXT/PDF、提取文字、保存资料，以及调用 AI 生成摘要和知识点。

当前主要通过 FastAPI 自带的 Swagger 文档页面操作，尚未实现独立前端。

## 已实现功能

- 任务新增、查询、修改、删除及完成状态筛选。
- 上传 UTF-8 编码的 TXT 文件，读取文字并统计字符数。
- 按页提取 PDF 文字；没有可提取文字的页面会尝试 OCR 识别。
- 保存上传的原始文件，以及文件名、页数和各页文字。
- 根据资料 ID 查询已保存的资料。
- 根据资料生成最多三条摘要或五条知识点，并要求 AI 标注来源页码。
- 提供普通 AI 对话接口，以及 pytest 自动化接口测试。

## 本地启动（Windows / PowerShell）

以下命令都在仓库的 `projects/study-assistant` 目录中运行。可以在 Cursor 或 VS Code 打开该文件夹，再打开终端。这个项目由原来的 `week2/fastapi-week2` 持续扩展而来，历史版本见[仓库首页](../../README.md)。

### 1. 安装依赖

首次使用时创建虚拟环境，已经存在 `.venv` 时跳过第一条命令：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -r requirements-ai.txt
```

`requirements-dev.txt` 会同时安装基础运行依赖和测试依赖；`requirements-ai.txt` 提供 AI 请求及本地配置读取依赖。

### 2. 配置 AI 服务

在项目根目录复制配置示例，然后编辑 `.env`，填写自己的服务配置。如果已有可用配置，保留原内容，跳过复制命令。

```powershell
Copy-Item .env.example .env
```

```dotenv
AI_BASE_URL=https://your-provider.example/v1
AI_API_KEY=your-api-key
AI_MODEL=your-model-name
```

上面都是占位值，需要替换。当前客户端会在 `AI_BASE_URL` 后追加 `/responses`，因此服务商必须支持这一接口以及对应的请求、返回格式。模型名称以服务商实际支持的名称为准。

`.env` 中包含密钥，不要上传到 GitHub。项目已将它加入 `.gitignore`。修改配置后重启后端，使配置重新加载。

### 3. 启动后端

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

保持终端运行，打开 [接口文档](http://127.0.0.1:8000/docs)。在启动后端的终端按 `Ctrl + C` 可以停止服务。

数据库路径固定为项目根目录的 `tasks.db`，应用加载时自动创建缺失的表。上传文件夹在保存文件时自动创建。

## 完整使用流程

1. 打开 `POST /document/upload`，点击 **Try it out**，选择 TXT 或 PDF，再点击 **Execute**。
2. 记录上传返回的 `id`，这是资料在数据库中的编号。
3. 在 `GET /documents/{document_id}` 填入该编号，核对文件名、页数和文字。
4. 在 `POST /documents/{document_id}/summary` 填入同一个编号，生成摘要。
5. 在 `POST /documents/{document_id}/key-points` 填入同一个编号，提取知识点。
6. 对照原文检查生成内容和页码。返回成功不代表 AI 内容一定正确。

查询、摘要和知识点接口都使用已保存的资料，不需要再次上传。上传地址中的 `document` 是单数，其他资料接口中的 `documents` 是复数。

仓库附带的示例文件（测试也会使用）：

- `output/pdf/day4-course-notes.pdf`：两页带文字的 PDF。
- `output/pdf/day4-scanned-notes.pdf`：用于尝试 OCR 的扫描版 PDF。

## 主要接口

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/health` | 检查后端是否运行 |
| POST | `/chat` | 向 AI 提问，请求 JSON 示例：`{"message": "你好"}` |
| POST | `/document/upload` | 上传资料，文件字段名为 `file` |
| GET | `/documents/{document_id}` | 查询资料 |
| POST | `/documents/{document_id}/summary` | 生成摘要，结果字段为 `summary` |
| POST | `/documents/{document_id}/key-points` | 提取知识点，结果字段为 `key_points` |
| GET / POST | `/tasks` | 查询任务列表 / 新增任务 |
| GET / PUT / DELETE | `/tasks/{task_id}` | 查询 / 修改 / 删除指定任务 |

常见状态码：`200` 表示请求成功；`400` 可能表示文件类型、编码或内容不符合要求；`404` 表示资料或任务不存在；`422` 可能表示请求参数不合法，或资料没有可供 AI 处理的文字；`500` 可能表示资料保存失败；`502` 可能表示 AI 请求或返回内容处理失败。具体原因查看响应中的 `detail`。

## 数据保存在哪里

| 位置 | 保存内容 |
| --- | --- |
| `uploads/` | 原始上传文件，使用生成的唯一文件名保存 |
| `tasks.db` | SQLite 数据库，包含任务表和资料表 |
| 资料表的 `pages` 字段 | 各页的 `page_number`、`text` 和 `char_count` |
| `app.log` | 应用日志 |

资料 ID 对应数据库中的一条资料记录。生成摘要时，接口按 ID 找到记录，再把 `document.pages` 中的文字交给 AI 处理。

原始文件、数据库、日志、密钥和虚拟环境不随 Git 提交。新检出的项目不会自动包含本机已上传的资料。

## 自动化测试

需要验证代码时，在项目根目录执行：

```powershell
New-Item -ItemType Directory -Path .\tmp -Force | Out-Null
$testTempDir = ".\tmp\pytest-" + [guid]::NewGuid().ToString("N")
.\.venv\Scripts\python.exe -m pytest -q --basetemp="$testTempDir"
```

每次使用独立的临时目录，减少 Windows 上重复使用临时目录时的权限冲突。测试使用内存 SQLite 数据库和临时上传目录，测试接口操作不会写入日常使用的资料库和上传目录。

摘要和知识点接口测试通过 `monkeypatch` 替换生成函数，提供固定回答或模拟异常。这些测试验证接口的数据传递和错误处理，不评价真实 AI 的回答质量，也不需要真实调用 AI。

最近一次验证结果（2026-09-21）：`26 passed`，另有一条依赖库弃用提醒。测试尚未覆盖所有边界情况，例如数据库提交失败后的回滚。

## 主要代码文件

| 文件 | 职责 |
| --- | --- |
| `app.py` | 接口地址、参数校验、数据库查询和响应 |
| `models.py` | 任务和资料的数据库表结构 |
| `database.py` | SQLite 连接和数据库会话 |
| `config.py` | 数据库、上传文件夹和日志等路径 |
| `document_storage.py` | 保存原始文件及资料记录 |
| `read_pdf.py` | PDF 逐页提取文字和 OCR 回退 |
| `ocr_service.py` | 从图片识别文字 |
| `document_ai.py` | 拼接各页文字，编写摘要和知识点提示词 |
| `ai_client.py` | 读取 `.env`，请求 AI 服务并提取回答 |
| `ask_ai.py` | 第三周第一天的独立命令行练习；接口统一使用 `ai_client.py` |
| `ocr_demo.py` | 独立 OCR 演示；接口使用 `read_pdf.py` 和 `ocr_service.py` |
| `tests/test_app.py` | 接口测试 |
| `tests/conftest.py` | 隔离测试数据库和上传目录 |
| `storage.py` | 早期 JSON 存储练习，当前接口已使用 SQLite |
| `migrate.py` | 将旧 `tasks.json` 导入 SQLite 的一次性脚本；已有相同 ID 时不要重复导入 |

## 当前限制

- 上传支持 TXT 和 PDF，尚不支持直接上传 PPT/PPTX。
- OCR 可能识别错字；仅在整页没有可提取文字时启用，含有文字和图片的混合页面不会自动对其中图片补做识别。
- 摘要和知识点尚未保存到数据库，每次请求都会重新生成。
- AI 标注的页码没有经过程序自动核验，内容仍需对照原文检查。
- 当前将资料文字整体发送给 AI，没有实现长文分块、检索增强或上下文长度管理。
- AI 最大输出量当前设为 256 tokens，较长回答可能被截断；短资料的摘要和知识点也可能比较接近。
- 当前是本地学习原型，尚未实现用户登录、用户之间的资料隔离和生产部署。
