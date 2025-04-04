# 智能儿童陪伴交互软件系统 - 安装与使用指南

## 环境要求

### 硬件要求

- 处理器：至少Intel Core i3或同等性能处理器
- 内存：至少4GB RAM
- 存储空间：至少1GB可用空间
- 摄像头：支持视频采集的摄像头（用于手势和表情识别）
- 麦克风：支持音频输入的麦克风（用于语音识别）
- 扬声器：音频输出设备

### 软件要求

- 操作系统：Windows 10/11、macOS 10.14以上、Ubuntu 18.04以上
- Python 3.8或更高版本
- 网络连接（用于内容更新）

## 安装步骤

### 1. 安装Python环境

如果您的系统尚未安装Python，请按照以下步骤安装：

#### Windows：

1. 访问Python官网 https://www.python.org/downloads/ 下载最新版Python
2. 运行安装程序，勾选"Add Python to PATH"选项
3. 完成安装过程

#### macOS：

```bash
# 安装Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python
brew install python
```

#### Linux (Ubuntu/Debian)：

```bash
sudo apt update
sudo apt install python3 python3-pip python3-dev
```

### 2. 安装必要的Python库

打开命令行或终端，执行以下命令安装所需的库：

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv
# 在Windows上激活虚拟环境
venv\Scripts\activate
# 在macOS/Linux上激活虚拟环境
source venv/bin/activate

# 安装依赖库
pip install PyQt5 numpy tensorflow scipy opencv-python SpeechRecognition pyttsx3 pyaudio
```

### 3. 下载智能儿童陪伴系统

```bash
# 克隆项目仓库
git clone https://github.com/your-organization/children-companion-system.git
cd children-companion-system
```

或者从官方网站下载压缩包并解压。

### 4. 初始化数据库

```bash
# 运行数据库初始化脚本
python initialize_database.py
```

### 5. 启动系统

```bash
# 启动主程序
python main.py
```

## 使用指南

### 首次使用

1. 首次启动系统时，您需要注册家长账户
   - 点击登录界面的"注册"按钮
   - 填写用户名、密码并选择"家长"类型
   - 完成注册并登录

2. 创建儿童账户
   - 登录家长账户后，进入设置标签页
   - 点击"添加儿童账户"
   - 填写儿童信息并设置账户

### 家长控制中心

登录家长账户后，您可以在控制中心进行以下操作：

1. **使用统计**：查看儿童的使用时长和内容偏好
2. **时间控制**：设置每日使用时间限制和禁用时段
3. **内容过滤**：设置可访问的内容类型和关键词过滤
4. **学习进度**：查看各学习领域的进度和完成情况
5. **习惯养成**：添加和管理习惯养成计划
6. **基本设置**：更新儿童信息和通知设置

### 儿童使用界面

儿童登录后可以使用以下功能：

1. **故事**：听各类童话故事、寓言故事等
2. **儿歌**：欣赏和学唱儿歌
3. **游戏**：体验各种益智游戏
4. **学习**：参与学习活动，提升各方面能力
5. **习惯养成**：完成每日习惯任务并获得奖励

### 语音交互

系统支持语音命令，儿童可以使用如下语音指令：

- "我想听故事"
- "播放儿歌"
- "我要玩游戏"
- "学习算术"
- "完成刷牙任务"

### 手势交互

系统支持以下手势操作：

- **挥手**：唤醒系统或打招呼
- **点头**：确认操作
- **摇头**：取消操作
- **指点**：选择项目

## 常见问题解答

### 1. 系统无法识别语音

**解决方案**：
- 确保麦克风已正确连接并授权应用使用
- 检查麦克风音量是否适当
- 尝试在安静的环境中使用
- 重新启动应用程序

### 2. 手势识别不准确

**解决方案**：
- 确保摄像头清洁且位置合适
- 保持光线充足，避免背光
- 尝试在简单背景下使用
- 更新至最新版本系统

### 3. 内容加载缓慢

**解决方案**：
- 检查网络连接状态
- 确保存储空间充足
- 关闭其他占用资源的应用
- 重启应用或设备

### 4. 家长控制设置未生效

**解决方案**：
- 确保设置后点击了"保存"按钮
- 重新登录儿童账号
- 检查是否有设置冲突
- 更新至最新版本系统

## 系统更新

系统会定期推出更新，包括新内容、功能改进和安全更新。您可以通过以下方式更新：

```bash
# 进入项目目录
cd children-companion-system

# 拉取最新代码（如果是通过git安装）
git pull

# 或下载并安装最新版本

# 更新依赖库
pip install -r requirements.txt --upgrade

# 更新数据库（如需要）
python update_database.py
```

## 联系与支持

如果您在使用过程中遇到任何问题，或有功能建议，请通过以下方式联系我们：

- 电子邮件：support@children-companion.com
- 官方网站：www.children-companion.com
- 技术支持热线：400-123-4567

我们的技术支持团队将在工作日24小时内回复您的问题。

---

感谢您选择智能儿童陪伴交互软件系统，我们致力于为儿童提供安全、有趣、富有教育意义的数字体验！
