# Tính tất định

Rapier cho cùng một kết quả với cùng một world và cùng một chuỗi thao tác. Backend giữ phần của nó trong lời hứa đó: một phiên bản Rapier cố định, feature `enhanced-determinism`, world được dựng theo cùng thứ tự trên mọi máy, và snapshot giữ cả world. Code game phải giữ cho các thao tác giống nhau.

## Code game phải làm gì <a href="#what-game-code-must-do" id="what-game-code-must-do"></a>

- Chỉ thay đổi body trong callback prediction (`apply`, `restore`) và tick event, theo một thứ tự cố định, từ input và số tick. Lực, xung lực và việc ghi state là thao tác trên world, và thứ tự khác cho kết quả khác.
- Không để phép toán thư viện đi vào các giá trị tới được mô phỏng. `Mathf.Sin`, `MathF.Cos` và các hàm thư viện khác có thể khác nhau ở bit cuối giữa Mono, IL2CPP và .NET. Hãy dùng bảng tra, phép toán số nguyên hoặc giá trị đến từ input.
- Không đọc thời gian, giá trị phụ thuộc frame hay bộ sinh số ngẫu nhiên seed từ đồng hồ trong code mô phỏng. Bộ sinh seed từ một giá trị server gửi, với phép toán của riêng nó, cho cùng một dãy số ở mọi nơi.
- Dựng geometry lúc chạy theo cùng thứ tự trên mọi peer. Số thứ tự của `AddStatic`, `AddBody` và thứ tự body trong world đi theo thứ tự các lời gọi.

`System.Random` không được bảo đảm cho cùng một dãy số dưới Mono và .NET, nên nó không hợp cho một level mà client Unity và server console cùng dựng từ một seed.

## Kiểm tra một lần chạy <a href="#checking-a-run" id="checking-a-run"></a>

`RapierWorld.StateHash` và `RapierWorld2D.StateHash` băm toàn bộ state của một world. So hash của cùng một tick trên hai máy, hoặc trên server và một client, cho biết hai mô phỏng có còn giống nhau không. Bản thân package không gửi hay so hash.

## Những gì vẫn gần đúng <a href="#what-is-still-approximate" id="what-is-still-approximate"></a>

Prediction vẫn sửa khi input của server khác với dự đoán của client, ví dụ khi input của người chơi khác đến muộn hoặc một body ở xa di chuyển khác với proxy đã hiển thị. Tính tất định loại bỏ những lần sửa do physics engine gây ra. Những lần sửa do client thiếu thông tin vẫn còn.

Bản build player IL2CPP chưa được kiểm tra tính tất định so với Mono và .NET.
