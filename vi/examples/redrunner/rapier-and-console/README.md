# Rapier và server console

Quá trình chuyển [từ offline lên online](../offline-to-online/README.md) kết thúc với một game chạy trên physics 2D của Unity và một server Unity. Phần này đi tiếp từ đó qua bốn bước. Nó chuyển game sang [backend Rapier](../../../rapier/overview.md), đưa luật game ra khỏi code Unity, và thêm một [server console](../../../console-server/overview.md) chạy cùng game đó mà không cần Unity.

Cuối cùng game chơi vẫn như cũ. Thay đổi nằm bên dưới:

- Replay của prediction tái tạo đúng physics của server, vì Rapier lưu và khôi phục cả world, kể cả contact.
- Các luật chạy, nhảy, chạm đất, cái chết và chướng ngại di chuyển nằm trong assembly `RedRunner.Simulation` không tham chiếu Unity, mà game Unity và server console cùng gọi.
- Physics của level được dựng từ một level catalogue đã xuất thay vì từ prefab, nên một tiến trình không có Unity cũng dựng được.
- Một chương trình .NET trong `Server~/` chạy server. Client Unity vào nó qua cùng màn hình bắt đầu.

## Các bước <a href="#steps" id="steps"></a>

| Bước | Nó thêm gì | Các trang Fomoxa chính |
|---|---|---|
| [10 Backend Rapier](step-10-rapier-backend.md) | `RapierPhysics` trên `Network Manager`, level dưới dạng nhóm tĩnh và body không chủ, chạm đất và cái chết từ tập contact | [Cài đặt Rapier](../../../rapier/setup.md), [Body và collider](../../../rapier/bodies.md) |
| [11 Thư viện mô phỏng](step-11-simulation-library.md) | Luật game trong `RedRunner.Simulation`, một bộ sinh số ngẫu nhiên riêng theo seed | [Tính tất định của Rapier](../../../rapier/determinism.md) |
| [12 Catalogue level](step-12-level-catalogue.md) | `RedRunner.Models`, catalogue đã xuất gồm block, body và đường đi, `LevelBuilder` | [Physics của console](../../../console-server/physics.md) |
| [13 Server console](step-13-console-server.md) | `Server~/`, một server .NET xây trên backend console và `RapierScenes` | [Server console](../../../console-server/overview.md) |

## Commit <a href="#commits" id="commits"></a>

| Bước | Commit |
|---|---|
| 10 | [`beb18a4`](https://github.com/fomoxa/RedRunner/commit/beb18a475db7cd27e9db29271c7bb1cb465f45e3) Run the online game on the Rapier physics backend |
| 11 | [`d8a30c4`](https://github.com/fomoxa/RedRunner/commit/d8a30c4e8f1baef53fc3125eddeb5a6b9d63c93d) Move the game simulation into RedRunner.Simulation |
| 12 | [`c44bcfe`](https://github.com/fomoxa/RedRunner/commit/c44bcfee259504c213a1542353a012b0f07d0805) Build the Rapier level from an exported level catalogue |
| 13 | [`125e3b8`](https://github.com/fomoxa/RedRunner/commit/125e3b8f34182d77bb9184f1a5e192460354bc6b) Add a .NET console server without Unity |

Các bước bắt đầu từ [`f164d56`](https://github.com/fomoxa/RedRunner/commit/f164d5624f171b64c8bfc6f029b12be2cfe41e27), điểm kết thúc của phần một. Khác với phần một, mỗi trang hiển thị code như ở commit của chính nó, và bước sau nêu rõ nó thay đổi gì.

## Yêu cầu <a href="#requirements" id="requirements"></a>

- Mọi thứ phần một cần, trên máy Windows x64 hoặc Linux x64, vì backend Rapier chỉ có thư viện native cho hai nền tảng đó.
- .NET 8 SDK, từ bước 13 trở đi.
- Các phép kiểm của những bước này chạy với backend Rapier bằng `Tools/unity-windows.sh`, như ở phần một. Bước 13 thêm `play-console`, chạy cùng các phép kiểm Play Mode đó trên server console.

## Xử lý sự cố <a href="#troubleshooting" id="troubleshooting"></a>

- Client dừng ngay sau khi vào với `PhysicsBackendMismatch`: client và server dùng component physics khác nhau. Mọi `Network Manager` của bản build, và `NetworkSettings.PhysicsBackend` của server console, phải dùng Rapier.
- Console cảnh báo `scene 0x... has no scene file`: xuất các network scene file bằng Tools > Fomoxa > Export Network Scene Files và commit `Generated/<scene id>.fomoxascene`.
- Nhân vật chìm qua level hoặc rơi lúc bắt đầu: level chưa được thêm vào Rapier. `NetworkLevel` phải dựng nó ở cả `OnStartServer` và `OnStartClient`, sau khi seed tới, và theo cùng thứ tự trên mọi peer.
- `the level catalogue was exported for a tick of ... s, the game ticks every ... s`: tick rate của `Network Manager` đã đổi sau khi catalogue được xuất. Hãy xuất lại bằng Tools > RedRunner > Export Level Catalogue.
- Server console in ra lỗi `behaviour type ... is not registered with StandaloneBehaviours`: một scene object của `Play.unity` có thêm `NetworkBehaviour` mới. Hãy đăng ký một behaviour console cho tên type của nó trong `ServerGame`.
- Client thất bại ở handshake với `SchemaConflict` khi nối tới server console: server console được build từ code sinh ra khác. Hãy để Unity sinh code, rồi build lại `Server~`.

Bắt đầu với [bước 10: backend Rapier](step-10-rapier-backend.md).
