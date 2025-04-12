# PDF 安全管理系统 v1.0
[English](README.md) | [中文](README.zh-CN.md)

[![Python 版本](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![许可证](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![文档](https://img.shields.io/badge/docs-available-brightgreen)](https://github.com/yourusername/PDF-Security-Manager/wiki)

一款专业的 PDF 安全管理系统，提供全面的文档保护和权限控制功能。基于 PyQt5 和 PyPDF2 开发，提供直观的图形界面，让 PDF 文档安全管理变得简单高效。

## 🌟 核心特性

- **高级安全控制**
  - 可自定义加密口令
  - 采用 SHA-256 哈希算法保护口令安全
  - 128 位加密强度
  - 基于权限的访问控制

- **灵活的备份选项**
  - 自动创建备份文件
  - 自定义备份目录
  - 备份文件命名规范

- **智能文件管理**
  - 支持拖放操作
  - 批量处理能力
  - 自定义文件后缀
  - 原文件保护选项

- **专业日志系统**
  - 详细的操作日志
  - 错误追踪和报告
  - 日志文件管理

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- PyQt5
- PyPDF2

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/PDF-Security-Manager.git
cd PDF-Security-Manager
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

### 使用方法

1. 启动程序：
```bash
python pdf_encryptor.py
```

2. 基本操作：
   - 将 PDF 文件拖放到程序窗口
   - 配置安全设置
   - 设置自定义加密口令
   - 选择备份选项
   - 处理文件

## 🔒 安全特性

- **口令保护**
  - 使用 SHA-256 哈希算法安全存储口令
  - 可自定义所有者口令
  - 不存储明文口令

- **权限管理**
  - 打印控制
  - 文档修改限制
  - 复制保护
  - 高分辨率打印选项

## 📊 技术规格

- **加密方式**：128 位 AES 加密
- **哈希算法**：SHA-256 用于口令保护
- **文件处理**：PyPDF2 用于 PDF 操作
- **图形界面**：PyQt5 提供现代化界面

## 📝 文档

详细文档请访问我们的 [Wiki](https://github.com/yourusername/PDF-Security-Manager/wiki)。

## 🤝 贡献指南

欢迎贡献！请阅读我们的[贡献指南](CONTRIBUTING.md)了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🔗 参考资料

- [PyPDF2 文档](https://pypdf2.readthedocs.io/en/latest/)
- [PyQt5 文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [PDF 安全标准](https://www.iso.org/standard/75839.html)

## 📞 技术支持

如需技术支持，请在 [GitHub 仓库](https://github.com/yourusername/PDF-Security-Manager/issues) 提交问题。 