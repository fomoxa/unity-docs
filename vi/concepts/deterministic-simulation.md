# Mô phỏng tất định

Một mô phỏng là tất định khi cùng state ban đầu và cùng input luôn cho ra cùng kết quả. Game networking dựa vào tính tất định ở các mức khác nhau tùy tính năng, và package cung cấp một số mức chứ không phải tất cả. Trang này phân rõ mức nào có, mức nào không.

```text
Deterministic input        same input for the same tick on every machine
        ↓
Deterministic game logic   apply() gives the same result from the same input and state
        ↓
Deterministic physics      the physics engine gives the same result from the same bodies
        ↓
Deterministic tick         every step has the same length and number
        ↓
Deterministic state        the state after tick N is the same everywhere
        ↓
Replay / rollback / lockstep
```

Mỗi mức phụ thuộc vào các mức phía trên nó. Game lockstep cần mọi mức đúng tới từng bit trên mọi nền tảng, còn client-side prediction, thứ package này hiện thực, chỉ cần chúng đủ gần để việc sửa hiếm khi xảy ra.

## Package cung cấp gì <a href="#what-the-package-provides" id="what-the-package-provides"></a>

| Thuộc tính | Tình trạng trong package |
|---|---|
| Giao thức tất định | Mỗi message có layout cố định do schema sinh ra quy định, và client với server so sánh schema trong lúc handshake. |
| Input tất định | Input gắn với một tick. Server áp dụng input của tick N tại tick N của nó. Khi thiếu input cho một tick, server lặp lại input cuối và đánh dấu bằng `InputContext.Repeated`. |
| Tick tất định | Tick có độ dài cố định, `TimeManager.TickDelta`, và client với server đánh số chúng trên cùng một thang. Replay dùng cùng độ dài tick. |
| Logic game tất định | Thuộc trách nhiệm của bạn. Package gọi `apply` với cùng input ở hai bên, nhưng không thể kiểm tra `apply` đọc những gì. |
| Physics tất định | Không có. Package step các physics engine của Unity, vốn không đảm bảo cho kết quả giống hệt nhau giữa các máy. |
| State tất định | Không yêu cầu. Hàm `matches` của reconcile quyết định state của client phải gần state của server tới mức nào. |

## Prediction không cần kết quả đúng tới từng bit <a href="#prediction-does-not-need-bit-exact-results" id="prediction-does-not-need-bit-exact-results"></a>

Client so sánh state đã dự đoán với state của server cho cùng một tick. Khi chúng khác nhau, client khôi phục state của server và chạy lại các input mới hơn, nên một khác biệt nhỏ chỉ tốn một lần sửa và game vẫn đồng bộ. Mặc định phép so sánh là chính xác trên các byte đã encode, còn với giá trị số thực bạn truyền một hàm `matches` có dung sai, như trong [reconciliation](../prediction/reconciliation.md).

Để việc sửa hiếm khi xảy ra, `apply` chỉ nên đọc input nó nhận, state của chính behaviour (thứ reconcile model chụp lại và khôi phục) và `TimeManager.TickDelta`. Đọc object khác, `Time.deltaTime`, số ngẫu nhiên không có seed hoặc dữ liệu chỉ một bên có sẽ làm hai bên khác nhau, và reconciliation sẽ sửa khác biệt đó mỗi lần nó xuất hiện. `NetworkBehaviour.ReconcileCount` đếm số lần sửa của một behaviour, giúp bạn tìm ra phụ thuộc như vậy.

## Physics chỉ gần đúng <a href="#physics-is-approximate" id="physics-is-approximate"></a>

Khi bật mô phỏng physics, client lưu state của mỗi physics world sau mỗi tick và load lại nó để rollback. State đã lưu chứa vị trí, góc xoay, vận tốc, vận tốc góc và trạng thái ngủ của mỗi body dynamic, nhưng không chứa dữ liệu contact của physics engine, nên một lần replay bắt đầu từ state đã load có thể khác lần chạy gốc. [Rollback với physics](../prediction/rollback.md) đi vào chi tiết.

## Chưa hiện thực <a href="#not-implemented" id="not-implemented"></a>

Một số tính năng cần mức tất định mà package không cung cấp, và package không có chúng. Không có lockstep simulation, không có bộ sinh số ngẫu nhiên tất định và không có state hashing để phát hiện lệch. Cũng không thể ghi lại một trận đấu rồi phát lại sau. Ở mọi chỗ trong tài liệu này, replay nghĩa là áp dụng lại input trong lúc reconciliation.

Để tìm hiểu thêm các phần trang này dựa vào, xem [prediction](prediction.md), [tick và thời gian](tick.md) và [tổng quan physics](../physics/overview.md).
