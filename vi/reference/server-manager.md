# Tham chiếu ServerManager

`public sealed class ServerManager` trong `Fomoxa.Networking` không có constructor public; bạn truy cập nó qua `NetworkManager.ServerManager`. Hướng dẫn [server](../connections/server.md) giải thích cách dùng nó.

## Kết nối <a href="#connection" id="connection"></a>

| Member | Mô tả |
|---|---|
| `void StartConnection(ushort port)` | Mở listener của transport và listener trong tiến trình, rồi spawn các scene object của các scene đã load. Port 0 chọn một port trống. Ném `InvalidOperationException` khi đang chạy, `PlatformNotSupportedException` trong trình duyệt. |
| `void StopConnection()` | Ngắt mọi peer, despawn mọi object, unload các network scene |
| `ServerState State` | `Stopped`, `Starting`, `Started` hoặc `Stopping` |
| `ushort Port` | Port đã bind; 0 khi đã dừng |
| `int PeerCount` | Số peer đã kết nối, kể cả peer đang handshake |
| `ConnectionState PeerState(ulong peerId)` | Trạng thái của một peer; `Stopped` khi không biết |
| `void Disconnect(ulong peerId)` | Đóng kết nối của một peer với `StopReason.LocalStop` |
| `bool HasRtt(ulong peerId)`, `TimeSpan RttOf(ulong peerId)` | Round-trip time mà các clock ping của peer báo; `TimeSpan.Zero` khi chưa có |
| `int DroppedInputsOf(ulong peerId)` | Số input từ peer đã bị bỏ |
| `int FrameBudgetOf(ulong peerId)` | Frame budget của transport của peer; 0 khi không biết |

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
| `bool IsObserver(INetworkEntity networkObject, ulong peerId)` | Peer có observe object hay không |
| `bool RebuildObservers(INetworkEntity networkObject)` | Tính lại một object cho mọi peer |
| `void RebuildObserversOfPeer(ulong peerId)` | Tính lại mọi object cho một peer |
| `void RebuildObservers()` | Tính lại mọi object cho mọi peer |

`NetworkObject` hiện thực `INetworkEntity`, nên bạn truyền một `NetworkObject` vào các method này. Gọi một method spawn, despawn, đổi owner hoặc dựng lại observer từ bên trong `ObserverRule.Observes` sẽ ném exception.

## Scene <a href="#scenes" id="scenes"></a>

Property `Scenes` trả về một `NetworkScenes`, type trong `Fomoxa.Networking` có các member sau:

| Member | Mô tả |
|---|---|
| `void LoadGlobal(IReadOnlyList<uint> sceneIds, bool replace = false)` | Load scene cho mọi peer; `replace` unload các global scene hiện tại trước. Ném exception với id chưa đăng ký. |
| `void UnloadGlobal(IReadOnlyList<uint> sceneIds)` | Unload các global scene. Ném exception với id không phải global. |
| `int LoadForPeers(uint sceneId, IReadOnlyList<ulong> peerIds)` | Load một scene cho một số peer; trả về số peer đã thêm. Ném exception với global scene hoặc id chưa đăng ký. |
| `int UnloadForPeers(uint sceneId, IReadOnlyList<ulong> peerIds)` | Gỡ một scene theo peer khỏi một số peer; trả về số peer đã gỡ |
| `void Unload(uint sceneId)` | Gỡ một scene theo peer khỏi mọi peer |
| `IReadOnlyList<uint> Global` | Các global scene id |
| `bool Contains(uint sceneId)`, `bool IsGlobal(uint sceneId)` | Scene có đang được dùng không, và có phải global không |
| `bool HasLoaded(ulong peerId, uint sceneId)` | Peer đã báo load xong scene hay chưa |
| `IReadOnlyCollection<ulong> PeersOf(uint sceneId)` | Các peer có scene |
| `bool TryGetScene(uint sceneId, out Scene scene)` | `Scene` mà server đã load; một extension method trong `Fomoxa.Unity` |
| `event Action<uint> OnLoaded` | Server đã load xong một scene |
| `event Action<uint, Exception> OnLoadFailed` | Server không load được một scene |

Các method về scene ném `InvalidOperationException` khi server đã dừng.

## Message <a href="#messages" id="messages"></a>

| Member | Mô tả |
|---|---|
| `SendResult Send(ulong peerId, uint messageId, ReadOnlySpan<byte> payload)` | Đưa một message cho một peer vào queue |
| `SendResult SendToObject(ulong peerId, uint messageId, uint objectId, byte behaviourIndex, ReadOnlySpan<byte> body)` | Đưa một object message cho một peer vào queue |
| `int Broadcast(uint messageId, ReadOnlySpan<byte> payload)` | Đưa một message cho mọi peer đã khởi động vào queue; trả về số peer |
| `MessageDispatcher Dispatcher` | Handler cho message tới |

## Event <a href="#events" id="events"></a>

| Event | Tham số |
|---|---|
| `OnServerConnectionState` | `ServerConnectionStateArgs` |
| `OnRemoteConnectionState` | `ConnectionStateArgs` |
| `OnSendDropped` | `SendDroppedArgs` |
| `OnReceiveDropped` | `ReceiveDroppedArgs` |
| `OnHandlerException` | `HandlerExceptionArgs`; được log khi không ai subscribe |

[Event và callback](callbacks.md) mô tả các tham số event.

Các type liên quan là [NetworkManager](network-manager.md), [ClientManager](client-manager.md) và [NetworkObject](network-object.md).
