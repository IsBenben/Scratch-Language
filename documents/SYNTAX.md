# 语法

这个语言的编译器会把源文件转换成Scratch可识别的 `project.json`！

当前支持的内容：

## 注释

```scl
// 单行注释
/*
多行注释
*/
```

## 函数调用

函数名可以在 <https://en.scratch-wiki.info/wiki/List_of_Block_Opcodes> 上找。仅支持小部分函数。

```scl
// 说hello,world
looks_say("hello,world")
```

本语言的大部分语法也会转换成函数调用。

## 语句

一条语句以 `;` 或换行结尾。

```scl
// 两条以换行分割的语句
looks_say("hello,world")
looks_say("hello,world")

// 一行里的两条以分号分割的语句
looks_say("hello,world"); looks_say("hello,world");
```

## 变量

```scl
// 声明
var a = 1
const b = 2

// 修改
a += 1
b = 2  // Error！无法修改常量

// 获取
looks_say(a)
```

### 命名规范

合法变量名：英文/中文/下划线/数字，不能以数字开头。

由于英文可能会和内部的变量产生冲突，所以对于变量命名，建议使用中文。

### 特殊变量

这些变量不属于关键字。可以被同名声明覆盖，而不会报错。

```scl
// Python代码：__import__('math').e / .pi
e: 2.718...
pi: 3.141...

// 注：下面这两个编译后是字符串，而不是运算
// 写上运算只是好理解
inf -> Infinity: 1 / 0
nan -> NaN: 0 / 0
```

### 块级作用域

本质上就是不同作用域改不同的变量名。

```scl
var a = 1  // 外层作用域
{
	var a = 2  // 内层作用域
}
a  // == 1，内层不影响外层
```

## 字面量

### 布尔值

这些值是关键字，不可以定义为变量名。

- `true`：编译成“&lt &gt不成立”
- `false`：编译成“&lt&lt &gt不成立&gt不成立”

### 整数

- `0b`…：二进制
- `0o`…：八进制
- `0x`…：十六进制
- 直接写：十进制
- `0`：零

### 小数

- …`.`：自动在末尾补 $0$
- `.`…：自动在开头补 $0$
- …`.`…：小数
- 只有 `.`：报错

### 字符串

`"`内容`"`

目前还不支持转义字符。

## 分支

```scl
if (true) {
    looks_say("It's true!")
} else {
    looks_say("It's false!")
}
```

Scratch Language 通过 `if` 语句实现分支。并通过一个小的技巧实现了 `if` - `else if` - `else`。

### 表达式

```
// 三元表达式
looks_say( \
    if (1 > 1) "true" \
    else "false" \
)
```

## 运算

### 运算符

- 算术运算符：`+ - * / %` 加减乘除（二元），`+ -` 正负（一元）。
- 逻辑运算符：`&&` 与，`||` 或（二元），`!` 非（一元）。
- 比较运算符：`>= <= > < == !=`。
- 成员运算符：`in` 属于，`contains` 包含。
- 拼接运算符：`..`。
- 字符串索引：字符串 `[` 索引 `]`，用于访问字符串中的单个字符。

对于简单的运算，编译器会进行优化（例如 `1 + 1` -> `2`）。

### 示例

```scl
looks_sayforsecs("e: " .. e, 0.5)
looks_sayforsecs("e + pi: " .. e + pi, 0.5)

const a = 1
const b = 2
looks_sayforsecs("a: " .. a .. ", b: " .. b, 0.5)
if (a != b) looks_sayforsecs("a != b", 0.5)
else looks_sayforsecs("a == b", 0.5)
```

## 函数（暂不支持返回值）

```scl
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

### 修改属性

函数使用 `attribute` 关键字修改属性。

目前支持修改：
- 运行时不刷新屏幕（`norefresh`）。
- 不进行优化（`nooptimize`）。

```scl
// 顺序不能错，可在不同位置写，但是一个位置只能写一个
function attribute(norefresh) test_function() { /* 做一些事 */ }
function test_function attribute(norefresh)() { /* 做一些事 */ }
function test_function() attribute(norefresh) { /* 做一些事 */ }
```

## 克隆体

```scl
clone {
    // 克隆体的代码
    looks_say("Hello, world! #1");
}
clone {
    // 克隆体的代码
    looks_say("Hello, world! #2");
}
// 两个克隆体的代码不会互相影响
```

## 列表 / 数组

### 列表字面量

```scl
// 第一种：直接书写列表元素
array foo = [1, 2, 3];

