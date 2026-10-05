# Phát triển

Trang này mô tả cấu trúc của package và cách chạy test của nó từ một project Unity. Bản thân tài liệu không thuộc package và nằm trong một repository riêng.

## Cấu trúc package <a href="#package-layout" id="package-layout"></a>

| Thư mục | Nội dung |
|---|---|
| `Runtime/Core` | Tầng 1, assembly `Fomoxa.Unity.Core`; không tham chiếu Unity |
| `Runtime/Core/SystemModels` | Các model của chính package, được copy vào project để sinh code |
| `Runtime/Unity` | Tầng 2, assembly `Fomoxa.Unity`, và `FomoxaWebSocket.jslib` |
| `Runtime/Unity/Generators` | Source generator cho RPC, build thành DLL |
| `Runtime/Plugins` | `Fomoxa.Net.dll` và `Fomoxa.Attributes.dll` |
| `Editor` | Assembly `Fomoxa.Unity.Editor`: sinh code, gán id, kiểm tra khi build |
| `Tests/Core`, `Tests/Unity`, `Tests/Fixtures` | Các assembly test, chỉ được biên dịch khi project bao gồm test của package |
| `Tools~/fomoxac` | Các binary `fomoxac`; Unity không import thư mục có tên kết thúc bằng `~` |

## Chạy test <a href="#running-the-tests" id="running-the-tests"></a>

Các assembly test dùng define `UNITY_INCLUDE_TESTS`, nên Unity chỉ biên dịch chúng khi project đánh dấu package là testable. Để làm vậy, thêm đoạn sau vào `Packages/manifest.json` của project:

```json
"testables": [
  "com.fomoxa.unity"
]
```

Sau đó mở Window > General > Test Runner và chạy các test EditMode. Test trong `Fomoxa.Unity.Core.Tests` bao phủ tầng 1, còn test trong `Fomoxa.Unity.Tests` tạo các component `NetworkManager`, transport và physics scene trong Editor.

## Phong cách code <a href="#code-style" id="code-style"></a>

Code của package không có comment và dựa vào tên để truyền đạt ý nghĩa. Hãy theo phong cách của file bạn sửa.

[Kiến trúc](../concepts/architecture.md) giải thích các tầng trong cấu trúc này khớp với nhau thế nào, và [tài liệu](documentation.md) nói về việc làm việc với các trang tài liệu.
