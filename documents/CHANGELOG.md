# 更新日志

## version 1.1

- *1.1 新增* 预处理命令解析系统。
- *1.1 新增* `--recursionlimit` 控制台参数。
- *1.1.1 新增* `--quite` 控制台参数。
- *1.1.1 新增* `--lint` 控制台参数，暂无作用。
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
