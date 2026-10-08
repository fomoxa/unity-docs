# NetworkBehaviour

`NetworkBehaviour` là base class cho các script networking. Nó là một `MonoBehaviour` thuộc về `NetworkObject` trên chính GameObject của nó hoặc trên một object cha, và cung cấp cho script các callback vòng đời phía server và client cùng những chỗ để đăng ký RPC, state và input.

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
        SendObserversRpc(nameof(PlayKnock));
    }

    [ClientRpc]
    private void PlayKnock()
    {
        GetComponent<AudioSource>().Play();
    }

    public void RequestKnock() => SendServerRpc(nameof(Knock));
}
```

Class khai báo RPC bằng attribute phải là `partial`, và mọi class chứa nó cũng vậy, vì package sinh code đăng ký các RPC đó.

## Callback vòng đời <a href="#lifecycle-callbacks" id="lifecycle-callbacks"></a>

Override các callback sau để phản ứng với vòng đời network của object:

| Callback                                      | Chạy                                                                                                                         |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `OnStartServer()`                             | Trên server, sau khi object được spawn                                                                                       |
| `OnStopServer()`                              | Trên server, trước khi object bị despawn                                                                                     |
| `OnStartClient()`                             | Trên client, sau khi object xuất hiện và state ban đầu đã được áp dụng                                                       |
| `OnStopClient()`                              | Trên client, trước khi object biến mất                                                                                       |
| `OnOwnerChangedServer(ulong previousOwnerId)` | Trên server, sau khi owner thay đổi                                                                                          |
| `OnOwnerChangedClient(ulong previousOwnerId)` | Trên mọi client đang observe, sau khi owner thay đổi                                                                         |
| `OnHostVisibility(bool visible)`              | Trên host, khi client của nó thôi hoặc bắt đầu observe object; xem [host mode](host-mode.md)                                 |
| `OnReconciled(uint tick)`                     | Trên client của owner, sau một lần sửa từ state của server tại `tick`; xem [reconciliation](../prediction/reconciliation.md) |

[Vòng đời](../khai-niem/lifecycle.md) cho thấy thứ tự chạy của chúng.

## Hook đăng ký <a href="#registration-hooks" id="registration-hooks"></a>

Package gọi các hook này một lần cho mỗi instance component, ở lần đầu object của nó spawn trên server hoặc trên client, trước `OnStartServer` hoặc `OnStartClient`:

| Hook                                  | Đăng ký gì                                   | Hướng dẫn                                      |
| ------------------------------------- | -------------------------------------------- | ---------------------------------------------- |
| `OnRegisterRpcs(NetworkRpcs rpc)`     | Các RPC handler viết tay                     | [RPC](../messaging/rpc.md#registering-by-hand) |
| `OnRegisterState(NetworkState state)` | State model của behaviour                    | [State](../dong-bo/state.md)                   |
| `OnRegisterInput(NetworkInput input)` | Input model và reconcile model của behaviour | [Input](../prediction/input.md)                |

## Gửi RPC <a href="#sending-rpcs" id="sending-rpcs"></a>

| Method                                   | Phía   | Gửi tới                 | Trả về                                             |
| ---------------------------------------- | ------ | ----------------------- | -------------------------------------------------- |
| `SendServerRpc<T>(codec, value)`         | Client | Server                  | `SendResult`                                       |
| `SendServerRpc(rpcName)`                 | Client | Server                  | `SendResult`                                       |
| `SendObserversRpc<T>(codec, value)`      | Server | Mọi observer của object | Số peer đã được đưa vào queue                      |
| `SendObserversRpc(rpcName)`              | Server | Mọi observer của object | Số peer                                            |
| `SendTargetRpc<T>(peerId, codec, value)` | Server | Một observer            | `SendResult`, `NotObserver` khi peer không observe |
| `SendTargetRpc(peerId, rpcName)`         | Server | Một observer            | `SendResult`                                       |

Các method này là `protected`. Khi object chưa spawn ở phía gửi, chúng ném `InvalidOperationException` với `<name> is not spawned on the server` hoặc `on the client`.

## Property <a href="#properties" id="properties"></a>

| Property         | Ý nghĩa                                                              |
| ---------------- | -------------------------------------------------------------------- |
| `NetworkObject`  | Object mà behaviour này thuộc về. Null cho tới lần đầu object spawn. |
| `BehaviourIndex` | Vị trí của behaviour trong `NetworkObject.Behaviours`                |
| `IsPredicting`   | True trên client của owner khi nó đang dự đoán behaviour này         |
| `IsReplaying`    | True trên client khi nó đang replay input trong lúc reconciliation   |
| `ReconcileCount` | Số lần sửa behaviour này kể từ khi nó được tạo                       |

## Giới hạn <a href="#limitations" id="limitations"></a>

Một behaviour đăng ký được một state model và một input model; object cần nhiều hơn thì dùng nhiều behaviour. Ở mỗi phía, một message id thuộc về một type behaviour, nên dùng cùng một model làm server RPC của hai type behaviour, hoặc vừa làm RPC vừa làm state model, sẽ ném `HandlerRegistrationException` khi object thứ hai spawn. Vì các hook đăng ký chạy một lần cho mỗi instance component, scene object bị despawn rồi spawn lại vẫn giữ lần đăng ký đầu tiên.

Behaviour thuộc về một [NetworkObject](network-object.md). Các hướng dẫn về [RPC](../messaging/rpc.md), [state](../dong-bo/state.md) và [input](../prediction/input.md) giải thích cần đăng ký gì trong mỗi hook, và [tham chiếu NetworkBehaviour](../tham-chieu/network-object.md#networkbehaviour) liệt kê mọi member.
