# Tài liệu

Tài liệu này nằm trong một repository riêng, tách khỏi package, nên không thuộc phần người dùng cài đặt và Unity không bao giờ import nó. GitBook xuất bản nó qua Git Sync. `gitbook-docs.yaml` mô tả site và hai space của nó, tiếng Anh và tiếng Việt, còn `.gitbook.yaml` chỉ ra `README.md` và `SUMMARY.md`; cả hai file nằm ở gốc của tài liệu.

## Cấu trúc <a href="#structure" id="structure"></a>

| Phần | Mục đích |
|---|---|
| Bắt đầu | Người dùng mới cài package và xây một game nhỏ từng bước |
| Khái niệm | Package hoạt động thế nào: các tầng, tick, authority, replication, prediction |
| Core, Messaging, Đồng bộ, Prediction, Physics, Transport, Server, Unity | Mỗi tính năng một hướng dẫn, kèm code chạy được |
| Nâng cao | Codec tùy chỉnh, hiệu năng, debug |
| Ví dụ | Các game có sẵn được chuyển sang dùng package, từng bước, kèm code và commit thật. Phần giải thích chung nằm ở các hướng dẫn tính năng và được link từ đây |
| Tham chiếu | Mô tả ngắn và chính xác về public API, để tra cứu |
| Đóng góp | Làm việc với package và với các trang này |

`SUMMARY.md` là mục lục, và mọi trang phải được liệt kê trong đó.

## Quy tắc <a href="#rules" id="rules"></a>

- Viết các trang tiếng Anh bằng văn kỹ thuật đơn giản. Heading viết hoa kiểu câu.
- Mô tả code hiện tại. Tính năng chưa hiện thực được đánh dấu như vậy và không được mô tả như thể nó chạy được.
- Kiểm tra mọi type, member và message với source trước khi viết ra.
- Ví dụ code biên dịch được với API hiện tại và dùng tên adapter được sinh, như `ShotNetAdapter.Instance`.
- Dùng cùng một tên cho cùng một thứ ở mọi nơi: `NetworkObject`, `NetworkBehaviour`, `NetworkManager`, prediction, reconciliation, rollback, replay.
- Link các trang liên quan bằng link tương đối, và giữ các link tới heading hoạt động khi đổi tên heading.
- Chỉ dùng GitBook hint (`{% hint style="warning" %}`) cho những cảnh báo người đọc không được bỏ lỡ.

## Bản tiếng Việt <a href="#vietnamese-translation" id="vietnamese-translation"></a>

Các trang tiếng Việt nằm trong `vi/`, có `README.md` và `SUMMARY.md` riêng, và tương ứng từng file với các trang tiếng Anh. GitBook xuất bản chúng như một space thứ hai với ngôn ngữ đặt là `vi`, nên người đọc đổi ngôn ngữ bằng nút chọn ngôn ngữ.

Các trang tiếng Anh là bản gốc. Khi sửa một trang tiếng Anh, hãy sửa trang tiếng Việt cùng đường dẫn trong cùng commit. Trang tiếng Việt giữ nguyên các code block của trang tiếng Anh và có cùng các heading theo cùng thứ tự. Mỗi heading đã dịch kết thúc bằng một thẻ anchor mang anchor tiếng Anh, như `## Teleport <a href="#teleporting" id="teleporting"></a>`, để link tới heading hoạt động ở cả hai ngôn ngữ. Các thuật ngữ kỹ thuật như model, codec, tick, peer và owner giữ nguyên tiếng Anh trong văn bản tiếng Việt.

## Câu hỏi còn mở <a href="#open-questions" id="open-questions"></a>

`DOCUMENTATION-TODO.md` ở gốc của tài liệu liệt kê những gì tài liệu chưa thể xác định được từ code. Nó không thuộc mục lục được xuất bản.
