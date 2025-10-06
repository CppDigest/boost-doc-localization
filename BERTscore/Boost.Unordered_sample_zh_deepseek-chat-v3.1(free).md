这是一份关于Boost C++库的技术文档，特别是关于Boost.Unordered哈希容器的内容。请保持所有技术准确性和格式进行翻译。

# [![图片1: Boost C++库](https://www.boost.org/static/img/original_docs/space.png)Boost C++库](https://www.boost.org/)

...世界上最受推崇和专业设计的C++库项目之一。——[Herb Sutter](https://herbsutter.com/)和[Andrei Alexandrescu](http://en.wikipedia.org/wiki/Andrei_Alexandrescu)，[C++编码标准](https://books.google.com/books/about/C++_Coding_Standards.html?id=mmjVIC6WolgC)

搜索...

简介 :: Boost.Unordered

\===============

### [Boost.Unordered](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/intro.html)

*   ```
      *   [简介](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/intro.html)
    ```
    
    *   [哈希表基础](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/buckets.html)
        
    *   [相等谓词和哈希函数](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/hash_equality.html)
        
    *   [常规容器](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/regular.html)
        
    *   [并发容器](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/concurrent.html)
        
    *   [哈希质量](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/hash_quality.html)
        
    *   [标准符合性](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/compliance.html)
        
    *   [数据结构](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/structures.html)
        
    *   [可调试性](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/debuggability.html)
        
    *   [基准测试](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/benchmarks.html)
        
    *   [实现原理](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/rationale.html)
        
    *   [参考](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/ref.html)
        
        *   [`<boost/unordered/unordered_map_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_map_fwd.html)
        *   [`<boost/unordered_map.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_map_top.html)
        *   [`<boost/unordered/unordered_map.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_map.html)
        *   [`unordered_map`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_map.html)
        *   [`unordered_multimap`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_multimap.html)
        *   [`<boost/unordered/unordered_set_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_set_fwd.html)
        *   [`<boost/unordered_set.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_set_top.html)
        *   [`<boost/unordered/unordered_set.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_set.html)
        *   [`unordered_set`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_set.html)
        *   [`unordered_multiset`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_multiset.html)
        *   [哈希特性](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/hash_traits.html)
        *   [统计信息](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/stats.html)
        *   [`<boost/unordered/unordered_flat_map_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_flat_map_fwd.html)
        *   [`<boost/unordered/unordered_flat_map.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_flat_map.html)
        *   [`unordered_flat_map`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_flat_map.html)
        *   [`<boost/unordered/unordered_flat_set_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_flat_set_fwd.html)
        *   [`<boost/unordered/unordered_flat_set.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_flat_set.html)
        *   [`unordered_flat_set`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_flat_set.html)
        *   [`<boost/unordered/unordered_node_map_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_node_map_fwd.html)
        *   [`<boost/unordered/unordered_node_map.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_node_map.html)
        *   [`unordered_node_map`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_node_map.html)
        *   [`<boost/unordered/unordered_node_set_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_node_set_fwd.html)
        *   [`<boost/unordered/unordered_node_set.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_unordered_node_set.html)
        *   [`unordered_node_set`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/unordered_node_set.html)
        *   [`<boost/unordered/concurrent_flat_map_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_flat_map_fwd.html)
        *   [`<boost/unordered/concurrent_flat_map.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_flat_map.html)
        *   [`concurrent_flat_map`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/concurrent_flat_map.html)
        *   [`<boost/unordered/concurrent_flat_set_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_flat_set_fwd.html)
        *   [`<boost/unordered/concurrent_flat_set.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_flat_set.html)
        *   [`concurrent_flat_set`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/concurrent_flat_set.html)
        *   [`<boost/unordered/concurrent_node_map_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_node_map_fwd.html)
        *   [`<boost/unordered/concurrent_node_map.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_node_map.html)
        *   [`concurrent_node_map`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/concurrent_node_map.html)
        *   [`<boost/unordered/concurrent_node_set_fwd.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_node_set_fwd.html)
        *   [`<boost/unordered/concurrent_node_set.hpp>`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/header_concurrent_node_set.html)
        *   [`concurrent_node_set`](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/reference/concurrent_node_set.html)
    *   [变更日志](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/changes.html)
        
    *   [参考文献](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/bibliography.html)
        
    *   [版权和许可](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/copyright.html)
        

[](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/intro.html)

*   [Boost.Unordered](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/intro.html)
*   [简介](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/intro.html)

# 简介

[哈希表](https://en.wikipedia.org/wiki/Hash_table)是极其流行的计算机数据结构，几乎在任何编程语言中都能以某种形式找到它们。虽然其他关联结构（如rb树，在C++中被`std::set`和`std::map`使用）具有对数时间复杂度的插入和查找操作，但如果配置得当，哈希表平均可以在常数时间内执行这些操作，并且通常要快得多。

C++在C++11中引入了_无序关联容器_`std::unordered_set`、`std::unordered_map`、`std::unordered_multiset`和`std::unordered_multimap`，但自那时以来哈希表的研究并未停止：CPU架构的进步，如更强大的缓存、[SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data)操作和日益普及的[多核处理器](https://en.wikipedia.org/wiki/Multi-core_processor)，为改进的基于哈希的数据结构和新的用例开辟了可能性，这些用例完全超出了2011年规范的无序关联容器的能力范围。

Boost.Unordered提供了一系列具有不同标准符合级别、性能和预期使用场景的哈希容器：

表1. Boost.Unordered容器| | **基于节点** | **扁平** | | --- | --- | --- | | **闭散列法** | `boost::unordered_set boost::unordered_map boost::unordered_multiset boost::unordered_multimap` | | | **开散列法** | `boost::unordered_node_set boost::unordered_node_map` | `boost::unordered_flat_set boost::unordered_flat_map` | | **并发** | `boost::concurrent_node_set` `boost::concurrent_node_map` | `boost::concurrent_flat_set` `boost::concurrent_flat_map` |

*   **闭散列法容器**完全符合C++无序关联容器的规范，并在所需标准接口的技术约束下提供了市场上最快的实现之一。
    
*   **开散列法容器**依赖于更快的数据结构和算法（在典型场景中快2倍以上），同时与标准接口略有不同以适应实现。有两种变体：**扁平**（最快的）和**基于节点**的，后者在重新哈希时提供指针稳定性，但代价是速度较慢。
    
*   最后，**并发容器**是为高性能多线程场景设计和实现的。它们的接口与常规C++容器截然不同。提供了扁平型和基于节点的变体。
    

Boost.Unordered中的所有集合和映射都分别类似于`std::unordered_set`和`std::unordered_map`进行实例化：

```c++
namespace boost {
    template <
        class Key,
        class Hash = boost::hash<Key>,
        class Pred = std::equal_to<Key>,
        class Alloc = std::allocator<Key> >
    class unordered_set;
    // 同样适用于unordered_multiset、unordered_flat_set、unordered_node_set、
    // concurrent_flat_set和concurrent_node_set

    template <
        class Key, class Mapped,
        class Hash = boost::hash<Key>,
        class Pred = std::equal_to<Key>,
        class Alloc = std::allocator<std::pair<Key const, Mapped> > >
    class unordered_map;
    // 同样适用于unordered_multimap、unordered_flat_map、unordered_node_map、
    // concurrent_flat_map和concurrent_node_map
}
```

c++![图片2: 复制图标](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/_/img/octicons-16.svg#view-clippy)已复制!

在无序关联容器中存储对象需要键相等函数和哈希函数。标准容器中的默认函数对象支持一些基本类型，包括整数类型、浮点类型、指针类型和标准字符串。由于Boost.Unordered使用[boost::hash](https://www.boost.org/doc/libs/latest/libs/container_hash/index.html)，它还支持其他一些类型，包括标准容器。要使用这些方法不支持的任何类型，您必须扩展Boost.Hash以支持该类型，或使用您自己的自定义相等谓词和哈希函数。有关更多详细信息，请参阅[相等谓词和哈希函数](https://www.boost.org/doc/libs/latest/libs/unordered/doc/html/unordered/hash_equality.html#hash_equality)部分。