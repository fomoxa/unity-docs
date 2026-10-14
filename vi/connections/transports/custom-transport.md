# Transport tùy chỉnh

Transport tùy chỉnh nối package với một cách chuyển byte khác, như một dịch vụ relay, SDK của một nền tảng hoặc một đường truyền trong bộ nhớ cho test. Nó là một component `NetworkTransport` tạo ra một `ITransportFactory`, và cả phần còn lại của package lẫn code game đều không phải thay đổi.

## Các thành phần <a href="#the-pieces" id="the-pieces"></a>

| Type | Namespace | Vai trò |
|---|---|---|
| `NetworkTransport` | `Fomoxa.Unity` | Component trên `NetworkManager`; `CreateFactory()` trả về factory |
| `ITransportFactory` | `Fomoxa.Networking.Transports` | `FrameBudget`, `CreateListener(port, out boundPort)`, `CreateConnector(address, port)` |
| `ITransportConnector` | `Fomoxa.Networking.Transports` | Một lần thử kết nối. `Poll(out ITransport)` trả về `Pending`, `Connected` hoặc `Failed`; `Dispose()` hủy nó |
| `IListenerTransport` | `Fomoxa.Net.Transports` | Phía server. `Accept()` trả về một `AcceptOutcome`; `Dispose()` đóng nó |
| `ITransport` | `Fomoxa.Net.Transports` | Một kết nối: `Kind`, `Send`, `Receive`, `CloseGracefully`, `Dispose` |

## Quy tắc <a href="#rules" id="rules"></a>

Quy tắc chính là không bao giờ chặn. Package gọi mọi method từ main thread, mỗi tick, và chờ câu trả lời ngay lập tức. Do đó `Poll` trả về `Pending` cho tới khi kết nối sẵn sàng, `Receive` trả về `ReceiveOutcome.WouldBlock` khi chưa có gì tới, và `Send` trả về `SendOutcome.WouldBlock` khi chưa nhận được byte ngay lúc đó. `Accept` trả về `AcceptOutcome.Pending` khi không có ai chờ, `Accepted(transport)` cho một kết nối mới, `Progress` khi có tiến triển nhưng chưa có kết nối, và `Error` khi thất bại.

`Kind` là `TransportKind.Message` khi mỗi `Send` tới thành đúng một `Receive`, như với datagram và message WebSocket, và là `TransportKind.Stream` khi byte tới dưới dạng stream, như với TCP.

Ngoài `WouldBlock`, `Receive(buffer)` trả về `ReceiveOutcome.NeedCapacity(size)` khi message tiếp theo không vừa buffer, `Ok(count)` với số byte đã copy, `Closed` sau khi phía bên kia đóng kết nối đúng cách, và `Error` khi thất bại. `Send` trả về `SendOutcome.TooLarge` với byte không bao giờ gửi được, `Closed` sau khi kết nối đã đóng, và `Error` khi thất bại.

`FrameBudget` là frame lớn nhất package nên dựng. Hãy dùng kích thước mà đường truyền của bạn mang được mà không phải chia nhỏ, hoặc `FomoxaWire.MaxDataFrameSize` cho đường truyền không có giới hạn thực tế.

## Ví dụ: transport trong bộ nhớ <a href="#example-an-in-memory-transport" id="example-an-in-memory-transport"></a>

Transport sau nối client với server trong cùng tiến trình qua các type loopback của package, và cho thấy hình dạng của từng thành phần.

```csharp
using Fomoxa.Net;
using Fomoxa.Net.Transports;
using Fomoxa.Networking.Transports;
using Fomoxa.Unity;

public sealed class InMemoryNetworkTransport : NetworkTransport
{
    private InMemoryTransportFactory factory;

    public override ITransportFactory CreateFactory() => factory ??= new InMemoryTransportFactory();

    private sealed class InMemoryTransportFactory : ITransportFactory
    {
        private LoopbackListener network;

        public int FrameBudget => FomoxaWire.MaxDataFrameSize;

        public IListenerTransport CreateListener(ushort port, out ushort boundPort)
        {
            boundPort = port;
            network = new LoopbackListener(64);
            return network;
        }

        public ITransportConnector CreateConnector(string address, ushort port) => new InMemoryConnector(this);

        private sealed class InMemoryConnector : ITransportConnector
        {
            private readonly InMemoryTransportFactory owner;

            public InMemoryConnector(InMemoryTransportFactory owner)
            {
                this.owner = owner;
            }

            public ConnectStatus Poll(out ITransport transport)
            {
                transport = owner.network?.Connect();
                return transport == null ? ConnectStatus.Failed : ConnectStatus.Connected;
            }

            public void Dispose()
            {
            }
        }
    }
}
```

Component trả về cùng một instance factory ở mọi lần gọi, nên server và client dùng chung nó, và hai component `NetworkManager` dùng cùng một component `InMemoryNetworkTransport` sẽ kết nối với nhau.

## Bản build cho trình duyệt <a href="#browser-builds" id="browser-builds"></a>

Transport không chạy được trong trình duyệt nên ném `PlatformNotSupportedException` từ `CreateFactory` trong player WebGL, vì `MultiNetworkTransport` bỏ qua các mục ném exception này trong trình duyệt.

[Tổng quan transport](README.md) mô tả cách factory gắn vào `NetworkManager`, và [loopback](loopback.md) mô tả các type trong bộ nhớ dùng trong ví dụ.
