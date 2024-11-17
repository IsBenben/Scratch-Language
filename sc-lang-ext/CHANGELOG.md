# Change Log

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
