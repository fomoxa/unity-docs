# Red Runner

Red Runner là một game platformer 2D miễn phí của Bayat Games, viết cho một người chơi. Nhân vật chạy sang phải qua một level gồm các khối, nhảy qua nước, lưỡi cưa, gai và chùy đung đưa, và nhặt đồng xu dọc đường. Ví dụ này biến game đó thành game online xây trên `com.fomoxa.unity`, từng bước một.

Trong khi các trang khác của tài liệu giải thích từng phần của package hoạt động ra sao, các trang này cho thấy những gì phải thay đổi trong một game thật vốn không được viết cho mạng, theo đúng thứ tự các thay đổi đã được thực hiện.

## Vì sao chọn game này <a href="#why-this-game" id="why-this-game"></a>

Red Runner đủ nhỏ để đọc hết trong một buổi chiều, nhưng vẫn có những vấn đề mà hầu hết game offline mang theo:

- Một scene object giữ nhân vật duy nhất, và nhiều object khác trỏ tới nó.
- Nhân vật đọc bàn phím trong `Update` và di chuyển bằng `Time.deltaTime`.
- `UnityEngine.Random` dựng một level vô tận trong lúc nhân vật chạy.
- Kẻ địch giết nhân vật từ chính các collision callback của chúng.
- Màn hình tạm dừng đặt `Time.timeScale` về 0.
- Chùy chờ nhân vật tới gần rồi mới di chuyển.

Mỗi điều trên đều đúng với một người chơi trong một tiến trình, và mỗi điều đều phải thay đổi khi game lên online.

## Game ban đầu <a href="#the-game-before" id="the-game-before"></a>

Game một người chơi là [BayatGames/RedRunner](https://github.com/BayatGames/RedRunner), và branch `master` của nó ở commit `2b675b5` là điểm xuất phát của ví dụ này. Bản port là [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner), một fork có branch `master` tiếp nối từ commit đó. Trang [bản offline ban đầu](offline-baseline.md) mô tả phiên bản xuất phát hoạt động thế nào.

## Game sau khi port <a href="#the-game-after" id="the-game-after"></a>

Một dedicated server chạy game. Người chơi mở client, nhập địa chỉ server ở màn hình bắt đầu và được đưa thẳng vào level, không có lobby hay phòng. Mọi người chơi chạy trên cùng một level, do server và mỗi client dựng từ một seed mà server chọn. Level có một khối bắt đầu, hai mươi khối giữa và một khối kết thúc, và tới khối kết thúc sẽ đưa người chơi về điểm bắt đầu.

Server quyết định khi nào người chơi chết. Lưỡi cưa, gai, nước và chùy giết trên server, client hiện bộ xương khi server báo, và người chơi hồi sinh ở điểm bắt đầu hai giây sau. Đồng xu và rương chỉ nằm trên từng client như vật trang trí, không có điểm số, và người chơi đi xuyên qua nhau.

Nhân vật của bạn di chuyển ngay khi bạn bấm phím, vì client dự đoán nó bằng physics `Rigidbody2D` và sửa lại khi kết quả của server khác đi. Nhân vật của người chơi khác được interpolate từ server.

![Hai người chơi chạy gần điểm bắt đầu của một level dựng từ seed](../../../.gitbook/assets/redrunner-two-players.png)

## Fomoxa được dùng ở đâu <a href="#where-fomoxa-is-used" id="where-fomoxa-is-used"></a>

| Phần của game | Tính năng Fomoxa | Trang |
|---|---|---|
| Khởi động server, host hoặc client | `NetworkManager`, `ServerManager`, `ClientManager` | [Server](../../core/server.md), [Client](../../core/client.md), [Host mode](../../core/host-mode.md) |
| Seed của level | State trên một scene object | [State](../../synchronization/state.md), [Spawn](../../core/spawning.md#scene-objects) |
| Mỗi người chơi một nhân vật | Spawn prefab kèm owner | [Spawn](../../core/spawning.md), [Ownership](../../core/ownership.md) |
| Vị trí của người chơi khác | `NetworkTransform` | [NetworkTransform](../../synchronization/transform.md) |
| Nhân vật của bạn | Input, prediction và reconciliation với physics 2D | [Tổng quan prediction](../../prediction/overview.md), [Rollback với physics](../../prediction/rollback.md) |
| Chết và hồi sinh | State, `NetworkTransform.Teleport` | [State](../../synchronization/state.md), [Teleport](../../synchronization/transform.md#teleporting) |
| Chùy và lưỡi cưa di chuyển | Tick event và số tick | [Tick và thời gian](../../concepts/tick.md) |

## Bạn học được gì <a href="#what-you-learn" id="what-you-learn"></a>

- Cách tìm các phần của một game offline giả định chỉ có một người chơi và một tiến trình.
- Cách giao quyết định cho server và để phần hiển thị ở client.
- Cách biến một character controller theo frame thành một bước tick mà cả server và client cùng chạy.
- Cách replicate cả một level sinh thủ tục chỉ bằng bốn byte.
- Cách xử lý hồi sinh, thứ làm hỏng cả interpolation lẫn prediction.
- Điều gì xảy ra khi một người chơi thoát hoặc bị crash.

## Các trang được sắp xếp thế nào <a href="#how-the-pages-are-organized" id="how-the-pages-are-organized"></a>

1. [Bản offline ban đầu](offline-baseline.md) mô tả game một người chơi.
2. [Từ offline lên online](offline-to-online/README.md) là quá trình chuyển đổi, gồm chín bước. Mỗi bước nêu các file nó thay đổi, code, cách test và commit đã thực hiện nó.
3. [Kiến trúc bản online](architecture.md) mô tả game đã hoàn chỉnh.
4. [Xử lý sự cố](troubleshooting.md) liệt kê các vấn đề riêng của bản port này.

Nếu chưa dùng package bao giờ, hãy đọc [tick và thời gian](../../concepts/tick.md), [authority](../../concepts/authority.md) và [prediction](../../concepts/prediction.md) trước. Các bước link tới những trang chúng dựa vào thay vì nhắc lại nội dung.

## Yêu cầu <a href="#requirements" id="requirements"></a>

- Unity 6000.5 trở lên. Package cần 6000.5, còn branch `master` của Red Runner dùng 6000.2.6f2.
- Editor Windows x64 hoặc Linux x64, để sinh code.
- Có kinh nghiệm với Unity Editor và C#.
