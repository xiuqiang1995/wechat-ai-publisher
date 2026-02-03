# 配置指南

本指南将详细介绍如何配置 WeChat AI Publisher 的各项设置。

## 🔧 基础配置

### 环境变量

WeChat AI Publisher 需要以下环境变量：

```bash
# 必需配置
WECHAT_APPID=your_wechat_appid          # 微信公众号 AppID
WECHAT_SECRET=your_wechat_secret        # 微信公众号 AppSecret
REPLICATE_API_TOKEN=your_replicate_token # Replicate API Token

# 可选配置
WORK_DIR=/path/to/articles              # 工作目录（默认：~/Documents/wechat-articles）
MAX_IMAGES=6                            # 最大配图数量（默认：6）
DEFAULT_STYLE=auto                      # 默认 CSS 样式（默认：auto）
DEFAULT_IMAGE_STYLE=auto                # 默认配图风格（默认：auto）
```

### 配置文件

创建 `config.json` 文件进行详细配置：

```json
{
  "wechat": {
    "appid": "your_wechat_appid",
    "secret": "your_wechat_secret",
    "api_base": "https://api.weixin.qq.com"
  },
  "replicate": {
    "api_token": "your_replicate_token",
    "default_model": "black-forest-labs/flux-dev"
  },
  "paths": {
    "work_dir": "~/Documents/wechat-articles",
    "styles_dir": "./styles",
    "references_dir": "./references"
  },
  "defaults": {
    "css_style": "auto",
    "image_style": "auto",
    "max_images": 6,
    "cover_type": "auto",
    "cover_text": "title-only",
    "cover_mood": "balanced"
  },
  "features": {
    "auto_humanize": true,
    "auto_sanitize": true,
    "skip_existing_images": false
  }
}
```

## 🎨 样式配置

### CSS 样式

支持的 CSS 样式：

#### 1. Purple（商务紫色）
```css
/* 适用于：产品、商业、策略类文章 */
--primary-color: #6366f1;
--secondary-color: #8b5cf6;
--background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

#### 2. OrangeHeart（温暖橙色）
```css
/* 适用于：生活、情感、成长类文章 */
--primary-color: #f97316;
--secondary-color: #fb923c;
--background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
```

#### 3. GitHub（技术风格）
```css
/* 适用于：编程、技术、开发类文章 */
--primary-color: #24292e;
--secondary-color: #586069;
--background: #f6f8fa;
```

#### 4. Doocs 系列
- `doocs-default`：默认微信风格
- `doocs-grace`：优雅简洁风格
- `doocs-simple`：极简风格

### 配图风格

支持的配图风格：

#### 技术类风格
- `blueprint`：蓝图技术风格，适合架构图、流程图
- `scientific`：科学图表风格，适合数据可视化
- `minimal`：极简风格，适合概念图解

#### 商务类风格
- `editorial`：编辑出版风格，适合商业文章
- `notion`：现代简洁风格，适合产品介绍
- `vector-illustration`：矢量插画风格

#### 生活类风格
- `warm`：温暖插画风格，适合生活分享
- `watercolor`：水彩画风格，适合情感文章
- `nature`：自然风光风格，适合健康养生

### 自动匹配规则

系统根据文章内容自动选择样式：

```python
# CSS 样式匹配
github_keywords = ["github", "cli", "api", "python", "javascript", "docker"]
orange_keywords = ["生活", "情绪", "成长", "健康", "幸福"]
purple_keywords = ["产品", "商业", "策略", "增长", "运营"]

# 配图风格匹配
if css_style == "github":
    prefer_styles = ["blueprint", "scientific", "minimal"]
elif css_style == "orangeheart":
    prefer_styles = ["warm", "watercolor", "nature"]
else:  # purple
    prefer_styles = ["editorial", "notion", "minimal"]
