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

`rbtree.h` 包含了红黑树的结构体的定义，以及对其数据的基本访问和操作。其中结点的定义如下：

```c
struct rb_node {
    unsigned long  __rb_parent_color;
    struct rb_node *rb_right;
    struct rb_node *rb_left;
} __attribute__((aligned(sizeof(long))));
    /* The alignment might seem pointless, but allegedly CRIS needs it */
```

红黑树根的定义如下：

```c
struct rb_root {
    struct rb_node *rb_node;
};
```

一些基本的访问和操作如下：

```c
#define rb_parent(r)   ((struct rb_node *)((r)->__rb_parent_color & ~3))
#define rb_entry(ptr, type, member) container_of(ptr, type, member)

extern void rb_insert_color(struct rb_node *, struct rb_root *);
extern void rb_erase(struct rb_node *, struct rb_root *);

/* Find logical next and previous nodes in a tree */
extern struct rb_node *rb_next(const struct rb_node *);
extern struct rb_node *rb_prev(const struct rb_node *);
extern struct rb_node *rb_first(const struct rb_root *);
extern struct rb_node *rb_last(const struct rb_root *);

```

在 `rbtree_augmented.h` 中还定义了更多的内部访问和操作，如下所示：

```c
#define RB_RED      0
#define RB_BLACK    1

#define __rb_parent(pc)    ((struct rb_node *)(pc & ~3))

#define __rb_color(pc)     ((pc) & 1)
#define __rb_is_black(pc)  __rb_color(pc)
#define __rb_is_red(pc)    (!__rb_color(pc))
#define rb_color(rb)       __rb_color((rb)->__rb_parent_color)
#define rb_is_red(rb)      __rb_is_red((rb)->__rb_parent_color)
#define rb_is_black(rb)    __rb_is_black((rb)->__rb_parent_color)

static inline void rb_set_parent(struct rb_node *rb, struct rb_node *p)
{
    rb->__rb_parent_color = rb_color(rb) | (unsigned long)p;
}

static inline void rb_set_parent_color(struct rb_node *rb,
                       struct rb_node *p, int color)
{
    rb->__rb_parent_color = (unsigned long)p | color;
}
```

我们总结如下：

- 红黑树结点结构体是以 long 的长度对齐的，在现在的计算机上这个值一般是 4 字节或是 8 字节。
- 红黑树结点中，父节点地址和颜色被储存在了同一个 long 变量中。其中低两位保存的是结点的颜色，
  高位保存的是结点的地址（以 4 字节为单位）。这么做可行是建立在 C 语言标准中，long 的长度
  至少为 4 字节的基础上的，故结构体在以 long 对其后最低 2 位一定为 00。
- 该红黑树用 0 代表红结点，用 1 代表黑结点。
- 外界通过在合适的结点调用 `rb_link_node` 插入新结点，然后调用 `rb_insert_color` 使树
  平衡。
- 外界使用 `rb_erase` 删除结点。

同时，需要注意到的是，`rbtree_augmented.h` 中还提供了一些操作的增强版本，如
`rb_insert_augmented` 和 `rb_erase_augmented`。这些函数主要是为了实现“增强红黑树”，
也就是每个结点保存了一些额外信息的红黑树。由于我们的实现中不需要增强红黑树，我们将忽略那些带有
`augmented` 后缀的函数版本。同时，我们需要实现的对外接口也应只限于 `rbtree.h` 中的对外
接口。`rbtree_augmented.h` 中的对外接口不用移植，但其中的一些内部定义和访问需要移植。


## WRK

为了完成移植工作，我们还需要了解 WRK 中 VAD 树的结构和接口。

# 模块设计

# 代码实现

# 实验结果



# 思考题

##	柜员人数和顾客人数对结果分别有什么影响？

##	实现互斥的方法有哪些？各自有什么特点？效率如何？
