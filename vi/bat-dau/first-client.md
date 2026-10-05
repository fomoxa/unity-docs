# Client đầu tiên

Trang này kết nối client tới server từ [server đầu tiên](first-server.md), thử RPC Jump và state, rồi cuối cùng chạy game ở host mode.

## Phần client hoạt động thế nào <a href="#how-the-client-part-works" id="how-the-client-part-works"></a>

Nút Client của launcher gọi:

```csharp
manager.ClientManager.StartConnection(address, port);
```

Địa chỉ có thể là host name hoặc địa chỉ IP. Client phân giải địa chỉ, mở transport và chạy handshake Fomoxa, còn `ClientManager.OnClientConnectionState` báo tiến trình: `Starting` khi đang kết nối, `Started` khi message truyền được và `Stopped` khi kết nối kết thúc.

Nếu kết nối thất bại hoặc bị rớt, client thử lại sau mỗi 0.5 giây, mặc định không giới hạn số lần. Với event `Stopped`, `ConnectionStateArgs.Reason` cho biết vì sao kết nối dừng và `ConnectionStateArgs.WillRetry` cho biết có lần thử mới hay không. [Client](../core/client.md) giải thích việc kết nối lại và các thiết lập của nó.

Khi client tới `Started`, server spawn một player cho nó và client tạo instance riêng của prefab `Player`. Các object server đã spawn trước đó, như player của người khác, cũng tới theo cách này.

## 1. Kết nối client tới dedicated server <a href="#id-1-connect-a-client-to-the-dedicated-server" id="id-1-connect-a-client-to-the-dedicated-server"></a>

1. Chạy bản build dedicated server từ trang trước, hoặc vào Play Mode trong một bản copy thứ hai của project và bấm Server.
2. Trong Editor, vào Play Mode, giữ `127.0.0.1` trong ô nhập và bấm Client.

Kết quả mong đợi:

* Console hiện `client: Starting None`, rồi `client: Started None`.
* Một capsule xuất hiện ở tọa độ x bằng hai lần peer id của client.
* Console hiện `player <id> spawned, owner <peer id>, mine: True, jumps: 0`.
* Nút Jump xuất hiện cho capsule mà client này sở hữu.
* Trên dedicated server, `server.log` hiện `peer <id>: Starting None` và `peer <id>: Started None`.

## 2. Gọi RPC <a href="#id-2-call-the-rpc" id="id-2-call-the-rpc"></a>

Bấm Jump. Capsule nhảy lên một đơn vị và Console hiện `player <id> jumps: 0 -> 1`.

Cú bấm đã gửi một server RPC, và server chạy `Jump`, di chuyển transform và thay đổi state. Cuối tick, server gửi vị trí mới qua `NetworkTransform` và state mới qua state model. Client áp dụng cả hai, và việc áp dụng thay đổi state đã gọi `OnStatsChanged`.

## 3. Thêm client thứ hai <a href="#id-3-add-a-second-client" id="id-3-add-a-second-client"></a>

Build lại player, hoặc dùng lại bản build ở trang trước, và chạy nó không có `-server` để nó mở cửa sổ. Bấm Client trong đó.

Lúc này cả hai client sẽ hiện hai capsule, mỗi client có một nút Jump cho capsule mà nó sở hữu. Nhảy trên một client sẽ di chuyển capsule của nó trên cả hai client và log số đếm mới ở cả hai.

## 4. Chạy host <a href="#id-4-run-a-host" id="id-4-run-a-host"></a>

Dừng mọi thứ, rồi vào Play Mode trong Editor và bấm Host. Launcher khởi động server rồi kết nối một client trong cùng tiến trình. Client đó bỏ qua địa chỉ và kết nối qua loopback trong tiến trình thay vì UDP.

Kết quả mong đợi:

* Nhãn hiện `server: Started, peers: 1, client: Started`.
* Một capsule được spawn cho client của chính host, kèm nút Jump.
* Một client ở tiến trình khác có thể kết nối tới host bằng nút Client, giống như với dedicated server.

Ở host mode, server và client của host dùng chung một instance cho mỗi object. [Host mode](../core/host-mode.md) giải thích điều đó ảnh hưởng tới code của bạn ra sao.

## 5. Ngắt kết nối <a href="#id-5-disconnect" id="id-5-disconnect"></a>

Bấm Stop trên một client. Client dừng và các object của nó biến mất, còn server despawn player của client đó với mọi người khác.

## Bạn đã xây được gì <a href="#what-you-built" id="what-you-built"></a>

| Bước                                 | Tính năng                   | Hướng dẫn                                                                |
| ------------------------------------ | --------------------------- | ------------------------------------------------------------------------ |
| Network Manager với transport UDP    | Transport và vòng lặp tick  | [NetworkManager](../core/network-manager.md), [UDP](../transport/udp.md) |
| Model `PlayerStats`                  | Model và codec sinh ra      | [Model và codec](../messaging/models.md)                                 |
| Prefab người chơi có `NetworkObject` | Network object và prefab id | [NetworkObject](../core/network-object.md), [Spawn](../core/spawning.md) |
| `ServerManager.Spawn` với owner      | Spawn và ownership          | [Ownership](../core/ownership.md)                                        |
| `[ServerRpc] Jump`                   | RPC                         | [RPC](../messaging/rpc.md)                                               |
| `state.Use`                          | State                       | [State](../dong-bo/state.md)                                             |
| `NetworkTransform`                   | Replicate transform         | [NetworkTransform](../dong-bo/transform.md)                              |
| Nút Host                             | Host mode                   | [Host mode](../core/host-mode.md)                                        |

Cú nhảy trong hướng dẫn này phải chờ server rồi mới thấy chuyển động. Game di chuyển nhân vật mỗi frame thì để client tự dự đoán nhân vật của mình, như trang [prediction](../prediction/overview.md) hướng dẫn. Nếu có gì trong hướng dẫn không chạy, xem [xử lý sự cố](troubleshooting.md).