```

## 🖼️ 图片生成配置

### Replicate 模型配置

支持的图片生成模型：

```json
{
  "models": {
    "flux-dev": {
      "name": "black-forest-labs/flux-dev",
      "description": "高质量图片生成，适合封面和配图",
      "max_resolution": "1024x1024",
      "cost_per_image": 0.055
    },
    "stable-diffusion": {
      "name": "stability-ai/stable-diffusion",
      "description": "经典稳定扩散模型",
      "max_resolution": "768x768",
      "cost_per_image": 0.02
    }
  },
  "default_model": "flux-dev",
  "generation_params": {
    "guidance_scale": 7.5,
    "num_inference_steps": 50,
    "seed": -1
  }
}
```

### 封面配置

封面生成参数：

```json
{
  "cover": {
    "types": ["hero", "minimal", "editorial", "technical"],
    "text_options": ["title-only", "title-subtitle", "none"],
    "mood_levels": ["calm", "balanced", "energetic"],
    "dimensions": {
      "width": 1242,
      "height": 1656
    }
  }
}
```

### 配图配置

正文配图参数：

```json
{
  "illustrations": {
    "max_count": 6,
    "min_spacing": 2,
    "placement_rules": {
      "after_heading": true,
      "before_code": false,
      "in_long_paragraphs": true
    },
    "dimensions": {
      "width": 1200,
      "height": 800
    }
  }
}
```

## 📱 微信公众号配置

### 获取 AppID 和 AppSecret

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 进入"开发" → "基本配置"
3. 获取 AppID 和 AppSecret

### API 权限配置

需要开通以下接口权限：
- 素材管理接口
- 草稿箱管理接口
- 图片上传接口

### 服务器配置

如果需要接收微信回调：

```json
{
  "server": {
    "url": "https://your-domain.com/wechat/callback",
    "token": "your_token",
    "encoding_aes_key": "your_aes_key"
  }
}
```

## 🔍 高级配置

### 缓存配置

```json
{
  "cache": {
    "enabled": true,
    "ttl": 3600,
    "max_size": "100MB",
    "storage": "file"
  }
}
```

### 日志配置

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/wechat-publisher.log",
    "max_size": "10MB",
    "backup_count": 5
  }
}
```

### 代理配置

```json
{
  "proxy": {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080",
    "no_proxy": "localhost,127.0.0.1"
  }
}
```

### 重试配置

```json
{
  "retry": {
    "max_attempts": 3,
    "backoff_factor": 2,
    "timeout": 30
  }
}
```

## 🛠️ 自定义配置

### 添加新的 CSS 样式

1. 在 `styles/` 目录创建新的 CSS 文件
2. 定义样式变量和规则
3. 在配置中添加样式名称

```css
/* styles/custom.css */
:root {
  --primary-color: #your-color;
  --secondary-color: #your-secondary;
  --font-family: 'Your Font', sans-serif;
}

.article-container {
  /* 自定义样式 */
}
```

### 添加新的配图风格

1. 在 `references/styles/` 目录创建 Markdown 文件
2. 定义风格描述和示例

```markdown
<!-- references/styles/custom.md -->
# Custom Style

## Description
Your custom illustration style description.

## Visual Elements
- Color palette: warm tones
- Style: minimalist
- Composition: centered

## Example Prompts
- "minimalist illustration of [concept]"
- "warm color palette, simple shapes"
```

### 自定义工作流

创建自定义脚本扩展工作流：

```python
# scripts/custom_workflow.py
from wechat_publisher import WeChatPublisher

class CustomWorkflow(WeChatPublisher):
    def custom_step(self, article_dir):
        # 自定义处理逻辑
        pass

    def run_custom_workflow(self, article_dir):
        self.write_article(article_dir)
        self.custom_step(article_dir)
        self.build(article_dir)
        self.publish(article_dir)
```

## 📊 性能优化配置

### 并发配置

```json
{
  "concurrency": {
    "max_workers": 4,
    "image_generation": 2,
    "api_requests": 3
  }
}
```

### 内存配置

```json
{
  "memory": {
    "max_image_size": "10MB",
    "cache_size": "100MB",
    "gc_threshold": 0.8
  }
}
```

## 🔒 安全配置

### API 密钥管理

```bash
# 使用环境变量（推荐）
export WECHAT_SECRET="$(cat /secure/path/wechat_secret)"
export REPLICATE_API_TOKEN="$(cat /secure/path/replicate_token)"

# 使用密钥管理服务
export WECHAT_SECRET="$(aws secretsmanager get-secret-value --secret-id wechat-secret --query SecretString --output text)"
```

### 访问控制

```json
{
  "security": {
    "allowed_ips": ["192.168.1.0/24"],
    "rate_limit": {
      "requests_per_minute": 60,
      "burst": 10
    },
    "encryption": {
      "enabled": true,
      "algorithm": "AES-256-GCM"
    }
  }
}
```

## 📝 配置验证

使用内置命令验证配置：

```bash
# 验证基础配置
python scripts/wechat_publisher.py config --validate

# 测试 API 连接
python scripts/wechat_publisher.py config --test-apis

# 检查样式文件
python scripts/wechat_publisher.py config --check-styles
```

---

配置完成后，请查看 [工作流程指南](workflow.md) 了解如何使用系统。