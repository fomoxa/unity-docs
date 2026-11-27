# NetworkBehaviour

`NetworkBehaviour` là base class cho các script networking. Nó là một `MonoBehaviour` thuộc về `NetworkObject` trên chính GameObject của nó hoặc trên một object cha, và cung cấp cho script các callback vòng đời phía server và client. RPC, state và input được khai báo trên nó bằng attribute.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class Door : NetworkBehaviour
{
    public override void OnStartServer()
    {
        Debug.Log($"door {NetworkObject.ObjectId} spawned on the server");
    }

    public override void OnStartClient()
    {
        Debug.Log($"door {NetworkObject.ObjectId} appeared on this client");
    }

    [ServerRpc(RequireOwnership = false)]
    private void Knock(ulong peerId)
    {
        Debug.Log($"peer {peerId} knocked");
        SendPlayKnockObserversRpc();
    }

    [ClientRpc]
    private void PlayKnock()
    {
        GetComponent<AudioSource>().Play();
    }

    public void RequestKnock() => SendKnockServerRpc();
}
```

Class khai báo RPC, state hoặc input phải là `partial`, và mọi class chứa nó cũng vậy, vì package sinh code đăng ký chúng và các method gửi của RPC.

## Callback vòng đời <a href="#lifecycle-callbacks" id="lifecycle-callbacks"></a>

Override các callback sau để phản ứng với vòng đời network của object:

| Callback | Chạy |
|---|---|
| `OnStartServer()` | Trên server, sau khi object được spawn |
| `OnStopServer()` | Trên server, trước khi object bị despawn |
| `OnStartClient()` | Trên client, sau khi object xuất hiện và state ban đầu đã được áp dụng |
| `OnStopClient()` | Trên client, trước khi object biến mất |
| `OnOwnerChangedServer(ulong previousOwnerId)` | Trên server, sau khi owner thay đổi |
| `OnOwnerChangedClient(ulong previousOwnerId)` | Trên mọi client đang observe, sau khi owner thay đổi |
| `OnSceneChangedServer(NetworkScene previous, NetworkScene current)` | Trên server, sau khi object [chuyển](scenes.md#move-an-object-to-another-instance) sang bản khác |
| `OnSceneChangedClient(NetworkScene previous, NetworkScene current)` | Trên mọi client observe object ở cả hai bản, sau khi lệnh chuyển tới |
| `OnHostVisibility(bool visible)` | Trên host, khi client của nó thôi hoặc bắt đầu observe object; xem [host mode](../connections/host-mode.md) |
| `OnReconciled(uint tick)` | Trên client của owner, sau một lần sửa từ state của server tại `tick`; xem [reconciliation](../prediction/reconciliation.md) |

[Vòng đời](../concepts/lifecycle.md) cho thấy thứ tự chạy của chúng.

## Khai báo <a href="#declarations" id="declarations"></a>

| Khai báo | Bằng | Hướng dẫn |
|---|---|---|
| RPC | `[ServerRpc]` và `[ClientRpc]` trên method | [RPC](../messaging/rpc.md) |
| State | `[NetworkState]` trên field | [State](../synchronization/state.md) |
| Collection | `[NetworkState(Index = n)]` trên field collection `readonly` | [Collection](../synchronization/collections.md) |
| Input và state được dự đoán | `[NetworkInput]` và `[NetworkReconcile]` trên field | [Input](../prediction/input.md), [reconciliation](../prediction/reconciliation.md) |

Package đăng ký chúng một lần cho mỗi instance component, ở lần đầu object của nó spawn trên server hoặc trên client, trước `OnStartServer` hoặc `OnStartClient`.

Behaviour có field `[NetworkInput]` override các method điền và đọc chúng:

| Method | Chạy khi |
|---|---|
| `OnGatherInput()` | Trên client của owner, mỗi tick một lần; ghi các field input ở đây |
| `OnApplyInput(InputContext context)` | Trên server và trên client đang dự đoán, sau khi các field input đã được ghi; mô phỏng từ chúng ở đây |
| `OnCaptureState()` | Trước khi các field `[NetworkReconcile]` được chép; không bắt buộc |
| `OnRestoreState()` | Sau khi các field `[NetworkReconcile]` đã được khôi phục từ server; không bắt buộc |

## Gửi RPC <a href="#sending-rpcs" id="sending-rpcs"></a>

Với mỗi RPC, package sinh các method gửi `protected`, đặt theo tên RPC:

| Method | Phía | Gửi tới | Trả về |
|---|---|---|---|
| `Send<Method>ServerRpc(...)` | Client | Server | `SendResult` |
| `Send<Method>ObserversRpc(...)` | Server | Mọi observer của object | Số peer đã được đưa vào queue |
| `Send<Method>TargetRpc(peerId, ...)` | Server | Một observer | `SendResult`, `NotObserver` khi peer không observe |

Chúng gọi `SendServerRpc`, `SendObserversRpc` và `SendTargetRpc`, các method nhận tên RPC và cũng là `protected`; [RPC](../messaging/rpc.md#sending-by-name) mô tả chúng. Khi object chưa spawn ở phía gửi, các method gửi ném `InvalidOperationException` với `<name> is not spawned on the server` hoặc `on the client`.

## Property <a href="#properties" id="properties"></a>

| Property | Ý nghĩa |
|---|---|
| `NetworkObject` | Object mà behaviour này thuộc về. Null cho tới lần đầu object spawn. |
| `BehaviourIndex` | Vị trí của behaviour trong `NetworkObject.Behaviours` |
| `IsPredicting` | True trên client của owner khi nó đang dự đoán behaviour này |
| `IsReplaying` | True trên client khi nó đang replay input trong lúc reconciliation |
| `ReconcileCount` | Số lần sửa behaviour này kể từ khi nó được tạo |

## Giới hạn <a href="#limitations" id="limitations"></a>

Một behaviour có một state model, gồm mọi field state của nó, tối đa 256 [collection](../synchronization/collections.md) và một input model; object cần nhiều hơn thì dùng nhiều behaviour. Vì việc đăng ký chạy một lần cho mỗi instance component, scene object bị despawn rồi spawn lại vẫn giữ lần đăng ký đầu tiên.

Behaviour thuộc về một [NetworkObject](network-object.md). Các hướng dẫn về [RPC](../messaging/rpc.md), [state](../synchronization/state.md) và [input](../prediction/input.md) giải thích từng loại khai báo, và [tham chiếu NetworkBehaviour](../reference/network-object.md#networkbehaviour) liệt kê mọi member.
