# Bước 09: Game online hoàn chỉnh

## Mục tiêu <a href="#goal" id="goal"></a>

Bước cuối này build game hoàn chỉnh, chạy nó dưới dạng dedicated server với các client, và kiểm tra màn hình bắt đầu trong một bản build player.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 08, game hoạt động với nhiều client và xử lý được người chơi rời đi hoặc bị crash.

## Vấn đề <a href="#problem" id="problem"></a>

Các bước trước chủ yếu chạy trong Editor, và một bản build player làm lộ ra những thứ Editor che đi. Trong bản build, ô địa chỉ trên màn hình bắt đầu không hiện chữ, vì font của game không vừa với input field mặc định.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Dedicated server](../../../deploy/dedicated-server.md)
- [Triển khai](../../../deploy/deployment.md)
- [Tích hợp Editor: kiểm tra khi build](../../../advanced/editor-integration.md#build-checks)

## Thiết kế <a href="#design" id="design"></a>

Một bản build player phục vụ mọi vai trò, và dòng lệnh chọn vai trò nào:

| Lệnh | Vai trò |
|---|---|
| `RedRunner.exe -batchmode -nographics -server -port 7777 -logFile server.log` | Dedicated server, frame rate giới hạn ở 60 |
| `RedRunner.exe -host` | Server và client trong một tiến trình |
| `RedRunner.exe` | Client; người chơi nhập địa chỉ ở màn hình bắt đầu |

## File <a href="#files" id="files"></a>

```
Assets/Scenes/Play.unity
```

Commit này cũng thêm công cụ chụp màn hình trong `Tools/PortChecks`, cùng các ảnh chụp màn hình dùng trên những trang này.

## Hiện thực <a href="#implementation" id="implementation"></a>

### Sửa ô địa chỉ <a href="#fix-the-address-field" id="fix-the-address-field"></a>

Chuyển `Address Field` xuống dưới các nút của màn hình bắt đầu và đặt Vertical Overflow thành Overflow trên text và placeholder của nó; [bước 03](step-03-player-spawning.md#add-the-address-field) liệt kê thiết lập cuối cùng.

### Build và chạy <a href="#build-and-run" id="build-and-run"></a>

Build một player Windows với `Play.unity` là scene duy nhất. Khởi động server, rồi khởi động các client và bấm Play với địa chỉ của server trong ô bên dưới các nút.

Trong game, phím mũi tên trái và phải để chạy, Space, W hoặc mũi tên lên để nhảy, và Shift để lăn.

## Test <a href="#test" id="test"></a>

Chạy một dedicated server và hai client từ bản build, như ở [bước 08](step-08-two-clients.md#test). Các bài kiểm tra của bản port chạy server và client trên cùng một máy. Để chơi qua nhiều máy, client nhập địa chỉ của server và server phải nhận UDP trên port của nó, như mô tả trong [triển khai](../../../deploy/deployment.md).

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

![Hai người chơi chạy gần điểm bắt đầu của một level dựng từ seed](../../../.gitbook/assets/redrunner-two-players.png)

- Màn hình bắt đầu hiện `localhost` trong ô địa chỉ.
- Mọi client chạy trên cùng một level, thấy nhau, và chết rồi hồi sinh theo quyết định của server.

## Commit <a href="#commit" id="commit"></a>

```
Commit: 7396f92
Message: Finish the GitBook guide with screenshots and a quick start
```

Xem [`7396f92`](https://github.com/fomoxa/RedRunner/commit/7396f9279b5796ffb35d97765cbe5cb1794d5357) trên GitHub.

Trong lịch sử, `7396f92` nằm sau `52e1696` và trước ba commit còn lại của bước 08.

Trang [kiến trúc bản online](../architecture.md) mô tả cái gì chạy ở đâu trong game hoàn chỉnh, và [xử lý sự cố](../troubleshooting.md) giúp khi có gì đó không hoạt động.
