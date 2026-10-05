# Observer

Observer của một object là client nhận object đó. Với mỗi object đã spawn, server giữ tập các peer observe nó. Peer vào tập sẽ nhận message spawn của object, peer rời tập sẽ nhận despawn, còn state, cập nhật transform và RPC tới observer chỉ đi tới các peer trong tập.

Giới hạn observer giúp tiết kiệm băng thông và giữ thông tin khỏi những client không nên có nó, như kẻ địch sau bức tường hay quân của đội khác.

## Ai observe một object <a href="#who-observes-an-object" id="who-observes-an-object"></a>

Với mỗi peer đã khởi động và mỗi object, server quyết định qua ba bước.

1. Object trong một network scene chỉ được observe bởi các peer đã load scene đó.
2. Owner observe các object của chính nó.
3. Với mọi peer khác, field Visibility của object quyết định. Với `Everyone`, mọi peer observe object, còn với `OwnerOnly` thì chỉ owner. Với `Rule`, giá trị mặc định, `ObserverRule` của `NetworkManager` quyết định, và nếu không có rule thì mọi peer observe object.

## ObserverRule <a href="#observerrule" id="observerrule"></a>

Observer rule là một `ScriptableObject` trả lời câu hỏi một peer cụ thể có observe một object cụ thể hay không:

```csharp
using Fomoxa.Unity;
using UnityEngine;

[CreateAssetMenu(menuName = "Game/Team Rule")]
public sealed class TeamRule : ObserverRule
{
    public override bool Observes(NetworkObject networkObject, ulong peerId)
    {
        Team team = networkObject.GetComponent<Team>();
        return team == null || team.IsVisibleTo(peerId);
    }
}
```

`Team` ở đây là một component của riêng bạn. Tạo một asset của rule và gán nó vào field Observer Rule của `NetworkManager`.

`Observes` chỉ chạy trên server. Nó không được spawn, despawn, đổi owner hay dựng lại observer, và các lời gọi đó sẽ ném exception khi server đang quyết định. Nếu `Observes` ném exception, exception được log và câu trả lời được tính là "không observe".

## DistanceRule <a href="#distancerule" id="distancerule"></a>

`DistanceRule` là rule có sẵn trong package, tạo bằng Assets > Create > Fomoxa > Distance Rule. Một peer observe một object khi object nằm trong Radius (mặc định 50 đơn vị) tính từ bất kỳ object nào peer đó sở hữu, đo giữa vị trí world của các transform. Component `ObserverRange` trên một object thay Radius cho riêng object đó, ví dụ để một tòa nhà cao có bán kính lớn hơn.

Peer không sở hữu object nào sẽ không observe gì qua rule này, nên hãy spawn player của peer trước khi muốn nó thấy thế giới. Ngay khi một peer có object sở hữu đầu tiên, server dựng lại observer cho peer đó.

## Khi nào observer được tính lại <a href="#when-observers-are-recalculated" id="when-observers-are-recalculated"></a>

Vì vị trí liên tục thay đổi, server tính lại observer liên tục. Mỗi tick nó xử lý một phần các object, sao cho mỗi object được tính lại một lần sau mỗi Observer Interval tick (mặc định 15), tức hai lần mỗi giây ở 30 tick mỗi giây.

Khi một điều kiện mà rule dựa vào thay đổi, bạn có thể tính lại ngay thay vì chờ:

| Method | Tính lại |
|---|---|
| `ServerManager.RebuildObservers(networkObject)` | Một object cho mọi peer. Trả về false khi server này không spawn object đó. |
| `ServerManager.RebuildObserversOfPeer(peerId)` | Mọi object cho một peer |
| `ServerManager.RebuildObservers()` | Mọi object cho mọi peer |

`ServerManager.IsObserver(networkObject, peerId)` cho biết một peer hiện có observe một object hay không.

## Host mode <a href="#host-mode" id="host-mode"></a>

Client của host là một peer như mọi peer khác và chỉ observe những gì rule cho phép. Object mà nó không observe vẫn tồn tại trong tiến trình của host vì server cần chúng, nhưng package ẩn renderer của chúng, như mô tả trong [host mode](host-mode.md).

Field Visibility được đặt trên [NetworkObject](network-object.md), [network scene](scenes.md) giải thích bước scene trong việc quyết định, và [tham chiếu ServerManager](../reference/server-manager.md) liệt kê các member về observer.
