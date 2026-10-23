# Cài đặt

Trang này cài backend Rapier vào một project đã dùng `com.fomoxa.networking` và chuyển `NetworkManager` của nó sang backend đó.

## Cài package <a href="#install-the-package" id="install-the-package"></a>

Package Unity không khai báo được dependency tới một package Git, nên `com.fomoxa.networking` không có trong danh sách dependency của package này, và bạn cài cả hai. Trong Window > Package Manager, bấm +, chọn Install package from git URL rồi lần lượt nhập từng URL:

```
https://github.com/fomoxa/com.fomoxa.networking.git
https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier
```

Backend kiểm tra phiên bản của `com.fomoxa.networking` khi tạo world và ném `com.fomoxa.networking.rapier needs com.fomoxa.networking 0.1.0; the project has ...` nếu project có phiên bản khác.

Package mang thư viện native cho Windows x64 và Linux x64 trong `Runtime/Plugins`, và Unity copy đúng thư viện vào bản build player. Thư viện Linux cần glibc 2.34 trở lên, tức Ubuntu 22.04, Debian 12 và các bản mới hơn.

## Thêm RapierPhysics <a href="#add-rapierphysics" id="add-rapierphysics"></a>

1. Chọn GameObject của `NetworkManager`.
2. Thêm component `RapierPhysics`. Nó phải nằm trên cùng GameObject với `NetworkManager`; nếu không, manager ném `RapierPhysics belongs on the GameObject of the NetworkManager that uses it` khi khởi động.
3. Đặt Gravity nếu game cần giá trị khác (0, -9.81, 0). World 2D dùng X và Y của nó.
4. Kéo component vào field Physics của `NetworkManager`.
5. Gỡ component `RigidbodyPhysics` nếu có.

Làm như vậy cho mọi `NetworkManager` chạy server hoặc client của game. `RapierPhysics` luôn mô phỏng, nên nó không có field Simulate Physics.

## Xuất scene file <a href="#export-the-scene-files" id="export-the-scene-files"></a>

Rapier đọc geometry tĩnh của một scene từ scene file mà package ghi vào Generated Folder, `<scene id>.fomoxascene`. Editor ghi file khi bạn lưu một network scene, trước mỗi lần build player, và khi chọn Tools > Fomoxa > Export Network Scene Files, như mô tả trong [tích hợp Editor](../advanced/editor-integration.md#scene-files). Commit các file này cùng phần code sinh ra còn lại.

Chỉ network scene mới có world. Scene phải nằm trong Scene List của Build Profiles, để có scene id trong `FomoxaSceneList.asset`, và `NetworkManager` phải có danh sách đó trong Collected Scenes. Network scene đã load mà không có scene file sẽ được mô phỏng không có geometry tĩnh, và backend cảnh báo `scene 0x... has no scene file; Rapier simulates it without static geometry. Export the network scene files`.

## Kiểm tra kết quả <a href="#check-the-result" id="check-the-result"></a>

Vào Play Mode ở chế độ host. Console không được có cảnh báo về scene file thiếu, và một network object có `Rigidbody2D` hoặc `Rigidbody` phải rơi xuống và đậu trên các collider tĩnh của scene. `Rigidbody` của nó hiện là kinematic trong Inspector khi manager đang chạy, vì Rapier di chuyển object và ghi tư thế ngược lại vào `Transform`.

Một client vẫn dùng `RigidbodyPhysics` sẽ kết nối rồi dừng với `PhysicsBackendMismatch`, điều đó xác nhận server đang chạy Rapier.

[Body và collider](bodies.md) liệt kê những gì backend biểu diễn được.
