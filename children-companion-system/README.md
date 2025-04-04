# 智能儿童陪伴交互软件系统

这是一个综合性的儿童教育娱乐平台，旨在为儿童提供丰富的学习、娱乐和习惯养成功能。系统采用了多模态交互方式，包括语音识别、手势识别和表情分析，使儿童能够通过自然的方式与系统进行交互。

## 项目结构

```
children-companion-system/
├── src/                    # 源代码目录
│   ├── core/               # 核心组件
│   ├── ui/                 # 用户界面
│   ├── speech/             # 语音交互模块
│   ├── emotion/            # 情感识别模块
│   ├── database/           # 数据库模块
│   └── utils/              # 工具函数
├── docs/                   # 文档目录
├── config/                 # 配置文件
├── models/                 # 模型文件
├── icons/                  # 图标资源
└── tests/                  # 测试代码
```

## 主要功能

- **多模态交互**：支持语音识别、手势识别和表情分析
- **内容资源**：包含故事、儿歌、游戏和教育内容
- **习惯养成**：帮助儿童培养良好的生活和学习习惯
- **家长控制**：提供家长监管和设置功能
- **个性化推荐**：根据儿童兴趣和学习进度提供个性化内容

## 安装指南

详细的安装步骤请参考 [安装指南](docs/installation-guide.md)。

### 快速开始

1. 确保已安装Python 3.8或更高版本
2. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```bash
   python main.py
   ```

## 文档索引

- [项目总结](docs/project-summary.md)
- [安装指南](docs/installation-guide.md)
- [语音集成指南](docs/speech-integration.md)
- [内容管理系统](docs/content-management.md)
- [需求完成度检查](docs/project-requirements-check.md)
- [系统架构](docs/system-architecture.mermaid)

## 技术栈

- **前端**：PyQt5
- **后端**：Python
- **数据库**：SQLite
- **AI技术**：TensorFlow, OpenCV, 百度语音API

## 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

- 电子邮件：support@children-companion.com
- 官方网站：www.children-companion.com
- 技术支持热线：400-123-4567
