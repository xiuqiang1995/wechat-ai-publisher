# 贡献指南

感谢您对 WeChat AI Publisher 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 检查 [Issues](https://github.com/your-username/wechat-ai-publisher/issues) 确认问题未被报告
2. 创建新的 Issue，包含：
   - 清晰的问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）

### 提交代码

1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/wechat-ai-publisher.git
   cd wechat-ai-publisher
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **开发环境设置**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 编写测试用例

5. **测试**
   ```bash
   python -m pytest tests/
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   # 或
   git commit -m "fix: fix your bug description"
   ```

7. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 代码规范

### Python 代码风格

- 使用 PEP 8 标准
- 函数和变量使用 snake_case
- 类名使用 PascalCase
- 常量使用 UPPER_CASE
- 每行最大长度 88 字符

### 提交信息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 文档

- 所有公共函数需要 docstring
- 重要功能需要添加使用示例
- 更新相关的 README 和文档

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_publisher.py

# 运行测试并显示覆盖率
python -m pytest --cov=scripts
```

### 编写测试

- 为新功能编写单元测试
- 测试文件命名：`test_*.py`
- 测试函数命名：`test_*`
- 使用 pytest fixtures 管理测试数据

## 🔍 代码审查

所有 PR 都需要经过代码审查：

1. **自动检查**
   - 代码风格检查（flake8）
   - 测试通过
   - 文档构建成功

2. **人工审查**
   - 代码逻辑正确性
   - 性能影响
   - 安全性考虑
   - 文档完整性

## 🏷️ 发布流程

项目使用语义化版本控制：

- `MAJOR.MINOR.PATCH`
- MAJOR：不兼容的 API 修改
- MINOR：向下兼容的功能性新增
- PATCH：向下兼容的问题修正

## 📞 联系方式

- GitHub Issues：技术问题和 bug 报告
- GitHub Discussions：功能讨论和使用交流
- Email：项目维护者邮箱

## 🙏 致谢

感谢所有贡献者的努力！您的贡献让这个项目变得更好。

---

再次感谢您的贡献！🎉