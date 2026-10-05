# Xử lý sự cố

Trang này sắp xếp theo triệu chứng. Mỗi mục đi qua các bước kiểm tra theo thứ tự và trích nguyên văn thông báo mà package log hoặc ném ra, để bạn tìm trên trang theo đúng dòng chữ mình thấy. Danh sách đầy đủ các lý do dừng và loại mismatch nằm trong [lỗi và lý do dừng](../tham-chieu/errors.md).

## Sinh code thất bại <a href="#code-generation-fails" id="code-generation-fails"></a>

Lỗi sinh code xuất hiện trong Console với tiền tố `[Fomoxa]`.

| Thông báo                                                                       | Nguyên nhân và cách sửa                                                                                                                                                   |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `the fomoxac binary for this editor platform is missing`                        | Editor chạy trên nền tảng không có `fomoxac` đi kèm. Chỉ Windows x64 và Linux x64 có binary.                                                                              |
| `no FomoxaSettings asset; create one with Assets > Create > Fomoxa > Settings`  | Tạo settings asset, xem [cài đặt](installation.md#create-the-settings-asset).                                                                                             |
| `more than one FomoxaSettings asset exists; keep exactly one`                   | Xóa asset thừa.                                                                                                                                                           |
| `the FomoxaSettings asset needs both a models folder and a generated folder`    | Điền cả hai field của settings asset.                                                                                                                                     |
| `fomoxac generate exited with ...`                                              | `fomoxac` từ chối một model hoặc một đường dẫn. Phần còn lại của thông báo là output của chính `fomoxac`. Nguyên nhân hay gặp là thiếu thư mục model; hãy tạo thư mục đó. |
| `... was not written by com.fomoxa.unity; remove it ...`                        | Một file do package quản lý, như `fomoxa.toml` hoặc một file trong `FomoxaSystemModels`, lại do người khác ghi. Xóa file đó và sinh lại.                                  |
| `the field type ... is neither a model nor a Unity type com.fomoxa.unity knows` | Một field của model dùng type không có codec. Xem [codec tùy chỉnh](../nang-cao/custom-codecs.md).                                                                        |

## NetworkManager ném exception khi scene khởi động <a href="#networkmanager-throws-when-the-scene-starts" id="networkmanager-throws-when-the-scene-starts"></a>

Exception có nội dung `no Fomoxa schema is registered; FomoxaAdapters.RegisterAll has not run`, hoặc `no ... codec is registered; FomoxaAdapters.RegisterAll has not run`.

1. Kiểm tra Generated Folder có `FomoxaAdapters.cs` và `FomoxaUnityRegistration.cs`; nếu không, chạy Tools > Fomoxa > Generate.
2. Kiểm tra project biên dịch được. Việc đăng ký chạy từ code sinh ra, nên một lỗi biên dịch ở bất kỳ đâu cũng chặn nó.
3. Nếu bạn tự gán `NetworkManager.Registry`, hãy gọi `FomoxaAdapters.RegisterAll(registry)` đã sinh trên registry đó trước.

## Client không kết nối được <a href="#client-cannot-connect" id="client-cannot-connect"></a>

`OnClientConnectionState` của client báo `Stopped` kèm một `Reason`, và `WillRetry` cho biết client có thử lại hay không. Hãy kiểm tra lần lượt theo thứ tự sau.

1. Server đang chạy, tức `ServerManager.State` của nó là `Started`.
2. Client dùng địa chỉ của máy chạy server. `127.0.0.1` chỉ tới được server trên cùng máy.
3. Port của client là port mà server báo trong `ServerManager.Port`.
4. Hai bên dùng cùng một transport. Client UDP không tới được listener TCP hay WebSocket, và server có [`MultiNetworkTransport`](../transport/multi-transport.md) lắng nghe trên port riêng cho mỗi transport.
5. Firewall cho phép giao thức của transport, UDP hoặc TCP, đi qua port của server.
6. Nếu `Reason` là `HandshakeFailed`, nó đi kèm một `Failure` giúp thu hẹp nguyên nhân.
   * `SchemaConflict` nghĩa là client và server được build từ các model khác nhau. Sinh code một lần và build cả hai từ cùng một trạng thái project.
   * `VersionMismatch` nghĩa là hai bên dùng phiên bản giao thức Fomoxa khác nhau, ví dụ vì được build bằng hai phiên bản package khác nhau.
   * `Timeout` nghĩa là handshake không xong trong Handshake Timeout Seconds. Với UDP, server không tới được cũng có thể biểu hiện như vậy, vì UDP không có bước kết nối trước handshake.
7. `Reason` là `TransportError` nghĩa là chính transport thất bại, ví dụ kết nối TCP bị từ chối hoặc host name không phân giải được. Log sẽ cho biết là trường hợp nào.

Client không thử lại sau `LocalStop`, `HandlerException`, `PrefabMismatch`, `ObjectMismatch`, `PhysicsBackendMismatch`, hoặc `HandshakeFailed` với failure khác `Timeout`. `PhysicsBackendMismatch` nghĩa là field Physics Backend khác nhau giữa `NetworkManager` của server và của client.

## Client kết nối được rồi dừng với PrefabMismatch hoặc ObjectMismatch <a href="#client-connects-then-stops-with-prefabmismatch-or-objectmismatch" id="client-connects-then-stops-with-prefabmismatch-or-objectmismatch"></a>

Trong trường hợp này client log `Fomoxa stopped the client: object mismatch <kind>, object <id>, prefab 0x..., scene object 0x...`, và loại mismatch cho biết cần kiểm tra gì.

| Loại                                                                 | Kiểm tra                                                                                                                                                        |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UnknownPrefab`                                                      | Client không có prefab nào mang prefab id đó. Gán Collected Prefabs cho `NetworkManager` của client, và build client với server từ cùng một trạng thái project. |
| `IncompatiblePrefab`                                                 | Prefab có tồn tại nhưng danh sách component `NetworkBehaviour` của nó khác nhau giữa server và client. Build lại cả hai.                                        |
| `UnknownSceneObject`                                                 | Scene của client không có object nào mang scene object id đó. Lưu scene sau khi thêm `NetworkObject` vào, rồi build lại.                                        |
| `IncompatibleSceneObject`                                            | Danh sách `NetworkBehaviour` của scene object khác nhau giữa hai bản build.                                                                                     |
| `UnknownScene`                                                       | Client không load được một network scene mà server yêu cầu. Kiểm tra scene có trong bản build và trong Collected Scenes.                                        |
| `InvalidSpawn`, `InvalidMessage`, `DuplicateObject`, `UnknownObject` | Client nhận một object message mà nó không áp dụng được, ví dụ state ban đầu không decode được. Kiểm tra hai bên chạy cùng một bản build.                       |

## Object không được spawn <a href="#object-does-not-spawn" id="object-does-not-spawn"></a>

Bắt đầu kiểm tra từ server.

1. Code chỉ gọi `ServerManager.Spawn` sau khi server đã khởi động; trước đó lời gọi ném `the server is not started`.
2. Tham số là một instance trong scene. Truyền asset prefab sẽ ném `<name> is a prefab asset; spawn an instance of it`.
3. Prefab đã được đăng ký. `prefab id 0x... of <name> is not registered` nghĩa là prefab không có trong Collected Prefabs lẫn danh sách Prefabs của `NetworkManager`; xem bước 5 của [project đầu tiên](first-project.md).
4. Prefab có prefab id. Prefab có Prefab Id bằng 0 không đăng ký được, nên hãy chạy Tools > Fomoxa > Assign Prefab Ids.
5. Owner là một client đang kết nối. `owner <id> is not a started peer` nghĩa là không phải vậy; truyền 0 cho object không có owner.

Nếu server đã spawn object nhưng một client không hiện nó, hãy kiểm tra tiếp trên client.

1. Client chỉ nhận object mà nó observe. Kiểm tra field Visibility của object, Observer Rule của `NetworkManager`, và `ServerManager.IsObserver(networkObject, peerId)`. Với [`DistanceRule`](../core/observers.md#distancerule), peer không sở hữu object nào sẽ không observe gì ngoài những gì nó sở hữu.
2. Object trong một network scene chỉ tới các peer đã load scene đó.
3. Nếu client đã dừng vì mismatch, xem mục trước.

## RPC không có tác dụng <a href="#rpc-does-nothing" id="rpc-does-nothing"></a>

1. Nếu server log `Fomoxa dropped server RPC 0x... to object <id> from peer <id>, which does not own the object`, bên gọi không phải owner. Hãy gọi RPC từ client của owner, hoặc đặt `RequireOwnership = false`.
2. `<name> is not spawned on the server` hoặc `on the client` nghĩa là object chưa được spawn ở phía gửi.
3. `<Type>.<Method> has no generated parameterless RPC model; mark the method with [NetworkRpc] and run Tools > Fomoxa > Generate` nghĩa là thiếu model đã sinh. Để việc sinh code chạy xong rồi thử lại.
4. Lỗi biên dịch `FOMOXA001` tới `FOMOXA010` mô tả khai báo RPC sai; xem [RPC](../messaging/rpc.md#compile-errors).
5. RPC có model dùng channel của model đó, mặc định là unreliable trừ khi model khai báo `[NetworkChannel(..., Channel.ReliableOrdered)]`, và RPC unreliable có thể bị mất.
6. `SendTargetRpc` trả về `SendResult.NotObserver` khi peer đích không observe object.

## State không cập nhật <a href="#state-does-not-update" id="state-does-not-update"></a>

1. Chỉ server gửi state. Thay đổi trên client chỉ nằm ở client đó và bị lần thay đổi tiếp theo từ server ghi đè.
2. Lỗi đăng ký được ném dưới dạng `HandlerRegistrationException` khi object spawn. Nguyên nhân là state model không nằm trên channel reliable-ordered, state model encode ra không byte nào, hoặc một behaviour đăng ký nhiều hơn một state model.
3. `onChanged` chỉ chạy cho các thay đổi sau khi spawn. Giá trị ban đầu đã có sẵn trong `OnStartClient` và không kích hoạt callback.

## Object từ xa bị giật, trễ hoặc không di chuyển <a href="#remote-objects-jitter-lag-or-do-not-move" id="remote-objects-jitter-lag-or-do-not-move"></a>

1. Prefab cần có `NetworkTransform`.
2. Chuyển động nhỏ hơn ngưỡng vị trí, góc xoay hoặc tỉ lệ sẽ không được gửi cho tới khi object dừng lại.
3. Client hiển thị object từ xa chậm Interpolation Ticks so với vị trí mới nhất. Giảm giá trị này để bớt trễ, hoặc tăng lên để chuyển động mượt hơn trên mạng hay mất gói.
4. `Rigidbody` hoặc `Rigidbody2D` dynamic trên client vẫn tự mô phỏng trừ khi bật Simulate Physics. Khi bật, client biến các body mà nó không dự đoán thành body kinematic đi theo `NetworkTransform`; xem [physics](../physics/overview.md).

## Prediction liên tục bị sửa <a href="#prediction-keeps-correcting" id="prediction-keeps-correcting"></a>

Mỗi lần client sửa một lần dự đoán, nó gọi `OnReconciled` và tăng `NetworkBehaviour.ReconcileCount`. Nếu số này cứ tăng trong khi người chơi không làm gì đặc biệt, client và server đang tính ra kết quả khác nhau.

1. `apply` phải di chuyển theo `TimeManager.TickDelta`, không bao giờ theo `Time.deltaTime`.
2. Input theo frame, như một lần bấm nút, phải được lưu trong `Update` và đọc trong `gather`, để lần bấm ngắn không bị mất.
3. `apply` chỉ được đọc input, state của chính behaviour và độ dài tick. Đọc object khác, thời gian frame hoặc số ngẫu nhiên không có seed sẽ làm hai bên khác nhau.
4. Khi có physics, Simulate Physics phải được bật để package step và rollback physics theo tick. Dù vậy, rollback physics của Unity vẫn chỉ gần đúng; xem [rollback](../prediction/rollback.md).
5. Reconcile model phải chứa mọi thứ `apply` phụ thuộc vào. Một giá trị được mang từ tick này sang tick sau, như vận tốc damping, phải nằm trong đó.
6. Không có hàm `matches`, package so sánh chính xác các byte đã encode, nên nhiễu số thực cũng bị tính là mismatch. Hãy truyền một hàm `matches` có dung sai.

Input mà server không dùng được cũng gây ra việc sửa. Input tới quá muộn hoặc quá sớm sẽ bị bỏ, server lặp lại input cuối cho tick đó, và `ServerManager.DroppedInputsOf(peerId)` đếm các trường hợp này.

Thông báo `<Type> registers an input model, but its NetworkManager uses the Variable timing mode; prediction needs the Tick timing mode` nghĩa là field Timing Mode phải đặt là Tick.

## Cảnh báo về message bị bỏ <a href="#warnings-about-dropped-messages" id="warnings-about-dropped-messages"></a>

`Fomoxa dropped message 0x... (N bytes) to peer <id>: TooLarge` nghĩa là một message đơn lẻ không vừa transport. `Fomoxa dropped N received bytes from peer <id>: a message bundle, or a model in it, could not be read` nghĩa là một bundle nhận được không decode được. Cả hai cảnh báo được log mặc định và có thể tắt bằng Log Send Dropped và Log Receive Dropped, còn [debug](../nang-cao/debugging.md) chỉ cách subscribe vào chính các event này.

## Bản build WebGL không kết nối được <a href="#webgl-build-fails-to-connect" id="webgl-build-fails-to-connect"></a>

`UdpNetworkTransport cannot run in a browser` hoặc `TcpNetworkTransport cannot run in a browser` nghĩa là bản build dùng sai transport: build WebGL cần `WebSocketNetworkTransport`, dùng riêng hoặc đặt trong `MultiNetworkTransport`. `a server cannot listen in a browser; WebGL builds are clients only` nghĩa là bản build đã cố khởi động server hoặc host, điều mà build WebGL không làm được. Xem [WebGL](../unity/webgl.md).
