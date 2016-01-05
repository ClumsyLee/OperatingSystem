% AVL树/红黑树问题
% 无36
  李思涵
  2013011187
  <lisihan969@gmail.com>
% \today

# 问题描述

在 Windows 的虚拟内存管理中，将 VAD 组织成 AVL 树。VAD 树是一种平衡二叉树。红黑树也是一种
自平衡二叉查找树，在 Linux 2.6 及其以后版本的内核中，采用红黑树来维护内存块。

请尝试参考 Linux 源代码将 WRK 源代码中的 VAD 树由 AVL 树替换成红黑树。


# 现有结构

## Linux

我们选取的 Linux Kernel 版本为 4.4-rc8。其中和红黑树有关的代码共有以下三个文件：

- `include/linux/rbtree.h`
- `include/linux/rbtree_augmented.h`
- `lib/rbtree.c`

有关其使用方法的介绍可以在 `Documentation/rbtree.txt` 中找到。

## Windows

# 模块设计

# 代码实现

# 实验结果



# 思考题

##	柜员人数和顾客人数对结果分别有什么影响？

##	实现互斥的方法有哪些？各自有什么特点？效率如何？
