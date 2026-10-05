# Cài đặt

Trang này thêm package vào một project Unity và thiết lập việc sinh code. Khi xong, project biên dịch được cùng code sinh ra và sẵn sàng cho hướng dẫn [project đầu tiên](first-project.md).

## Yêu cầu <a href="#requirements" id="requirements"></a>

Package cần Unity 6000.5 trở lên, chạy trong Editor Windows x64 hoặc Linux x64. Công cụ sinh code `fomoxac` chỉ đi kèm cho hai nền tảng này, nên trong Editor macOS việc sinh code dừng lại với thông báo `the fomoxac binary for this editor platform is missing`.

Package còn phụ thuộc vào các module có sẵn Physics, Physics 2D và Animation. Vì package khai báo chúng là dependency, Package Manager tự bật các module này.

## Thêm package <a href="#add-the-package" id="add-the-package"></a>

### Từ Git URL <a href="#from-a-git-url" id="from-a-git-url"></a>

Trong Unity, mở Window > Package Manager, bấm nút +, chọn Install package from git URL và nhập:

```
https://github.com/fomoxa/com.fomoxa.unity.git
```

Để cố định phiên bản, thêm branch, tag hoặc commit sau dấu `#`, ví dụ `https://github.com/fomoxa/com.fomoxa.unity.git#<tag>`.

### Từ thư mục trên máy <a href="#from-a-local-folder" id="from-a-local-folder"></a>

Để làm việc với một bản copy trên máy, chọn Install package from disk trong cùng menu rồi chọn file `package.json` của package, Package Manager sẽ thêm một mục `file:` vào `Packages/manifest.json`. Bạn cũng có thể tự viết mục này. Một đường dẫn tương đối so với thư mục `Packages` của project sẽ dùng được trên mọi máy có cùng cấu trúc thư mục:

```json
"com.fomoxa.unity": "file:../../com.fomoxa.unity"
```

## Tạo settings asset <a href="#create-the-settings-asset" id="create-the-settings-asset"></a>

Package đọc vị trí các model của bạn, cùng thư mục để ghi code sinh ra, từ một asset `FomoxaSettings`.

1. Tạo một thư mục cho model, ví dụ `Assets/Network/Models`, và một thư mục cho code sinh ra, ví dụ `Assets/Network/Generated`.
2. Bấm chuột phải vào một thư mục trong cửa sổ Project và chọn Create > Fomoxa > Settings.
3. Trong asset mới, đặt Models Folder thành `Assets/Network/Models` và Generated Folder thành `Assets/Network/Generated`. Giá trị mặc định là `Assets/Models` và `Assets/Generated`.

Project chỉ được có đúng một asset `FomoxaSettings`. Nếu có hai, package log `more than one FomoxaSettings asset exists; keep exactly one` và không sinh gì cả.

Thư mục model phải tồn tại trước lần sinh code đầu tiên, kể cả khi còn trống, vì `fomoxac` dừng lại khi thiếu thư mục nguồn. Git không giữ thư mục trống, nên hãy đặt một file `.gitkeep` trống vào đó; Unity bỏ qua các file có tên bắt đầu bằng dấu chấm.

## Sinh code <a href="#generate-the-code" id="generate-the-code"></a>

Package sinh code sau mỗi lần biên dịch script, và bạn cũng có thể chạy thủ công bằng Tools > Fomoxa > Generate. Mỗi lần sinh code ghi các file sau:

| Đường dẫn | Nội dung |
|---|---|
| `fomoxa.toml` | Cấu hình của `fomoxac`, được ghi từ settings asset. Hãy sửa asset, đừng sửa file này. |
| `FomoxaSystemModels/` | Các model của chính package, được copy ra khỏi package để `fomoxac` đọc được. Thư mục này nằm ngoài `Assets` nên Unity không biên dịch nó. |
| `.fomoxa/` | Các file schema do `fomoxac` ghi. |
| Generated Folder | Một codec và một adapter cho mỗi model, `NetSchema.cs`, `FomoxaAdapters.cs`, `FomoxaUnityRegistration.cs`, danh sách prefab và hằng số của chúng, danh sách scene và hằng số của chúng, cùng hai thư mục con `RpcModels` và `UnityCodecs`. |

Hãy commit tất cả để một bản clone mới biên dịch được trước khi bộ sinh code chạy.

Bạn không bao giờ phải tự gọi code đăng ký. `FomoxaUnityRegistration.cs` đăng ký schema và codec đã sinh khi player hoặc Play Mode khởi động, và `NetworkManager` lấy chúng từ đó.

## Kiểm tra kết quả <a href="#check-the-result" id="check-the-result"></a>

Sau khi Unity biên dịch xong, Console không được có lỗi nào bắt đầu bằng `[Fomoxa]`, và Generated Folder phải có `NetSchema.cs`, `FomoxaAdapters.cs` cùng các adapter như `MessageBundleNetAdapter.cs`. Nếu sinh code thất bại, xem [xử lý sự cố](troubleshooting.md#code-generation-fails).

Code sinh ra nằm trong namespace mang tên thư mục cuối cùng của đường dẫn Generated Folder. Với `Assets/Network/Generated`, namespace đó là `Generated`, vì vậy các ví dụ trong tài liệu này bắt đầu bằng `using Generated;`.

Tiếp theo là [project đầu tiên](first-project.md).
