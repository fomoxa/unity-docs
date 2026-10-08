# Bước 01: Nền tảng network

## Mục tiêu <a href="#goal" id="goal"></a>

Bước này thêm `com.fomoxa.networking` vào Red Runner, thiết lập sinh code và đặt một `NetworkManager` vào `Play.unity`. Game vẫn chơi như trước, vì chưa có gì mở kết nối.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

[Game offline](../offline-baseline.md) ở commit gốc `2b675b5`, được lưu bằng Unity 6000.2.6f2.

## Vấn đề <a href="#problem" id="problem"></a>

Package cần Unity 6000.5 trở lên, còn project đang ở phiên bản cũ hơn. Package cũng sinh codec cho mọi network message từ các class C#, nên trước khi code networking nào biên dịch được, project cần một chỗ cho các class đó và cho code được sinh. Cuối cùng, scene list trong build ghi một scene không tồn tại, và package lấy network scene từ danh sách đó.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Cài đặt](../../../getting-started/installation.md)
- [Model và codec](../../../messaging/models.md)
- [Tích hợp Editor](../../../unity/editor-integration.md)
- [NetworkManager](../../../core/network-manager.md)
- [UDP](../../../transports/udp.md)

## Thiết kế <a href="#design" id="design"></a>

Mọi code networking nằm dưới `Assets/Scripts/RedRunner/Networking`, cạnh các thư mục của chính game. Model nằm trong `Networking/Models` và code sinh ra trong `Networking/Generated`, nên namespace được sinh là `Generated`. Một object `Network Manager` duy nhất ở gốc `Play.unity` mang `NetworkManager` và một `UdpNetworkTransport`.

## File <a href="#files" id="files"></a>

```
Packages/manifest.json
Packages/packages-lock.json
ProjectSettings/ProjectVersion.txt
ProjectSettings/EditorBuildSettings.asset
Assets/Scenes/Play.unity
Assets/Scripts/RedRunner/Networking/FomoxaSettings.asset
Assets/Scripts/RedRunner/Networking/Models/.gitkeep
Assets/Scripts/RedRunner/Networking/Generated/
FomoxaSystemModels/
.fomoxa/
fomoxa.toml
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Nâng cấp project <a href="#upgrade-the-project" id="upgrade-the-project"></a>

Mở project bằng Unity 6000.5 trở lên và chấp nhận nâng cấp. Package Manager chuyển các package Unity trong `Packages/manifest.json` sang phiên bản đi kèm Editor của bạn, và `ProjectSettings/ProjectVersion.txt` ghi phiên bản mới; bản port dùng 6000.5.7f1. Nếu muốn tách việc nâng cấp khỏi phần networking, hãy commit nó riêng.

### Thêm package <a href="#add-the-package" id="add-the-package"></a>

Mở Window > Package Manager, bấm +, chọn Install package from git URL và nhập:

```
https://github.com/fomoxa/com.fomoxa.networking.git
```

Package phụ thuộc vào các module có sẵn Physics, Physics 2D và Animation, những module Red Runner đã dùng.

### Tạo settings asset <a href="#create-the-settings-asset" id="create-the-settings-asset"></a>

1. Tạo các thư mục `Assets/Scripts/RedRunner/Networking/Models` và `Assets/Scripts/RedRunner/Networking/Generated`.
2. Bấm chuột phải vào `Assets/Scripts/RedRunner/Networking` và chọn Create > Fomoxa > Settings.
3. Đặt Models Folder thành `Assets/Scripts/RedRunner/Networking/Models` và Generated Folder thành `Assets/Scripts/RedRunner/Networking/Generated`.
4. Thêm một file `.gitkeep` trống vào thư mục model. Thư mục này trống cho tới bước 02, và `fomoxac` dừng lại khi thiếu thư mục nguồn.

Sau lần biên dịch tiếp theo, package ghi `fomoxa.toml`, `FomoxaSystemModels/`, `.fomoxa/` và thư mục code sinh ra, mỗi thứ đều được [cài đặt](../../../getting-started/installation.md#generate-the-code) mô tả. Hãy commit tất cả.

### Sửa scene list của build <a href="#fix-the-build-scene-list" id="fix-the-build-scene-list"></a>

Mở File > Build Profiles, xóa `Assets/Scenes/Gooose.unity` không tồn tại khỏi Scene List và thêm `Assets/Scenes/Play.unity`. Package làm mới `Generated/FomoxaSceneList.asset` từ danh sách này, như mô tả trong [network scene](../../../core/scenes.md#scene-ids).

### Thêm NetworkManager <a href="#add-the-networkmanager" id="add-the-networkmanager"></a>

Trong `Play.unity`, tạo một GameObject trống ở gốc tên `Network Manager` và thêm:

1. `UdpNetworkTransport`.
2. `NetworkManager`, với `UdpNetworkTransport` trong field Transport.

Tạm thời giữ các field khác ở mặc định; bước 03 đổi tick rate, bật physics simulation và điền Collected Prefabs và Collected Scenes. `NetworkManager` không làm gì cho tới khi code gọi `ServerManager.StartConnection` hoặc `ClientManager.StartConnection`, nên game vẫn chơi như trước.

## Test <a href="#test" id="test"></a>

Để test thiết lập, thêm một component tạm vào scene, component này khởi động server trên manager của scene, tạo manager thứ hai làm client và kết nối nó:

```csharp
server.ServerManager.StartConnection(0);
var clientObject = new GameObject("Check Client");
clientObject.AddComponent<UdpNetworkTransport>();
NetworkManager client = clientObject.AddComponent<NetworkManager>();
client.ClientManager.StartConnection("127.0.0.1", server.ServerManager.Port);
```

Port 0 để hệ điều hành chọn một port trống, rồi `ServerManager.Port` báo port đó. Bài kiểm tra riêng của bản port cho bước này là `Tools/PortChecks/ConnectionCheck.cs`.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Console không có lỗi nào bắt đầu bằng `[Fomoxa]`.
- `Generated/` chứa `NetSchema.cs`, `FomoxaAdapters.cs` và một adapter cho mỗi system model.
- Vài frame sau khi test bắt đầu, `client.ClientManager.State` là `ConnectionState.Started` và `server.ServerManager.PeerCount` là 1.
- Không có component test, game chơi như bản offline.

## Commit <a href="#commit" id="commit"></a>

```
Commit: 8983a5a
Message: Install com.fomoxa.unity and add a NetworkManager to the Play scene
```

Xem [`8983a5a`](https://github.com/fomoxa/RedRunner/commit/8983a5ae2105e4ce79b8b127c9e5564147707eb1) trên GitHub, rồi tiếp tục với [bước 02: level dùng chung](step-02-shared-level.md).
