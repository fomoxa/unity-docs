# Collection

Collection là một list, một dictionary hoặc một set mà một `NetworkBehaviour` giữ và server giữ đồng bộ trên mọi observer. Server chỉ gửi các thao tác bạn gọi trên nó, như một lần thêm hay một lần xoá. Mỗi client áp chúng theo đúng thứ tự đó và nhận một callback cho từng thao tác.

## Khi nào dùng <a href="#when-to-use-it" id="when-to-use-it"></a>

Dùng collection cho dữ liệu lớn lên và nhỏ đi: túi đồ, danh sách người chơi trong phòng, bảng điểm. Một [state model](state.md) có field `Array` được gửi nguyên vẹn khi mảng đổi độ dài, nên thêm một món vào list 500 món là gửi cả 500. Collection chỉ gửi một món đó.

Các giá trị đổi cùng nhau và giữ nguyên kích thước, như máu hay vị trí trong một trận, nên ở lại trong state model, vì với chúng state model rẻ hơn.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

Phần tử là một model hoặc một kiểu nguyên thuỷ. Phần tử model được khai báo như mọi model khác. Nó không cần channel, vì nó không bao giờ đi như một message riêng:

```csharp
using Fomoxa;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class Item
    {
        [Network("u32")]
        [Codec("net")]
        public uint Id { get; set; }

        [Network("u16")]
        [Codec("net")]
        public ushort Count { get; set; }
    }
}
```

Behaviour giữ các collection của nó và đăng ký từng cái trong `OnRegisterState`, dưới một index do bạn chọn:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking;
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

public sealed class Inventory : NetworkBehaviour
{
    private readonly NetworkList<Item> items = new NetworkList<Item>();
    private readonly NetworkDictionary<string, int> scores = new NetworkDictionary<string, int>();
    private readonly NetworkSet<ulong> visitors = new NetworkSet<ulong>();

    public IReadOnlyList<Item> Items => items;

    protected override void OnRegisterState(NetworkState state)
    {
        state.Use(0, items, ItemNetAdapter.Instance, OnItemsChanged);
        state.Use(1, scores);
        state.Use(2, visitors);
    }

    public void Pick(uint id)
    {
        items.Add(new Item { Id = id, Count = 1 });
    }

    public void UseOne(int index)
    {
        items.Modify(index, item => item.Count--);
    }

