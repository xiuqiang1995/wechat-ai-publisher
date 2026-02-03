# 安装指南

本指南将帮助您在不同操作系统上安装和配置 WeChat AI Publisher。

## 📋 系统要求

### 最低要求
- Python 3.9 或更高版本
- Node.js 16 或更高版本
- 4GB 可用内存
- 2GB 可用磁盘空间

### 推荐配置
- Python 3.11+
- Node.js 18+
- 8GB 内存
- SSD 硬盘

### 支持的操作系统
- macOS 10.15+
- Ubuntu 20.04+
- CentOS 8+
- Windows 10+ (WSL2 推荐)

## 🚀 快速安装

### 方法一：使用 pip（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/wechat-ai-publisher.git
cd wechat-ai-publisher

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Node.js 依赖
cd scripts/wechat-markdown-renderer
npm install
cd ../..

# 5. 验证安装
python scripts/wechat_publisher.py --help
```

### 方法二：使用 Docker

```bash
# 1. 克隆项目
git clone https://github.com/your-username/wechat-ai-publisher.git
cd wechat-ai-publisher

# 2. 构建镜像
docker build -t wechat-ai-publisher .

# 3. 运行容器
docker run -it --rm \
  -v $(pwd)/articles:/app/articles \
  -e WECHAT_APPID="your_appid" \
  -e WECHAT_SECRET="your_secret" \
  -e REPLICATE_API_TOKEN="your_token" \
  wechat-ai-publisher
```

## 🔧 详细安装步骤

### 1. 安装 Python

#### macOS
```bash
# 使用 Homebrew
brew install python@3.11

# 或下载官方安装包
# https://www.python.org/downloads/macos/
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

#### CentOS/RHEL
```bash
sudo dnf install python3.11 python3.11-pip
```

#### Windows
1. 下载 Python 安装包：https://www.python.org/downloads/windows/
2. 运行安装程序，确保勾选 "Add Python to PATH"
3. 或使用 WSL2 + Ubuntu

### 2. 安装 Node.js

#### macOS
```bash
# 使用 Homebrew
brew install node

# 或使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

#### Ubuntu/Debian
```bash
# 使用 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 或使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

#### Windows
1. 下载 Node.js 安装包：https://nodejs.org/
2. 运行安装程序
3. 或在 WSL2 中按 Ubuntu 方式安装

### 3. 克隆项目

```bash
git clone https://github.com/your-username/wechat-ai-publisher.git
cd wechat-ai-publisher
```

### 4. 创建虚拟环境

```bash
# Python 虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 5. 安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list
```

### 6. 安装 Node.js 依赖

```bash
# 进入渲染器目录
cd scripts/wechat-markdown-renderer

# 安装依赖
npm install

# 验证安装
npm list

# 返回项目根目录
cd ../..
```

## ⚙️ 环境配置

### 1. 环境变量设置

创建 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env
```

`.env` 文件内容：

```bash
# 微信公众号配置
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret

# Replicate API 配置
REPLICATE_API_TOKEN=your_replicate_token

# 工作目录配置
WORK_DIR=/path/to/your/articles

# 可选：代理设置
# HTTP_PROXY=http://proxy.example.com:8080
# HTTPS_PROXY=http://proxy.example.com:8080
```

### 2. 系统环境变量（推荐）

#### Linux/macOS

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
export WECHAT_APPID="your_wechat_appid"
export WECHAT_SECRET="your_wechat_secret"
export REPLICATE_API_TOKEN="your_replicate_token"
```

然后重新加载：

```bash
source ~/.bashrc  # 或 ~/.zshrc
```

#### Windows

1. 打开"系统属性" → "高级" → "环境变量"
2. 添加用户变量：
   - `WECHAT_APPID`
   - `WECHAT_SECRET`
   - `REPLICATE_API_TOKEN`

### 3. 创建工作目录

```bash
# 创建文章存储目录
mkdir -p ~/Documents/wechat-articles

# 设置权限（Linux/macOS）
chmod 755 ~/Documents/wechat-articles
```

## 🧪 验证安装

### 1. 基本功能测试

```bash
# 检查主脚本
python scripts/wechat_publisher.py --help

# 检查版本信息
python scripts/wechat_publisher.py --version

# 测试环境变量
python -c "import os; print('WECHAT_APPID:', os.getenv('WECHAT_APPID'))"
```

### 2. 依赖检查

```bash
# Python 依赖
pip check

# Node.js 依赖
cd scripts/wechat-markdown-renderer
npm audit
cd ../..
```

### 3. 功能测试

```bash
# 创建测试文章目录
mkdir -p test-article

# 创建测试文章
echo "# 测试文章\n\n这是一篇测试文章。" > test-article/article.md

# 测试文本清理功能
python scripts/wechat_publisher.py sanitize --article-dir test-article

# 清理测试文件
rm -rf test-article
```

## 🔧 故障排除

### 常见问题

#### 1. Python 版本问题

```bash
# 检查 Python 版本
python --version

# 如果版本过低，使用特定版本
python3.11 -m venv venv
```

#### 2. 权限问题（Linux/macOS）

```bash
# 修复权限
chmod +x scripts/wechat_publisher.py

# 或使用 sudo 安装全局包
sudo pip install -r requirements.txt
```

#### 3. 网络问题

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# npm 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

#### 4. 依赖冲突

```bash
# 清理缓存
pip cache purge
npm cache clean --force

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 日志调试

```bash
# 启用详细日志
export PYTHONPATH=.
python scripts/wechat_publisher.py --verbose sanitize --article-dir test-article

# 查看系统信息
python -c "import sys; print(sys.version)"
python -c "import platform; print(platform.platform())"
```

## 📞 获取帮助

如果遇到安装问题：

1. 查看 [FAQ](docs/faq.md)
2. 搜索 [GitHub Issues](https://github.com/your-username/wechat-ai-publisher/issues)
3. 创建新的 Issue 并提供：
   - 操作系统信息
   - Python 和 Node.js 版本
   - 完整的错误信息
   - 安装步骤

---

安装完成后，请查看 [配置指南](configuration.md) 进行进一步设置。