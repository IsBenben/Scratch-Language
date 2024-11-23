# Scratch Language Extension README

Scratch Language 是用Python为Scratch做的编程语言。包括词法分析、语法分析、编译器。

编译成品为Scratch可直接识别的project.json。支持打包sb3格式。

已经支持基本的语法。包括注释、函数、变量、判断、运算、列表、循环。

视频：https://www.bilibili.com/video/BV1G31iY3ETX

## Features

Scratch Language 的语法见 https://github.com/IsBenben/Scratch-Language/blob/main/documents/CHANGELOG.md。

本扩展支持：
- 语法高亮（关键字及字面量，不支持进一步的高亮）。
- 代码提示（关键字及 API，不支持进一步的提示）。
- 快捷运行（须手动下载编译器）。

## Requirements

扩展没有直接依赖。

如果要使用快捷运行功能，需要下载编译器和 Python 3.11+，见 https://github.com/IsBenben/Scratch-Language/releases。

## Extension Settings

扩展有以下设置项：

* `sc-lang-ext.showRunIconInEditorTitleMenu`：在编辑器标题栏中显示“运行代码”图标。
* `sc-lang-ext.alwaysRunInNewTerminal`：始终在新的控制台运行代码。
* `sc-lang-ext.compilerPath`：编译器文件cmdnew.py文件路径。
* `sc-lang-ext.compilerOptions`：编译器命令行的附加选项。

## Known Issues

包括编译器的 Issue，可见 https://github.com/IsBenben/Scratch-Language/issues。

## Release Notes

## version 1.1

- *1.1 新增* 预处理命令解析系统。
- *1.1 新增* `--recursionlimit` 命令行参数。
- *1.1.1 新增* `--quite` 命令行参数。
- *1.1.1 新增* `--lint` 命令行参数，暂无作用。
- *1.1.1 新增* VS Code 插件语言服务器。
- *1.1.1 更改* `--recursionlimit` 使用 `argparser` 自带的类型限制。
- *1.1.1 修复* 关闭文件函数总是使用 `atexit` 注册，防止程序报错无法正常关闭文件。
- *1.1.1 更改* hash 值生成算法的第一位从 `0` 改为 `$`。
- *1.1.1 修复* [#1](https://github.com/IsBenben/Scratch-Language/issues/1) 不支持空函数体。
- *1.1.2 修复* [#1](https://github.com/IsBenben/Scratch-Language/issues/1) 函数参数的作用域泄露。
- *1.1.2 修复* [#1](https://github.com/IsBenben/Scratch-Language/issues/1) 可以修改内置函数。
- *1.1.2 新增* `attribute` 关键字。
- *1.1.2 新增* `#ifndef`、`#ifdef`、`#endif` 预处理命令。
- *1.1.3 修复* mypy 报错。
- *1.1.4 新增* 三元表达式。
- *1.1.4 新增* VS Code 插件运行功能。

## version 1.2

- *1.2 新增* 基本的优化（例如 `1 + 1` -> `2`）。
- *1.2 新增* `--nooptimize` 命令行参数。
- *1.2.1 修复* [#2](https://github.com/IsBenben/Scratch-Language/issues/2) KeyError: None。
- *1.2.1 修复* VS Code 插件使用 `*` 启动事件。
- *1.2.1 更改* 由于重名，VS Code 插件更名为 `sc-lang-ext`，功能基本不受影响。
- *1.2.1 新增* `nooptimize` 函数属性。
- *1.2.2 修复* 错误的 `.vscodeignore`。
- *1.2.2 新增* 数组推导式。
- *1.2.3 修复* `while/until` 循环的条件三元表达式不能动态求值。
- *1.2.3 新增* 支持列表的三元表达式。
- *1.2.3 新增* 支持布尔值的三元表达式。
