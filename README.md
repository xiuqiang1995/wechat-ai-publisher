# WeChat AI Publisher

一个完整的微信公众号自动化发布工具链，支持从文章写作、配图生成到草稿箱发布的全流程自动化。

## 🚀 功能特性

- **📝 智能写作**：基于主题和素材自动生成公众号文章
- **🎨 自动配图**：智能分析文章内容，自动规划和生成配图
- **🖼️ 多样式支持**：支持多种 CSS 样式和配图风格
- **📱 一键发布**：自动渲染 HTML 并发布到微信公众号草稿箱
- **🔄 完整工作流**：写作 → 人性化改写 → 配图规划 → 生图 → 回填 → 渲染 → 发布

## 📋 系统要求

- Python 3.9+
- Node.js 16+
- macOS/Linux（推荐）
- 微信公众号开发者账号
- Replicate API Token（用于图片生成）

## 🛠️ 安装配置

### 1. 克隆项目

```bash
git clone https://github.com/your-username/wechat-ai-publisher.git
cd wechat-ai-publisher
```

### 2. 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖（用于 Markdown 渲染）
cd scripts/wechat-markdown-renderer
npm install
cd ../..
```

### 3. 环境变量配置

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
export WECHAT_APPID="your_wechat_appid"
export WECHAT_SECRET="your_wechat_secret"
export REPLICATE_API_TOKEN="your_replicate_token"
```

### 4. 创建工作目录

```bash
mkdir -p ~/Documents/wechat-articles
```

## 🎯 快速开始

### 基本使用

```bash
# 1. 写文章（交互式）
python scripts/wechat_publisher.py write --topic "你的文章主题"

# 2. 完整发布流程（推荐）
python scripts/wechat_publisher.py ship \
  --article-dir "~/Documents/wechat-articles/2024-01-01_your-article" \
  --style auto \
  --image-style auto \
  --max-images 6
```

### 分步执行

```bash
# 1. 仅构建（生成图片和 HTML）
python scripts/wechat_publisher.py build \
  --article-dir "path/to/article" \
  --style purple \
  --image-style notion

# 2. 仅发布到草稿箱
python scripts/wechat_publisher.py publish \
  --article-dir "path/to/article"

# 3. 文本清理
python scripts/wechat_publisher.py sanitize \
  --article-dir "path/to/article"
```

## 📁 项目结构

```
wechat-ai-publisher/
├── README.md                          # 项目说明
├── requirements.txt                   # Python 依赖
├── LICENSE                           # 开源许可证
├── .gitignore                        # Git 忽略文件
├── scripts/                          # 核心脚本
│   ├── wechat_publisher.py           # 主编排脚本
│   ├── wechat-article-writer/        # 文章写作模块
│   ├── wechat-article-illustration-planner/  # 配图规划
│   ├── wechat-article-image-generator/       # 图片生成
│   ├── wechat-article-embedder/      # 图片嵌入
│   ├── wechat-markdown-renderer/     # HTML 渲染
│   └── wechat-draft-publisher/       # 草稿箱发布
├── styles/                           # CSS 样式文件
│   ├── purple.css                    # 紫色商务风格
│   ├── orangeheart.css              # 橙色温暖风格
│   ├── github.css                   # GitHub 技术风格
│   └── doocs-*.css                  # doocs/md 主题
├── references/                       # 配图风格参考
│   └── styles/
│       ├── notion.md                # Notion 风格
│       ├── blueprint.md             # 蓝图风格
│       ├── editorial.md             # 编辑风格
│       └── ...                      # 更多风格
├── examples/                         # 示例文章
│   └── sample-article/
│       ├── article.md               # 示例文章
│       ├── cover.png               # 封面图
│       └── img1.png                # 配图
└── docs/                            # 详细文档
    ├── installation.md              # 安装指南
    ├── configuration.md             # 配置说明
    ├── workflow.md                  # 工作流程
    └── api.md                       # API 文档
```