// 第二种：生成区间列表（仅适用于数字）
array bar = 1 -> 5;  // 等同于 [1, 2, 3, 4, 5]

// 第三种：通过运算（不是本节讨论的范围）
```

### 创建列表

定义列表的关键字为 `array`，其余语法和定义变量相同。

```scl
// 创建列表（不建议）
// 由于 Scratch 有机制：重启之后列表项目不会删除
array foo;

// 创建列表（推荐）
// 给予默认值
array bar = [];
```

### 列表推导式

列表推导式支持子语句的嵌套，提供灵活的方式生成列表。

```scl
// 生成一个 5x5 的“乘法表”
array foo = [for (i = 1 -> 5) \
             for (j = 1 -> 5) \
             if (j >= i) \
             (i .. "x" .. j .. "=" .. i * j)];
```

### 增加元素

列表支持通过 `+` 运算符快速增加元素。

```scl
// 更简洁的语法，适合多个元素
// 但是编译之后积木比较多，可能产生效率问题
foo += [1, 2, 3]

// 较为复杂的语法，适合单个元素
// 效率相比起来较高
data_addtolist(foo, 1)
data_addtolist(foo, 2)
data_addtolist(foo, 3)
```

### 删除元素

本操作直接对应积木块 `data_deleteoflist`，只是起了一个别名。

```scl
// 删除第一个元素
delete foo[1]

// 同上，不推荐使用
data_deleteoflist(foo, 1)
```

### 更改元素

本操作直接对应积木块 `data_replaceitemoflist`，只是起了一个别名。

```scl
// 更改第一个元素为 10
foo[1] = 10

// 同上，不推荐使用
data_replaceitemoflist(foo, 1, 10)
```

### 获取元素

本操作直接对应积木块 `data_itemoflist`，只是起了一个别名。

```scl
// 获取第一个元素
const a = foo[1]

// 同上，不推荐使用
const b = data_itemoflist(foo, 1)
```

## 循环

循环分为 `while` 循环、`until` 循环和 `for` 循环。

```scl
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

for (k = 1 -> 5) {  // 仅适用于遍历列表
    looks_sayforsecs(k, 0.5)
}
```

## 预处理

预处理指令以 `#` 开头，在编译时会进行展开。

### `#include "path/to/file"`

```scl
#include "examples/preprocess_test.scl"
// → 直接将文件内容复制到此处
```

### `#include <header_name>`

```scl
#include <pen>
// → 将 /includes/pen.scl 的文件内容复制到此处
```

### `#define value identifier(param1, param2, ...)`

```scl
#define -1 a
#define 0 a()
#define 1 a(b)

// 这里只是简单替换，并不会对语法进行检查
const res1 = a;  // == -1
const res2 = a();  // == 0
const res3 = a(b);  // == 1

// 例如这里的代码正常工作
#define { left
#define } right

left 
    looks_say("Hello, world!");
right
```

### `#undef identifier`

```scl
#define a 1
#undef a  // 取消定义a
const b = a;  // Error! 找不到a
```

### `#error "message"`

```scl
#error "This is an error!"  // Error! 展开时出错
```

### `#ifdef identifier`

与 `#endif` 配合使用，可以嵌套。判断是否定义了某个预处理命令，如果定义了则展开。

### `#ifndef identifier`

与 `#endif` 配合使用，可以嵌套。判断是否没有定义某个预处理命令，如果没有定义则展开。与 `#ifdef` 相反。

### `#endif`

结束 `#ifdef` 或 `#ifndef` 的影响范围。

```scl
#ifdef a
    looks_say("a is defined!")
#endif

#ifndef b
    looks_say("b is not defined!")
// 末尾可以省略 #endif（不建议，因为其他文件可能#include，但是影响范围会延续）
#endif
```
