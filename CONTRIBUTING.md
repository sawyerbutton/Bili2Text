# 贡献指南

感谢您对Bili2Text项目的关注和支持！本文档将指导您如何为项目做出贡献。

## 🎯 贡献方式

### 🐛 报告Bug
- 在[Issues页面](../../issues)创建新的Bug报告
- 使用Bug报告模板，提供详细的复现步骤
- 包含系统环境、错误日志等关键信息

### 💡 功能建议
- 在[Issues页面](../../issues)创建功能请求
- 清楚描述新功能的用途和预期效果
- 讨论实现方案和可能的影响

### 🔧 代码贡献
- Fork项目到您的账号下
- 创建功能分支进行开发
- 提交Pull Request

## 🛠️ 开发环境搭建

### 1. 克隆项目
```bash
git clone https://github.com/your-username/Bili2Text.git
cd Bili2Text
```

### 2. 创建开发环境
```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements/dev.txt
```

### 3. 配置开发环境
```bash
# 复制配置文件
cp config/app/default.env config/app/development.env

# 安装pre-commit钩子
pre-commit install

# 运行测试确保环境正常
pytest tests/
```

## 📝 代码规范

### Python代码风格
- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)代码风格
- 使用[Black](https://black.readthedocs.io/)进行代码格式化
- 使用[isort](https://pycqa.github.io/isort/)整理import语句
- 使用类型提示提高代码可读性

### 代码格式化
```bash
# 格式化代码
black src/ cli/ webapp/ tests/
isort src/ cli/ webapp/ tests/

# 检查代码风格
flake8 src/ cli/ webapp/
mypy src/ cli/ webapp/
```

### 提交信息规范
使用[约定式提交](https://www.conventionalcommits.org/zh-hans/)格式：

```
type(scope): description

[optional body]

[optional footer]
```

**类型说明**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例**：
```bash
feat(cli): add batch processing command
fix(webapp): resolve websocket connection timeout
docs(readme): update installation instructions
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_transcriber.py

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

### 编写测试
- 为新功能编写相应的测试用例
- 确保测试覆盖率不低于80%
- 使用有意义的测试名称和断言

### 测试目录结构
```
tests/
├── unit/           # 单元测试
│   ├── test_config.py
│   ├── test_transcriber.py
│   └── test_downloader.py
├── integration/    # 集成测试
│   ├── test_cli.py
│   └── test_api.py
└── fixtures/       # 测试数据
    ├── sample_audio.wav
    └── test_config.json
```

## 🔀 Pull Request流程

### 1. 创建分支
```bash
# 从main分支创建新的功能分支
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. 开发和测试
```bash
# 进行开发
# ...

# 运行测试
pytest

# 格式化代码
black .
isort .

# 提交更改
git add .
git commit -m "feat(scope): your feature description"
```

### 3. 提交Pull Request
- 推送分支到您的Fork仓库
- 在GitHub上创建Pull Request
- 填写PR模板，描述更改内容
- 确保所有检查通过

### PR检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 测试全部通过
- [ ] 更新了相关文档
- [ ] 提交信息符合规范

## 📚 文档贡献

### 文档类型
- **API文档**: 描述接口用法和参数
- **用户文档**: 使用指南和教程
- **开发文档**: 技术实现和架构说明

### 文档规范
- 使用Markdown格式
- 保持简洁清晰的语言
- 提供代码示例和截图
- 及时更新过时内容

## 🎯 特殊贡献领域

### 🌍 国际化
- 翻译界面文本
- 本地化配置和文档
- 多语言测试

### 🎨 UI/UX改进
- 界面设计优化
- 用户体验改进
- 响应式设计

### 📦 包管理和部署
- Docker配置优化
- CI/CD流程改进
- 包发布和分发

### 🔧 性能优化
- 算法优化
- 内存使用优化
- 并发处理改进

## 🏆 贡献者认可

### 贡献者列表
项目感谢所有贡献者的努力，我们会在以下地方认可您的贡献：
- README.md贡献者部分
- 发布说明中的致谢
- GitHub贡献者图表

### 特殊贡献
对于重大贡献，我们会：
- 在项目文档中特别鸣谢
- 邀请加入项目维护团队
- 提供项目推荐信

## 📞 获取帮助

如果您在贡献过程中遇到任何问题，可以通过以下方式获取帮助：

- 📋 [GitHub Issues](../../issues) - 技术问题和Bug报告
- 💬 [GitHub Discussions](../../discussions) - 社区讨论和Q&A
- 📧 邮件联系 - your-email@example.com

## 📄 许可证

通过向本项目贡献代码，您同意您的贡献将根据项目的[MIT许可证](LICENSE)进行许可。

---

再次感谢您的贡献！您的努力让Bili2Text变得更好！ 🙏 