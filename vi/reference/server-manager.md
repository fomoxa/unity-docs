# Tham chiếu ServerManager

`public sealed class ServerManager` trong `Fomoxa.Networking` không có constructor public; bạn truy cập nó qua `NetworkManager.ServerManager`. Hướng dẫn [server](../connections/server.md) giải thích cách dùng nó.

## Kết nối <a href="#connection" id="connection"></a>

| Member | Mô tả |
|---|---|
| `void StartConnection(ushort port)` | Mở listener của transport và listener trong tiến trình, rồi spawn các scene object của các scene đã load. Port 0 chọn một port trống. Ném `InvalidOperationException` khi đang chạy, `PlatformNotSupportedException` trong trình duyệt. |
| `void StopConnection()` | Ngắt mọi peer, despawn mọi object, unload các network scene |
| `ServerState State` | `Stopped`, `Starting`, `Started` hoặc `Stopping` |
| `ushort Port` | Port đã bind; 0 khi đã dừng |
| `int PeerCount` | Số peer đã kết nối, kể cả peer chưa khởi động xong |
| `PeerIds StartedPeers` | Id của các peer ở `Started`, tức các peer mà `Broadcast` gửi tới; xem [danh sách peer](#the-peer-list) |
| `ConnectionState PeerState(ulong peerId)` | Trạng thái của một peer; `Stopped` khi không biết |
| `void Disconnect(ulong peerId)` | Đóng kết nối của một peer ngay lập tức với `StopReason.LocalStop` |
| `bool Kick(ulong peerId)` | Gửi các message đã xếp và một thông báo cho client, rồi đóng kết nối; client dừng với `ServerClosed` và không kết nối lại. Trả false khi peer không tồn tại hoặc đang bị đóng. |
| `bool Transfer(ulong peerId, string address, ushort port, ReadOnlyMemory<byte> ticket)` | Gửi các message đã xếp, rồi địa chỉ, port và vé của server khác, rồi đóng kết nối như `Kick`; peer dừng với `Transferred`. Trả false khi peer không tồn tại, đang bị đóng hoặc chưa `Started`. Ném `ArgumentNullException` khi địa chỉ là null và `InvalidOperationException` với client chính của host. Xem [chuyển server](../connections/transfer.md). |
| `bool Transfer(ulong peerId, string address, ushort port, ReadOnlyMemory<byte> ticket, ReadOnlyMemory<byte> connection)` | Như trên, và gửi vé kết nối mà client cần cho server mới dùng [UDP mã hóa](../connections/transports/encrypted-udp.md#server-transfers) |
| `bool HasRtt(ulong peerId)`, `TimeSpan RttOf(ulong peerId)` | Round-trip time mà các clock ping của peer báo; `TimeSpan.Zero` khi chưa có |
| `int DroppedInputsOf(ulong peerId)` | Số input từ peer đã bị bỏ |
| `long DroppedInputs` | Số input bị bỏ của mọi peer kể từ khi server được tạo, kể cả peer đã rời |
| `ServerTrafficStatistics Statistics` | [Bộ đếm lưu lượng](../advanced/debugging.md#traffic-counters) của mọi peer, với `Of(peerId)` cho một peer; `null` khi Collect Statistics tắt |
| `int FrameBudgetOf(ulong peerId)` | Frame budget của transport của peer; 0 khi không biết |
| `IServerAuthenticator Authenticator` | Phía server của [bước xác thực](../connections/authentication.md). Đọc và ghi; đặt khi server đang chạy sẽ ném `InvalidOperationException`. |

### Danh sách peer <a href="#the-peer-list" id="the-peer-list"></a>

`StartedPeers` là một `PeerIds` trong `Fomoxa.Networking.Sessions`, một `IReadOnlyCollection<ulong>` có `Count` và `Contains(ulong peerId)`. Một peer vào danh sách khi tới `Started`, và rời danh sách ngay tại lời gọi kick, chuyển server hay từ chối nó, hoặc khi nó dừng. `foreach` trên danh sách không cấp phát.

Danh sách là danh sách sống. Khi nó đổi trong lúc một vòng lặp đang duyệt, bước kế tiếp của vòng lặp ném `InvalidOperationException`, như `Dictionary`. Muốn kick hay chuyển server cho peer trong một vòng lặp thì chép danh sách ra trước:

```csharp
foreach (ulong peerId in new List<ulong>(manager.ServerManager.StartedPeers))
{
    manager.ServerManager.Kick(peerId);
}
```

## Object <a href="#objects" id="objects"></a>

| Member | Mô tả |
|---|---|
| `void Spawn(INetworkEntity networkObject, ulong ownerId = 0)` | Spawn một instance. Ném `ArgumentNullException`, `InvalidOperationException` khi server chưa khởi động, `ArgumentException` với asset prefab, object đã spawn, prefab id chưa đăng ký, scene object không hợp lệ hoặc owner không phải peer đã khởi động. |
| `bool Despawn(INetworkEntity networkObject)` | Despawn và hủy một instance, hoặc tắt một scene object. False khi server này không spawn object đó. |
| `bool ChangeOwner(INetworkEntity networkObject, ulong ownerId)` | Đổi owner; 0 cho server. False khi server này không spawn object đó hoặc owner không phải peer đã khởi động. |
| `IReadOnlyDictionary<uint, INetworkEntity> Spawned` | Các object đã spawn theo object id |

## Observer <a href="#observers" id="observers"></a>

| Member | Mô tả |
|---|---|
| `IObserverRule ObserverRule` | Rule cho các object có `Visibility.Rule`, thường là một asset `ObserverRule`. Đọc và ghi. |
| `int ObserverInterval` | Số tick mà sau đó mọi object được tính lại một lần. Tối thiểu 1. |
| `ObserverGroups Groups` | Các [nhóm](../objects/observers.md#groups) peer và object |
| `bool IsObserver(INetworkEntity networkObject, ulong peerId)` | Peer có observe object hay không |
| `bool RebuildObservers(INetworkEntity networkObject)` | Tính lại một object cho mọi peer |
| `void RebuildObserversOfPeer(ulong peerId)` | Tính lại mọi object cho một peer |
| `void RebuildObservers()` | Tính lại mọi object cho mọi peer |

`NetworkObject` hiện thực `INetworkEntity`, nên bạn truyền một `NetworkObject` vào các method này. Gọi một method spawn, despawn, đổi owner, dựng lại observer hoặc đổi nhóm từ bên trong `ObserverRule.Observes` sẽ ném exception.

### ObserverGroups <a href="#observergroups" id="observergroups"></a>

`public sealed class ObserverGroups`, lấy qua `ServerManager.Groups`. Id nhóm là một `uint` bất kỳ. Mỗi method đổi nhóm tính lại các cặp bị ảnh hưởng và xếp hàng spawn, despawn của chúng trước khi trả về.

| Member | Mô tả |
|---|---|
| `void Add(uint groupId, ulong peerId)` | Thêm peer vào nhóm. Nếu peer đã khởi động, tính lại các object đã spawn của nhóm cho peer đó. |
| `bool Remove(uint groupId, ulong peerId)` | Bỏ peer khỏi nhóm và tính lại các cặp đó. False khi peer không ở trong nhóm. |
| `void Add(uint groupId, INetworkEntity networkObject)` | Thêm object vào nhóm. Nếu server này đã spawn nó, tính lại nó cho mọi peer. Ném `ArgumentNullException` với null. |
| `bool Remove(uint groupId, INetworkEntity networkObject)` | Bỏ object khỏi nhóm và tính lại nó theo cùng cách. False khi object không ở trong nhóm. Ném `ArgumentNullException` với null. |
| `bool Contains(uint groupId, ulong peerId)` | Peer có ở trong nhóm hay không |
| `bool Contains(uint groupId, INetworkEntity networkObject)` | Object có ở trong nhóm hay không |

Peer rời mọi nhóm của nó khi ngắt kết nối, object rời mọi nhóm của nó khi bị despawn, và dừng server sẽ xoá mọi nhóm.

## Scene <a href="#scenes" id="scenes"></a>

Property `Scenes` trả về một `NetworkScenes`, type trong `Fomoxa.Networking` có các member sau. `NetworkScene` là một readonly struct trong `Fomoxa.Networking` chỉ một bản đã load; `Id` là giá trị thô, và `default` nghĩa là không có network scene. `ScenePhysics` là enum có `Shared` và `Own`.

| Member | Mô tả |
|---|---|
| `IReadOnlyList<NetworkScene> LoadGlobal(IReadOnlyList<uint> sceneIds, bool replace = false, ScenePhysics physics = ScenePhysics.Shared)` | Load scene cho mọi peer và trả về các bản global, mỗi id một bản; asset đã có bản global thì trả về bản đó. `replace` unload các bản global hiện tại trước. Ném exception với id chưa đăng ký. |
| `void UnloadGlobal(IReadOnlyList<NetworkScene> scenes)` | Unload các bản global. Ném exception với bản không phải global. |
| `NetworkScene Load(uint sceneId, IReadOnlyList<ulong> peerIds, ScenePhysics physics = ScenePhysics.Shared)` | Tạo một bản mới cho một số peer, có thể không có peer nào. Ném exception với id chưa đăng ký. |
| `int AddPeers(NetworkScene scene, IReadOnlyList<ulong> peerIds)` | Giao một bản theo peer cho thêm peer; trả về số peer đã thêm |
| `int RemovePeers(NetworkScene scene, IReadOnlyList<ulong> peerIds)` | Gỡ một bản theo peer khỏi một số peer; trả về số peer đã gỡ. Bản vẫn được load. |
| `void Unload(NetworkScene scene)` | Unload một bản theo peer khỏi các peer của nó và khỏi server |
| `IReadOnlyList<NetworkScene> Global` | Các bản global |
| `bool Contains(NetworkScene scene)`, `bool IsGlobal(NetworkScene scene)` | Bản có tồn tại không, và có phải global không |
| `bool HasLoaded(ulong peerId, NetworkScene scene)` | Peer đã báo load xong bản hay chưa |
| `IReadOnlyCollection<ulong> PeersOf(NetworkScene scene)` | Các peer có bản |
| `IReadOnlyList<NetworkScene> ScenesOf(ulong peerId)` | Các bản mà peer có |
| `IReadOnlyList<NetworkScene> InstancesOf(uint sceneId)` | Các bản của một scene asset |
| `uint SceneIdOf(NetworkScene scene)` | Scene id của một bản; 0 khi bản không tồn tại |
| `bool TryGetScene(NetworkScene scene, out Scene unityScene)` | `Scene` mà server đã load cho bản; một extension method trong `Fomoxa.Unity` |
| `bool TryGetNetworkScene(Scene unityScene, out NetworkScene scene)` | Bản mà một `Scene` server đã load thuộc về; false với scene khác; một extension method trong `Fomoxa.Unity` |
| `event Action<NetworkScene> OnLoaded` | Server đã load xong một bản |
| `event Action<NetworkScene, Exception> OnLoadFailed` | Server không load được một bản |
| `event Action<NetworkScene> OnUnloaded` | Server đã unload xong một bản |
| `event Action<ulong, NetworkScene> OnPeerLoaded` | Một peer đã báo load xong một bản |

Bản không tồn tại, hoặc bản sai loại với lời gọi, ném `ArgumentException`. Bản `Shared` thứ hai của một scene asset ném `ArgumentException`; hãy cho nó `ScenePhysics.Own`. Các method về scene ném `InvalidOperationException` khi server đã dừng.

## Message <a href="#messages" id="messages"></a>

| Member | Mô tả |
|---|---|
| `SendResult Send(ulong peerId, uint messageId, ReadOnlySpan<byte> payload)` | Đưa một message cho một peer vào queue |
| `SendResult Send<T>(ulong peerId, IMessageCodec<T> codec, T value)` | Encode giá trị bằng codec rồi đưa vào queue cho một peer |
| `SendResult SendToObject(ulong peerId, uint messageId, uint objectId, byte behaviourIndex, ReadOnlySpan<byte> body)` | Đưa một object message cho một peer vào queue |
| `int Broadcast(uint messageId, ReadOnlySpan<byte> payload)` | Đưa một message cho mọi peer đã khởi động vào queue; trả về số peer |
| `int Broadcast<T>(IMessageCodec<T> codec, T value)` | Encode giá trị một lần rồi đưa vào queue cho mọi peer đã khởi động; trả về số peer |
| `MessageDispatcher Dispatcher` | Handler cho message tới |

Hai method generic ném `ArgumentNullException` khi codec null.

## Event <a href="#events" id="events"></a>

| Event | Tham số |
|---|---|
| `OnServerConnectionState` | `ServerConnectionStateArgs` |
| `OnRemoteConnectionState` | `ConnectionStateArgs` |
| `OnSendDropped` | `SendDroppedArgs` |
| `OnReceiveDropped` | `ReceiveDroppedArgs` |
| `OnHandlerException` | `HandlerExceptionArgs`; được log khi không ai subscribe; đặt `Disconnect` thành `false` để giữ peer |
| `OnInputRejected` | `InputRejectedArgs`; input từ peer không sở hữu object; được log khi không ai subscribe |
| `OnServerRpcRejected` | `ServerRpcRejectedArgs`; server RPC có `RequireOwnership` từ peer không sở hữu object; được log khi không ai subscribe |

[Event và callback](callbacks.md) mô tả các tham số event.

Các type liên quan là [NetworkManager](network-manager.md), [ClientManager](client-manager.md) và [NetworkObject](network-object.md).