    private void OnItemsChanged(NetworkListOperation operation, int index, Item oldItem, Item newItem)
    {
        Debug.Log($"{name}: {operation} at {index}");
    }
}
```

Gọi `Pick` và `UseOne` trên server. Cuối tick đó mỗi observer nhận các thao tác, áp chúng lên `items` của riêng nó và gọi `OnItemsChanged` một lần cho mỗi thao tác.

## Đăng ký collection <a href="#registering-a-collection" id="registering-a-collection"></a>

`state.Use(index, collection, ...)` đăng ký một collection. Index là một `byte` do bạn chọn. Các lời gọi có thể theo thứ tự bất kỳ và index có thể nhảy số; package xử lý các collection theo thứ tự index tăng dần. Dùng cùng một index hai lần trong một behaviour, hoặc đăng ký một instance collection hai lần, sẽ ném `HandlerRegistrationException`.

Index đi kèm mọi thao tác, nên client phải đăng ký cùng index với cùng loại collection và cùng kiểu phần tử. Nếu message spawn cho thấy một tập index, loại hoặc kiểu phần tử khác, client dừng với `ObjectMismatch` (`InvalidSpawn`).

Một behaviour có thể đăng ký collection bên cạnh [state model](state.md) của nó, hoặc không cần state model.

## Kiểu phần tử <a href="#element-types" id="element-types"></a>

| Phần tử | Đăng ký |
|---|---|
| Một model (`[Network]`, `[Codec("net")]`) | Truyền adapter của nó: `state.Use(0, items, ItemNetAdapter.Instance)` |
| `bool`, `sbyte`, `byte`, `short`, `ushort`, `int`, `uint`, `long`, `ulong`, `float`, `double`, `string` | Không cần adapter: `state.Use(1, scores)` |

Value của dictionary có thể là model hoặc kiểu nguyên thuỷ. Key của dictionary và phần tử của set phải là kiểu nguyên thuỷ, vì chúng được so sánh theo giá trị. Model đăng ký thiếu adapter, hoặc model dùng làm key hay phần tử set, sẽ ném `HandlerRegistrationException` với thông báo nêu tên kiểu.

## Thao tác <a href="#operations" id="operations"></a>

Ba kiểu theo `List<T>`, `Dictionary<TKey, TValue>` và `HashSet<T>`, và hiện thực `IReadOnlyList<T>`, `IReadOnlyDictionary<TKey, TValue>` và `IReadOnlyCollection<T>`, nên `foreach`, LINQ và các method nhận những interface đó đều dùng được.

| Kiểu | Thao tác |
|---|---|
| `NetworkList<T>` | `Add`, `Insert`, `list[index] = value`, `RemoveAt`, `Remove(item)`, `Clear`, `Dirty(index)`, `Modify(index, ...)` |
| `NetworkDictionary<TKey, TValue>` | `Add` (ném `ArgumentException` nếu key đã có), `dictionary[key] = value`, `Remove(key)`, `Clear`, `Dirty(key)`, `Modify(key, ...)`; đọc bằng `ContainsKey`, `TryGetValue`, `Keys`, `Values` |
| `NetworkSet<T>` | `Add`, `Remove`, `Clear`, `Contains` |

Mỗi lời gọi làm đổi collection gửi một thao tác, trừ các trường hợp sau:

- `Remove(item)` trên list xoá phần tử đầu tiên bằng `item`, so bằng `Equals`, với model nghĩa là cùng một instance. Nó được gửi như một lần xoá tại index đó.
- `Remove` trên dictionary hoặc set trả về `false` và không gửi gì khi key hoặc phần tử không có. `Add` trên set trả về `false` và không gửi gì khi phần tử đã có.
- Gán cho một phần tử đúng giá trị nó đang có vẫn gửi thao tác. Server không so sánh giá trị.

Phần tử, value hoặc key là `null` sẽ ném `ArgumentNullException` ngay tại lời gọi, vì một model hay một `string` trên wire không thể là null.

## Sửa một phần tử tại chỗ <a href="#changing-an-element-in-place" id="changing-an-element-in-place"></a>

Đổi một field của phần tử model không tự gửi gì. Sau đó hãy gọi `Dirty` trên server, và phần tử được gửi lại dưới dạng `Set`:

```csharp
items[index].Count = 5;
items.Dirty(index);
```

`Modify` làm cả hai bước:

```csharp
items.Modify(index, item => item.Count--);
```

Để truyền một giá trị mà không phải capture nó trong lambda, để lời gọi không cấp phát, dùng overload nhận thêm một tham số state:

```csharp
items.Modify(index, amount, (item, value) => item.Count -= value);
```

Phần tử vẫn được đánh dấu khi action ném exception, và exception sau đó được ném tiếp ra ngoài. `Modify` chỉ có cho phần tử model; phần tử nguyên thuỷ thì thay bằng phép gán. Cả `Dirty` và `Modify` ném giống như khi đọc nếu index nằm ngoài phạm vi hoặc key không có.

Phần tử được encode lúc bạn gọi thao tác. Một field đổi sau đó trong cùng tick mà không có `Dirty` mới sẽ không được gửi.

## Callback <a href="#callbacks" id="callbacks"></a>

Mỗi collection nhận một callback tuỳ chọn, được gọi trên client sau khi thao tác đã được áp:

| Kiểu | Callback |
|---|---|
| `NetworkList<T>` | `(NetworkListOperation operation, int index, T oldItem, T newItem)` |
| `NetworkDictionary<TKey, TValue>` | `(NetworkDictionaryOperation operation, TKey key, TValue oldValue, TValue newValue)` |
| `NetworkSet<T>` | `(NetworkSetOperation operation, T oldItem, T newItem)` |

| Thao tác | Index hoặc key | Giá trị cũ | Giá trị mới |
|---|---|---|---|
| `Add`, `Insert` | Nơi phần tử được đặt vào | `default` | Phần tử |
| `Set` | Index hoặc key của phần tử | Phần tử trước đó | Phần tử sau đó |
| `RemoveAt`, `Remove` | Nơi phần tử đã nằm | Phần tử bị xoá | `default` |
| `Clear` | `-1`, hoặc key `default` | `default` | `default` |
| `Reset` | `-1`, hoặc key `default` | `default` | `default` |

Callback của set không có index hay key. `Dirty` và `Modify` đến dưới dạng `Set`. Gán vào một key của dictionary đến dưới dạng `Add` khi key mới và dạng `Set` khi key đã có. `Clear` và `Reset` chạy một lần, sau khi collection đã được làm rỗng hoặc thay mới. `Reset` nghĩa là client đã nhận lại toàn bộ collection sau khi nó [bị lệch nhịp](#recovery); hãy đọc chính collection để dựng lại những gì phụ thuộc vào nó.

Nội dung đến cùng message spawn không kích hoạt callback. Nó đã nằm sẵn khi `OnStartClient` chạy.

## Cách hoạt động <a href="#how-it-works" id="how-it-works"></a>

Giữa hai lần gửi, server ghi lại từng thao tác theo thứ tự bạn gọi. Sau các event `OnTick` và `OnPostTick` của tick, cùng chỗ [state](state.md) được gửi, server gửi một message cho mỗi collection có thao tác, tới mọi observer. Trong một behaviour, state model đi trước, rồi tới các collection theo thứ tự index tăng dần, nên callback của collection đã thấy state mới.

`Clear` bỏ các thao tác ghi từ lần gửi trước, vì client chỉ cần collection rỗng. Thao tác thực hiện khi object không có observer nào cũng bị bỏ; observer đến sau nhận toàn bộ collection trong message spawn của nó.

Server đánh số mọi thao tác. Client bắt đầu observe giữa hai lần gửi sẽ nhận nội dung hiện tại trong message spawn, gồm cả các thao tác server chưa gửi. Khi các thao tác đó đến, client thấy qua số thứ tự rằng nó đã có chúng và bỏ qua.

## Hành vi trên server <a href="#server-behavior" id="server-behavior"></a>

Chỉ thay đổi collection trên server. Server không nhận callback cho thay đổi của chính nó.

Collection có thể được điền trước `Spawn`, ví dụ trong `Awake`. Không có gì được gửi cho các thay đổi đó, và nội dung đi trong message spawn. Sau khi server despawn object cũng vậy: được phép thay đổi và không gửi gì, rồi lần `Spawn` tiếp theo mang theo nội dung.

## Hành vi trên client <a href="#client-behavior" id="client-behavior"></a>

Trên client, mọi lời gọi làm đổi một collection đã spawn đều ném `InvalidOperationException`, kể cả `Dirty` và `Modify`. Một thay đổi cục bộ sẽ làm lệch các index mà thao tác sau đó từ server trỏ tới. Cứ đọc collection thoải mái; package tự áp các thao tác của server.

Instance phía client bị thay đổi trước khi message spawn của nó được áp sẽ mất thay đổi đó, vì nội dung trong message spawn thay thế nó.

## Host mode <a href="#host-mode" id="host-mode"></a>

Trên host, collection dùng chung với server, nên client của host không áp thao tác lên nó. Để báo giá trị trước đó trong callback, client của host giữ một bản sao riêng của mỗi collection và áp thao tác lên bản sao đó.

## Khôi phục <a href="#recovery" id="recovery"></a>

Client không áp được một thao tác, ví dụ index vượt quá cuối, key không có hoặc byte không decode được, sẽ đánh dấu collection đó lệch nhịp. Nó bỏ qua các thao tác tiếp theo cho collection đó, xin server toàn bộ nội dung, và thay collection khi nội dung tới. Callback sau đó chạy một lần với `Reset`. Các collection khác và state model không bị ảnh hưởng. Khi chính message không đọc được, client không biết nó dành cho collection nào, nên mọi collection của behaviour đó khôi phục theo cách này.

## Cấu hình <a href="#configuration" id="configuration"></a>

| Quy tắc | Khi vi phạm |
|---|---|
| Mỗi index dùng một lần trong một behaviour | `HandlerRegistrationException`: `... uses collection index 1 twice` |
| Mỗi instance collection đăng ký một lần | `HandlerRegistrationException`: `... uses as collection 2 an instance that is already collection 1 of a behaviour` |
| Phần tử model đi kèm adapter; key và phần tử set là kiểu nguyên thuỷ | `HandlerRegistrationException`: `... which is not a primitive type; a model needs its codec, and keys and set elements must be primitive` |
| Chỉ server thay đổi collection đã spawn | `InvalidOperationException`: `... cannot change collection 0 on a client; only the server changes a collection` |
| Không có phần tử, value hay key `null` | `ArgumentNullException` |
| Hai phía đăng ký cùng index, loại và kiểu phần tử | Client dừng với `ObjectMismatch` (`InvalidSpawn`) |

## Giới hạn <a href="#limitations" id="limitations"></a>

Chỉ server thay đổi collection. Một behaviour có nhiều nhất 256 collection, mỗi cái một index `byte`. Toàn bộ collection đi trong message spawn, nên collection rất lớn làm mọi lần spawn object của nó lớn theo. Thứ tự duyệt một dictionary hay một set không được đảm bảo giống nhau giữa server và client.

Collection được đăng ký trong một [NetworkBehaviour](../objects/network-behaviour.md), và phần tử model được khai báo như mọi [model](../messaging/models.md) khác.
