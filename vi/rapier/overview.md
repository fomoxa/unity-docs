# Rapier physics

`com.fomoxa.networking.rapier` là một physics backend xây trên [Rapier](https://rapier.rs). Nó thay `RigidbodyPhysics` trên `NetworkManager`, để network object được mô phỏng trong các world của Rapier thay cho PhysX và Box2D của Unity. Đây là một package riêng trong repository [networking-rapier](https://github.com/fomoxa/networking-rapier), và game đã hài lòng với physics của Unity thì không cần nó.

| | |
|---|---|
| Package | `com.fomoxa.networking.rapier` 0.1.0 |
| Yêu cầu | `com.fomoxa.networking` 0.1.0 |
| Unity | 6000.5 trở lên |
| Nền tảng | Windows x64 và Linux x64: Editor, bản build player và server console |
| Rapier | `rapier3d` và `rapier2d` 0.36.0, build với `enhanced-determinism` |
| Giấy phép | Apache-2.0; Rapier và các crate được link khác liệt kê trong `Third Party Notices.md` |

## Khi nào nên dùng <a href="#when-to-use-it" id="when-to-use-it"></a>

Rollback với `RigidbodyPhysics` chỉ gần đúng. PhysX và Box2D không lưu được dữ liệu contact, nên một lần replay bắt đầu từ tick đã lưu có thể lệch khỏi lần chạy đầu, và client phải sửa lần nữa. [Rollback với physics](../prediction/rollback.md) mô tả chi tiết điều này.

Snapshot của Rapier giữ cả world, kể cả contact, nên replay sau `Load` cho ra đúng các tick như lần chạy đầu. Rapier được ghim một phiên bản và build với `enhanced-determinism`, và cùng các bước cho cùng một state trên Windows và Linux, dưới Mono và dưới .NET. Nhờ đó có hai điều:

- Việc sửa chỉ xảy ra khi input hoặc state của server thật sự khác với prediction của client.
- Một [server console](../console-server/overview.md) chạy không cần Unity có thể mô phỏng cùng physics với client Unity, vì cả hai dựng world từ cùng scene file và cùng mô tả body.

Rapier còn báo body nào vừa di chuyển ở mỗi bước. Server chỉ đọc transform của một network object khi nó đổi, nên object đứng yên không tốn lần đọc transform nào của server. Với `RigidbodyPhysics`, mọi `NetworkTransform` được đọc sau mỗi tick, như mô tả ở [NetworkTransform](../synchronization/transform.md#server-behavior).

## Nó nằm ở đâu <a href="#how-it-fits-in" id="how-it-fits-in"></a>

<figure><img src="../.gitbook/assets/diagrams/rapier-stack.svg" alt="Trong client hoặc server Unity, code game với apply, capture, restore và OnTick dùng PhysicsBody và PhysicsBody2D, không đổi, và chúng dùng RapierPhysics, một world mỗi network scene và mỗi chiều. Trong console server không có Unity, chương trình console của bạn với các class EntityBehaviour và cùng model dùng RapierScenes, dựng cùng các world từ cùng scene file. Cả hai nằm trên thư viện native fomoxa_rapier, build từ rapier3d và rapier2d 0.36.0 với enhanced-determinism. Snapshot chứa toàn bộ world Rapier, kể cả contact, nên replay cho ra đúng các tick như lần chạy đầu."><figcaption><p>Code game giữ nguyên; chỉ các tầng bên dưới PhysicsBody thay đổi.</p></figcaption></figure>

Code game vẫn dùng `PhysicsBody` và `PhysicsBody2D`, model input và reconcile, và các component contact. Phần thay đổi nằm bên dưới:

| | `RigidbodyPhysics` | `RapierPhysics` |
|---|---|---|
| Engine | PhysX và Box2D, qua Unity | Rapier, qua một thư viện native |
| World | Một cho mỗi physics scene của Unity | Một cho mỗi network scene và mỗi chiều |
| Geometry tĩnh | Các collider trong scene Unity | Scene file của network scene, cộng các nhóm thêm lúc chạy |
| Snapshot | Chỉ body dynamic, không có contact | Cả world, kể cả contact |
| `Rigidbody` và `Rigidbody2D` | Unity mô phỏng | Chuyển thành kinematic; Rapier ghi tư thế ngược lại vào `Transform` sau mỗi tick |
| Transform server đọc | Mọi `NetworkTransform`, sau mỗi tick | `NetworkTransform` trên object có body chỉ khi nó đổi, trừ khi bật Sync Scale |
| Bật mô phỏng | Khi tick Simulate Physics | Luôn luôn |
| Server console | Không làm được | Cùng world qua `RapierScenes` |

Server và mọi client phải dùng cùng backend. Client có backend khác với server sẽ dừng với `StopReason.PhysicsBackendMismatch`.

## Giới hạn <a href="#limitations" id="limitations"></a>

- Chỉ Windows x64 và Linux x64. Client macOS, Android, iOS và WebGL chưa dùng được backend này.
- Bản build player IL2CPP chưa được kiểm tra tính tất định so với Mono và .NET.
- Không hỗ trợ joint, effector như `PlatformEffector2D`, thiết lập va chạm liên tục và contact point.
- Mỗi network object một body.

Tiếp tục với [cài đặt](setup.md). [Body và collider](bodies.md) mô tả cách object Unity trở thành body của Rapier, [contact event](contacts.md) mô tả cách các component contact hoạt động, còn [tính tất định](determinism.md) nêu những gì code game phải làm để mô phỏng giống nhau trên mọi máy.
