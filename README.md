# Scratch.py

**这只是一个临时起性子的空壳子！没有什么实际意义。**

Scratch-Language.

## 介绍

Scratch.py 是Python制作的编程语言，它的编译器可以将你写的源代码转换为Scratch的project.json文件。

## 使用

这个语言的编译器会把源文件转换成Scratch可识别的 `project.json`！

当前支持的内容：

### 注释

```plain
// 单行注释
/*
多行注释
*/
```

### 函数调用

函数名可以在 <https://en.scratch-wiki.info/wiki/List_of_Block_Opcodes> 上找。仅支持小部分函数。

```plain
// 说hello,world
looks_say("hello,world")
```

本语言的大部分语法也会转换成函数调用。

### 语句

一条语句以 `;` 或换行结尾。

```plain
// 两条以换行分割的语句
looks_say("hello,world")
looks_say("hello,world")

// 一行里的两条以分号分割的语句
looks_say("hello,world"); looks_say("hello,world");
```

### 变量

```plain
// 声明
var a = 1
const b = 2

// 修改
a += 1
b = 2  // Error！无法修改常量

// 获取
looks_say(a)
```

#### 特殊变量

这些变量不属于关键字。可以被同名声明覆盖，而不会报错。

```plain
// Python代码：__import__('math').e / .pi
e: 2.718...
pi: 3.141...

// 注：下面这两个编译后是字符串，而不是运算
// 写上运算只是好理解
inf -> Infinity: 1 / 0
nan -> NaN: 0 / 0
```

#### 块级作用域

本质上就是不同作用域改不同的变量名。

```plain
var a = 1  // 外层作用域
{
	var a = 2  // 内层作用域
}
a  // == 1，内层不影响外层
```

### 字面量

#### 布尔值

这些值是关键字，不可以定义为变量名。

- `true`：编译成“&lt &gt不成立”
- `false`：编译成“&lt&lt &gt不成立&gt不成立”

#### 整数

- `0b`…：二进制
- `0o`…：八进制
- `0x`…：十六进制
- 直接写：十进制
- `0`：零

#### 小数

- …`.`：自动在末尾补 $0$
- `.`…：自动在开头补 $0$
- …`.`…：小数
- 只有 `.`：报错

#### 字符串

`"`内容`"`

目前还不支持转义字符。

### 分支

```plain
if (true) {
    looks_say("It's true!")
} else {
    looks_say("It's false!")
}
```

### 运算

#### 运算符

- 算术运算符：`+ - * / %` 加减乘除（二元），`+ -` 正负（一元）。
- 逻辑运算符：`&&` 与，`||` 或（二元），`!` 非（一元）。
- 比较运算符：`>= <= > < == !=`。
- 成员运算符：`in` 属于，`contains` 包含。
- 拼接运算符：`..`。
- 字符串索引：字符串 `[` 索引 `]`，用于访问字符串中的单个字符。

#### 示例

```plain
looks_sayforsecs("e: " .. e, 0.5)
looks_sayforsecs("e + pi: " .. e + pi, 0.5)

const a = 1
const b = 2
looks_sayforsecs("a: " .. a .. ", b: " .. b, 0.5)
if (a != b) looks_sayforsecs("a != b", 0.5)
else looks_sayforsecs("a == b", 0.5)
```

### 循环

```plain
var i = 0
while (i <= 5) {  // 重复执行直到 i <= 5 不成立
	looks_sayforsecs(i, 0.5)
	i += 1
}

var j = 0
until (j > 5) {  // 重复执行直到 j > 5
	looks_sayforsecs(j, 0.5)
	j += 1
}
```

### 函数（暂不支持返回值）

```plain
/**
 * 说a，b秒（只是一个例子）
 */
function test_function(a, b) {
    // 这里会生成函数作用域
    looks_say(a)
    control_wait(b)
    looks_say("")
}

test_function("Hello world", inf)
```
