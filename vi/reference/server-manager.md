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
| `ConnectionState PeerState(ulong peerId)` | Trạng thái của một peer; `Stopped` khi không biết |
| `void Disconnect(ulong peerId)` | Đóng kết nối của một peer ngay lập tức với `StopReason.LocalStop` |
| `bool Kick(ulong peerId)` | Gửi các message đã xếp và một thông báo cho client, rồi đóng kết nối; client dừng với `ServerClosed` và không kết nối lại. Trả false khi peer không tồn tại hoặc đang bị đóng. |
| `bool Transfer(ulong peerId, string address, ushort port, ReadOnlyMemory<byte> ticket)` | Gửi các message đã xếp, rồi địa chỉ, port và vé của server khác, rồi đóng kết nối như `Kick`; peer dừng với `Transferred`. Trả false khi peer không tồn tại, đang bị đóng hoặc chưa `Started`. Ném `ArgumentNullException` khi địa chỉ là null và `InvalidOperationException` với client chính của host. Xem [chuyển server](../connections/transfer.md). |
| `bool Transfer(ulong peerId, string address, ushort port, ReadOnlyMemory<byte> ticket, ReadOnlyMemory<byte> connection)` | Như trên, và gửi vé kết nối mà client cần cho server mới dùng [UDP mã hóa](../connections/transports/encrypted-udp.md#server-transfers) |
| `bool HasRtt(ulong peerId)`, `TimeSpan RttOf(ulong peerId)` | Round-trip time mà các clock ping của peer báo; `TimeSpan.Zero` khi chưa có |
| `int DroppedInputsOf(ulong peerId)` | Số input từ peer đã bị bỏ |
| `int FrameBudgetOf(ulong peerId)` | Frame budget của transport của peer; 0 khi không biết |
| `IServerAuthenticator Authenticator` | Phía server của [bước xác thực](../connections/authentication.md). Đọc và ghi; đặt khi server đang chạy sẽ ném `InvalidOperationException`. |

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
