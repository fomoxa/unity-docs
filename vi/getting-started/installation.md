# Cài đặt

Trang này thêm package vào một project Unity và thiết lập việc sinh code. Khi xong, project biên dịch được cùng code sinh ra và sẵn sàng cho [tutorial](tutorial/README.md).

## Yêu cầu <a href="#requirements" id="requirements"></a>

- Unity 6000.5 trở lên.
- Editor Windows x64 hoặc Linux x64. Trình sinh code `fomoxac` chỉ đi kèm cho hai nền tảng này, nên trong Editor trên macOS việc sinh code dừng với `the fomoxac binary for this editor platform is missing`.

Package phụ thuộc vào các module có sẵn Physics, Physics 2D và Animation. Package khai báo chúng là dependency, nên Package Manager tự bật chúng.

## Thêm package <a href="#add-the-package" id="add-the-package"></a>

### Từ Git URL <a href="#from-a-git-url" id="from-a-git-url"></a>

1. Trong Unity, mở **Window > Package Manager**.
2. Bấm nút **+** và chọn **Install package from git URL**.
3. Nhập URL rồi bấm **Install**:

```
https://github.com/fomoxa/com.fomoxa.networking.git
```

Để ghim một phiên bản, thêm branch, tag hoặc commit sau dấu `#`, ví dụ `https://github.com/fomoxa/com.fomoxa.networking.git#<tag>`.

### Từ thư mục cục bộ <a href="#from-a-local-folder" id="from-a-local-folder"></a>

Để làm việc với một bản copy cục bộ, chọn **Install package from disk** trong cùng menu và chọn file `package.json` của package. Package Manager sẽ thêm một mục `file:` vào `Packages/manifest.json`. Bạn cũng có thể tự viết mục đó. Một đường dẫn tương đối với thư mục `Packages` của project chạy được trên mọi máy có cùng cấu trúc thư mục:

```json
"com.fomoxa.networking": "file:../../com.fomoxa.networking"
```

## Tạo settings asset <a href="#create-the-settings-asset" id="create-the-settings-asset"></a>

Package cần biết model của bạn nằm ở đâu và code sinh ra được ghi vào đâu. Cả hai thư mục được đặt trong một asset `FomoxaSettings`.

1. Tạo một thư mục cho model, ví dụ `Assets/Network/Models`, và một thư mục cho code sinh ra, ví dụ `Assets/Network/Generated`.
2. Bấm chuột phải vào một thư mục trong cửa sổ Project và chọn **Create > Fomoxa > Settings**.
3. Chọn asset mới và đặt **Models Folder** và **Generated Folder** trong Inspector.

<figure><img src="../.gitbook/assets/screenshots/fomoxa-settings-inspector.png" alt="Inspector của một asset FomoxaSettings với Models Folder là Assets/Network/Models và Generated Folder là Assets/Network/Generated." width="460"><figcaption><p>Settings asset dùng trong tutorial.</p></figcaption></figure>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Models Folder | `Assets/Models` | Thư mục `fomoxac` đọc model của bạn |
| Generated Folder | `Assets/Generated` | Thư mục package ghi codec, adapter và các danh sách |

Giữ đúng một asset `FomoxaSettings` trong project. Nếu có hai, package log `more than one FomoxaSettings asset exists; keep exactly one` và không sinh gì.

Thư mục model phải tồn tại trước lần sinh code đầu tiên, kể cả khi còn trống, vì `fomoxac` dừng khi thiếu một thư mục nguồn. Git không giữ thư mục trống, nên hãy đặt một file `.gitkeep` trống vào đó. Unity bỏ qua các file có tên bắt đầu bằng dấu chấm.

## Việc sinh code diễn ra thế nào <a href="#how-code-generation-works" id="how-code-generation-works"></a>

Package sinh code sau mỗi lần biên dịch script. Bạn cũng có thể chạy nó bằng **Tools > Fomoxa > Generate**.