## 🔧 配置说明

### CSS 样式选择

- `purple`：商务紫色风格，适合产品、商业类文章
- `orangeheart`：温暖橙色风格，适合生活、情感类文章
- `github`：技术风格，适合编程、技术类文章
- `doocs-*`：仿微信编辑器风格

### 配图风格选择

- `notion`：简洁现代风格
- `blueprint`：蓝图技术风格
- `editorial`：编辑出版风格
- `warm`：温暖插画风格
- `scientific`：科学图表风格

### 自动匹配规则

系统会根据文章内容自动选择合适的样式：

- 包含技术关键词 → `github` + `blueprint`
- 包含生活情感词汇 → `orangeheart` + `warm`
- 包含商业产品词汇 → `purple` + `editorial`

## 📖 使用指南

### 1. 文章目录结构

每篇文章使用独立目录，建议命名：`YYYY-MM-DD_slug/`

```
2024-01-01_my-article/
├── article.md                    # 最终文章（带图）
├── prompts/                      # 图片生成提示词
│   ├── cover.md                 # 封面提示词
│   ├── img1.md                  # 配图1提示词
│   └── img2.md                  # 配图2提示词
├── cover.png                     # 封面图片
├── img1.png                      # 配图1
├── img2.png                      # 配图2
├── article.html                  # 发布用HTML
├── publish.json                  # 发布结果
└── .wechat-ai-publisher/         # 中间文件
    ├── article.plan.md          # 配图规划
    ├── build.json               # 构建信息
    └── style.json               # 样式选择记录
```

### 2. 工作流程

1. **写作阶段**：生成纯文本 Markdown
2. **人性化改写**：去除 AI 写作痕迹
3. **文本清理**：移除格式符号
4. **用户确认**：检查文章内容
5. **配图规划**：自动分析并规划配图位置
6. **图片生成**：批量生成封面和配图
7. **图片嵌入**：将图片插入文章
8. **HTML 渲染**：生成发布用 HTML
9. **草稿箱发布**：上传到微信公众号

### 3. 命令行选项

```bash
# 主要命令
python scripts/wechat_publisher.py [command] [options]

# 命令列表
write       # 写文章
sanitize    # 文本清理
build       # 构建（配图+渲染）
publish     # 发布到草稿箱
ship        # 完整流程（build + publish）

# 常用选项
--article-dir PATH        # 文章目录
--style STYLE            # CSS样式 (auto/purple/orangeheart/github)
--image-style STYLE      # 配图风格 (auto/notion/blueprint/editorial)
--max-images N           # 最大配图数量 (1-6)
--skip-existing-images   # 跳过已存在的图片
--cover-type TYPE        # 封面类型
--cover-text TEXT        # 封面文字设置
--cover-mood MOOD        # 封面情绪强度
```

## 🔌 API 集成

### 微信公众号 API

需要在微信公众平台申请开发者权限，获取：
- AppID
- AppSecret

### Replicate API

用于 AI 图片生成，支持多种模型：
- FLUX.1 [dev]
- Stable Diffusion
- 其他图像生成模型

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Claude Code](https://claude.ai/code) - AI 编程助手
- [Replicate](https://replicate.com) - AI 模型 API 平台
- [微信公众平台](https://mp.weixin.qq.com) - 内容发布平台

## 📞 支持

- 提交 Issue：[GitHub Issues](https://github.com/your-username/wechat-ai-publisher/issues)
- 讨论交流：[GitHub Discussions](https://github.com/your-username/wechat-ai-publisher/discussions)

## 🔄 更新日志

### v1.0.0 (2024-02-03)
- 🎉 首次发布
- ✨ 完整的文章写作到发布工作流
- 🎨 多样式 CSS 和配图风格支持
- 🤖 智能样式自动匹配
- 📱 微信公众号草稿箱集成

---

**让 AI 帮你轻松创作和发布优质公众号内容！** 🚀