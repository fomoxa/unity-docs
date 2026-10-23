# Thuật ngữ

| Thuật ngữ | Ý nghĩa |
|---|---|
| Adapter | `IMessageCodec<T>` được sinh cho một model và một codec, như `ShotNetAdapter`. Xem [model](../messaging/models.md). |
| Authoritative state | Kết quả của server cho một tick, gửi tới owner để reconciliation. |
| Behaviour index | Vị trí của một `NetworkBehaviour` trong danh sách behaviour của object; message tới object mang giá trị này. |
| Bundle | Một frame của transport chứa nhiều message. |
| Channel | `Unreliable` hoặc `ReliableOrdered`; đặt theo từng message id. Xem [channel](../messaging/channels.md). |
| Codec | Một cách encode model có tên, do `fomoxac` sinh. Một model có thể có nhiều codec. |
| Delta | XOR giữa bản encode mới và bản encode trước của một state, với các đoạn không đổi được nén lại. |
| Fingerprint | Hash của danh sách type `NetworkBehaviour` của một prefab hoặc scene object, được so sánh khi spawn. |
| Fragment | Một mảnh của message `ReliableOrdered` lớn hơn frame budget. Bên nhận ghép các mảnh lại rồi mới giao message. Xem [kích thước message](../messaging/channels.md#message-size). |
| Frame budget | Frame lớn nhất package dựng cho một transport: 1200 byte với UDP. |
| Host | Tiến trình chạy server và client trong cùng một `NetworkManager`. Xem [host mode](../connections/host-mode.md). |
| Input model | Model mà một behaviour đăng ký bằng `NetworkInput.Use`, được owner gửi mỗi tick. |
| Interpolation | Hiển thị một object ở xa nằm giữa các transform đã nhận, chậm vài tick so với hiện tại. |
| Tầng 1 | `Fomoxa.Networking`, tức Core: phần của package không tham chiếu Unity. |
| Tầng 2 | `Fomoxa.Unity`, phần tích hợp với Unity. |
| Message id | Id 32 bit của một model và một codec trong schema. |
| Model | Một class C# đánh dấu bằng `[Network]` mô tả một message. |
| Network scene | Scene mà server load theo kiểu additive trên chính nó và trên các peer được chọn. Xem [network scene](../objects/scenes.md). |
| `NetworkObject` | Một GameObject tồn tại trên mạng, có object id và owner. |
| Object id | Id mà server gán cho một `NetworkObject` khi nó spawn. |
| Observer | Một peer nhận một object. Xem [observer](../objects/observers.md). |
| Owner | Peer mà object thuộc về; 0 với server. |
| Peer id | Id của một client đang kết nối trên server; không bao giờ bằng 0. |
| Prediction | Áp dụng input của owner trên client của nó trước khi server xác nhận. |
| Prediction tick | Tick mà input của client dành cho, đi trước tick của server. |
| Prefab id | Id 32 bit của một prefab, suy ra từ asset GUID trừ khi được đặt tường minh. |
| Proxy | Trên client, body kinematic của một object mà client không dự đoán, được đặt ở vị trí đã replicate. |
| Reconcile model | Model mà một behaviour đăng ký bằng `NetworkInput.Reconcile`, được so sánh sau mỗi tick. |
| Reconciliation | So sánh authoritative state với dự đoán và sửa khi không khớp. |
| Replay | Áp dụng lại input đã ghi sau một lần sửa. Không phải bản ghi trận đấu. |
| Rollback | Khôi phục một state trước đó, của một behaviour hoặc của các physics world, trước khi replay. |
| Rollback group | Các physics world được rollback cùng nhau. Xem [rollback](../prediction/rollback.md#rollback-groups). |
| Scene id | Id 32 bit của một scene, suy ra từ asset GUID của nó. |
| Scene object | Một `NetworkObject` đặt trong scene, nhận diện bằng scene object id. |
| Schema | Danh sách mọi message id và layout của chúng, được sinh thành `NetSchema`; được so sánh trong lúc handshake. |
| Settle | Message reliable mà `NetworkTransform` gửi khi object dừng, spawn hoặc teleport. |
| State model | Model mà một behaviour đăng ký bằng `NetworkState.Use`, được server giữ đồng bộ. |
| System model | Một trong các model của chính package, như `ObjectSpawn`. |
| Tick | Một bước cố định của mô phỏng network. Xem [tick và thời gian](../concepts/tick.md). |
| World | Một physics scene của Unity, 3D hoặc 2D, nhìn qua `IPhysicsWorld` hoặc `IPhysicsWorld2D`. |