<figure><img src="../.gitbook/assets/diagrams/code-generation.svg" alt="Model của bạn, system model của package và RPC model đi vào fomoxac. fomoxac ghi codec, NetSchema.cs, Handshake.cs và Runtime.cs. Sau đó package ghi codec cho type của Unity, adapter, FomoxaAdapters.cs và FomoxaUnityRegistration.cs. Bước prefab và bước scene ghi danh sách prefab và danh sách scene. Khi khởi động, FomoxaUnityRegistration điền FomoxaRegistry.Default, và NetworkManager đọc registry đó trong Awake."><figcaption><p>Một lần sinh code đọc gì, ghi gì, và kết quả đến được NetworkManager như thế nào.</p></figcaption></figure>

Một lần sinh code đi qua các bước sau:

1. Package copy các model của chính nó, như message spawn và message transform, vào `FomoxaSystemModels/` ở thư mục gốc của project, để model của bạn và model của package tạo thành một schema chung.
2. Với mỗi RPC khai báo không có model, package viết một model nhỏ vào `RpcModels/` trong Generated Folder.
3. Package viết `fomoxa.toml` từ settings asset và chạy `fomoxac`. `fomoxac` viết codec cho mọi model, `NetSchema.cs` chứa message id và fingerprint, `Handshake.cs` và `Runtime.cs`.
4. Package viết codec cho các type của Unity mà model của bạn dùng, như `Vector3`, vào `UnityCodecs/`. Thư mục này chỉ xuất hiện khi có model dùng type của Unity.
5. Package viết một adapter cho mỗi codec, `FomoxaAdapters.cs` để đăng ký các adapter đó, và `FomoxaUnityRegistration.cs` để chạy việc đăng ký khi Play Mode hoặc bản build khởi động.

Danh sách prefab và danh sách scene đến từ hai bước riêng, chạy khi bạn lưu một prefab, sửa một scene hoặc danh sách scene trong Build Profiles, và trước mỗi lần build player. [Tutorial](tutorial/project-setup.md#4-make-the-player-prefab) cho thấy lúc nào chúng cần đến. [Tích hợp Editor](../advanced/editor-integration.md) mô tả từng bước và từng file sinh ra.

Bạn không bao giờ tự gọi việc đăng ký. Khi Play Mode hoặc bản build khởi động, `FomoxaUnityRegistration` đăng ký schema và codec vào `FomoxaRegistry.Default`, và mọi `NetworkManager` đọc chúng từ đó trong `Awake`.

## File cần commit <a href="#files-to-commit" id="files-to-commit"></a>

| Đường dẫn | Nội dung |
|---|---|
| `fomoxa.toml` | Cấu hình của `fomoxac`, viết từ settings asset. Hãy sửa asset, không sửa file này. |
| `FomoxaSystemModels/` | Các model của chính package. Thư mục nằm ngoài `Assets` nên Unity không biên dịch nó. |
| `.fomoxa/` | Các file schema do `fomoxac` viết, như `schema.json`. |
| Generated Folder | Mọi thứ ở trên, cộng với danh sách prefab, danh sách scene, các hằng số của chúng và một scene file cho mỗi network scene. |

Commit tất cả, để một bản clone mới biên dịch được trước khi trình sinh code chạy.

## Kiểm tra kết quả <a href="#check-the-result" id="check-the-result"></a>

Sau khi Unity biên dịch xong:

- Console không có lỗi nào bắt đầu bằng `[Fomoxa]`.
- Generated Folder có `NetSchema.cs`, `FomoxaAdapters.cs`, `FomoxaUnityRegistration.cs` và các adapter như `MessageBundleNetAdapter.cs`.

Mỗi khi schema thay đổi, ví dụ sau khi bạn thêm một model, package log một cảnh báo `[Fomoxa]` liệt kê từng thay đổi, như `+ new message`, kèm việc thay đổi đó có tương thích với các bản build trước hay không. Cảnh báo này là bình thường, không phải lỗi.

Nếu sinh code thất bại, xem [xử lý sự cố](troubleshooting.md#code-generation-fails).

Code sinh ra nằm trong một namespace đặt theo tên thư mục cuối của đường dẫn Generated Folder. Với `Assets/Network/Generated`, namespace là `Generated`, vì vậy các ví dụ trong tài liệu này đều bắt đầu bằng `using Generated;`.

Tiếp tục với [tutorial](tutorial/README.md).
