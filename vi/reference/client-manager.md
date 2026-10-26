# Tham chiếu ClientManager

`public sealed class ClientManager` trong `Fomoxa.Networking` không có constructor public; bạn truy cập nó qua `NetworkManager.ClientManager`. Hướng dẫn [client](../connections/client.md) giải thích cách dùng nó.

## Kết nối <a href="#connection" id="connection"></a>

| Member | Mô tả |
|---|---|
| `void StartConnection(string address, ushort port)` | Kết nối tới server. Khi cùng manager đang chạy server, kết nối qua kết nối trong tiến trình và bỏ qua cả hai tham số. Ném `InvalidOperationException` khi đang chạy, và trên transport cần vé kết nối. |
| `void StartConnection(string address, ushort port, ReadOnlyMemory<byte> connection)` | Kết nối bằng vé kết nối từ `ConnectTokens.Issue` trên [UDP mã hóa](../connections/transports/encrypted-udp.md#on-the-client); các lần thử lại dùng lại vé. Client chính của host bỏ qua nó. Ném `ArgumentException` khi transport không nhận vé hoặc các byte không phải là vé. |
| `void StopConnection()` | Gửi message rời đi, đóng kết nối, despawn các object của client và hủy các lần thử lại đang chờ |
| `ConnectionState State` | `Stopped`, `Starting`, `Authenticating` hoặc `Started` |
| `IClientAuthenticator Authenticator` | Phía client của [bước xác thực](../connections/authentication.md). Đọc và ghi; đặt khi client đang chạy sẽ ném `InvalidOperationException`. |
| `TimeSpan Rtt` | Round-trip time đã làm mượt tới server; bằng 0 với client của host và trước câu trả lời clock đầu tiên |

## Object và prediction <a href="#objects-and-prediction" id="objects-and-prediction"></a>

| Member | Mô tả |
|---|---|
| `IReadOnlyDictionary<uint, INetworkEntity> Spawned` | Các object đã spawn trên client này, theo object id; trong Unity mỗi giá trị là một `NetworkObject` |
| `bool IsReplaying` | True khi client đang replay input trong lúc reconciliation |

## Message <a href="#messages" id="messages"></a>

| Member | Mô tả |
|---|---|
| `SendResult Send(uint messageId, ReadOnlySpan<byte> payload)` | Đưa một message gửi tới server vào queue; `NotConnected` khi đã dừng. Trước `Started`, message chờ trong queue. |
| `SendResult SendToObject(uint messageId, uint objectId, byte behaviourIndex, ReadOnlySpan<byte> body)` | Đưa một object message gửi tới server vào queue |
| `MessageDispatcher Dispatcher` | Handler cho message tới |

## Event <a href="#events" id="events"></a>

| Event | Tham số |
|---|---|
| `OnClientConnectionState` | `ConnectionStateArgs`, kể cả `WillRetry` |
| `OnSendDropped` | `SendDroppedArgs` |
| `OnReceiveDropped` | `ReceiveDroppedArgs` |
| `OnHandlerException` | `HandlerExceptionArgs`; được log khi không ai subscribe |
| `OnObjectMismatch` | `ObjectMismatchArgs`; được log khi không ai subscribe |
| `OnTransferring` | `TransferringArgs`; server chuyển client sang server khác. Xem [chuyển server](../connections/transfer.md). |

[Event và callback](callbacks.md) mô tả các tham số event.

## Kết nối lại <a href="#reconnection" id="reconnection"></a>

Việc kết nối lại được cấu hình trên `NetworkManager` bằng Max Reconnect Retries và Reconnect Interval Seconds. Client không thử lại sau `LocalStop`, `HandlerException`, `PrefabMismatch`, `ObjectMismatch`, `PhysicsBackendMismatch`, `InvalidFragment`, `ServerClosed`, hoặc `HandshakeFailed` với failure khác `Timeout`, và không bao giờ thử lại kết nối trong tiến trình của host. Sau `Transferred`, nó kết nối ngay tới server được chuyển tới, và các lần thử lại sau đó cũng đi tới đó, trừ khi vé kết nối của lần chuyển không hợp với transport; khi đó `WillRetry` là false.

Các type liên quan là [NetworkManager](network-manager.md), [ServerManager](server-manager.md) và [TimeManager](time-manager.md).
