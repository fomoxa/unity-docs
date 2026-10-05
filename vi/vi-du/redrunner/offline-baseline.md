# Bản offline ban đầu

Trang này mô tả Red Runner ở commit `2b675b5`, branch `master` của [BayatGames/RedRunner](https://github.com/BayatGames/RedRunner). Fork [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner) chứa cùng commit này với bản port nằm phía trên, và mọi thứ trong quá trình [chuyển đổi](offline-to-online/README.md) đều bắt đầu từ đây.

```
git clone https://github.com/fomoxa/RedRunner.git
cd RedRunner
git switch -c my-port 2b675b5
```

## Vòng lặp frame <a href="#the-frame-loop" id="the-frame-loop"></a>

```
Start screen (Play button)
  ↓
GameManager.StartGame: gameRunning = true, Time.timeScale = 1
  ↓
RedCharacter.Update, every frame
  reads CrossPlatformInputManager
  ↓
Move, Jump, roll force on the Rigidbody2D
  ↓
Unity 2D physics
  ↓
Enemy collision callbacks: Die
TerrainGenerator.Update: next block near the character
GameManager.Update: score = furthest x
  ↓
CameraController follows the character
```

Mọi thứ diễn ra trong một tiến trình, mỗi frame, không có gì phải chờ thứ gì khác.

## Điểm vào <a href="#entry-point" id="entry-point"></a>

Toàn bộ game nằm trong `Assets/Scenes/Play.unity`. Scene list trong build settings ghi `Assets/Scenes/Gooose.unity`, scene không tồn tại trong repository, nên game được chơi từ `Play.unity` trong Editor.

`GameManager` là một singleton trong scene. `Awake` của nó load số đồng xu, thiết lập âm thanh và điểm số bằng SaveGameFree, còn `Start` subscribe vào property `IsDead` của nhân vật chính và gọi `Init`, hàm hiện màn hình bắt đầu sau ba giây. Sau đó nút Play mở màn hình trong game và gọi `StartGame`.

## Người chơi và input <a href="#player-and-input" id="player-and-input"></a>

Nhân vật là object `RedRunner` trong `Play.unity`, có `RedCharacter`, một `Rigidbody2D` và một `Animator`. `GameManager`, `TerrainGenerator` và `CameraController` đều giữ tham chiếu tới nó trong một serialized field.

`RedCharacter.Update` return sớm khi game không chạy, còn không thì tự đọc bàn phím:

```csharp
// Input Processing
Move ( CrossPlatformInputManager.GetAxis ( "Horizontal" ) );
if ( CrossPlatformInputManager.GetButtonDown ( "Jump" ) )
{
	Jump ();
}
```

Hành động đỡ và đấm đến từ các nút `Guard` và `Fire`, còn nút Roll thêm một lực theo `transform.localScale.z`.

## Di chuyển và physics <a href="#movement-and-physics" id="movement-and-physics"></a>

Di chuyển dùng physics 2D của Unity với fixed timestep 0.02 giây của project. `Update` tăng tốc nhân vật vượt tốc độ chạy bằng `Mathf.SmoothDamp`, hàm dùng thời gian frame và giữ vận tốc damping trong một field giữa các frame. `Jump` đặt vận tốc dọc khi `GroundCheck.IsGrounded` là true, cờ mà `GroundCheck` cập nhật mỗi frame một lần.

## Level <a href="#level" id="level"></a>

`TerrainGenerator` dựng level trong lúc nhân vật chạy. Mỗi khi nhân vật tới gần khối cuối cùng, `Generate` thêm khối tiếp theo, được `TerrainGenerator.ChooseFrom` chọn bằng `Random.value`. Với các số lượng trong `Assets/Generation Settings.asset`, level không bao giờ kết thúc. Các khối nền, như đồi và mây, được thêm theo cùng cách.

## Chướng ngại <a href="#hazards" id="hazards"></a>

Mỗi kẻ địch giết nhân vật từ callback của riêng nó:

| Kẻ địch | Callback | Hiệu ứng do kẻ địch phát |
|---|---|---|
| `Saw` | `OnCollisionEnter2D` | không có, gọi `Die (true)` để có máu |
| `Spike` | `OnCollisionStay2D`, chỉ từ phía trên | âm thanh gai, joint tới bộ xương |
| `Water` | `OnTriggerEnter2D` | particle và âm thanh bắn nước |
| `Mace` | `OnCollisionEnter2D` | đập, cười, âm thanh gai |

Rơi xuống dưới y = 0 cũng giết nhân vật, từ `RedCharacter.Update`.

Chùy và lưỡi cưa trên đường ray di chuyển bằng `PathFollower`, có `Update` đưa object về phía điểm tiếp theo bằng `Time.deltaTime` và dừng khi `GameManager.gameRunning` là false. Khi bật Smart, như trên chùy, nó chờ tới khi có nhân vật trong tầm.

## Trạng thái game, chết và hồi sinh <a href="#game-state-death-and-respawn" id="game-state-death-and-respawn"></a>

`Character.IsDead` là một `Property<bool>`. Khi nó thành true, `GameManager.DeathCrt` ghi điểm, chờ 1.5 giây rồi mở màn hình kết thúc. Nút của màn hình kết thúc gọi `GameManager.Reset`, hàm phát `OnReset`, và khi đó nhân vật quay về vị trí ban đầu và sống lại, địa hình được xóa và dựng lại, và các chùy được đặt lại.

## Điểm số và đồng xu <a href="#score-and-coins" id="score-and-coins"></a>

Điểm số là tọa độ x xa nhất nhân vật đã tới. Đồng xu và rương cộng vào `GameManager.m_Coin` khi bất kỳ `Character` nào chạm vào, và điểm số cùng đồng xu được lưu bằng SaveGameFree khi game thoát.

## Camera và tạm dừng <a href="#camera-and-pause" id="camera-and-pause"></a>

`CameraController` đi theo `Transform` trong field Followee của nó và di chuyển nhanh sau khi nhân vật chết. `GameManager.StopGame` và `ResumeGame` đặt `Time.timeScale` về 0 và về lại 1, việc này đóng băng mọi thứ phía sau màn hình tạm dừng.

## Những gì không thể giữ nguyên <a href="#what-cannot-stay-as-it-is" id="what-cannot-stay-as-it-is"></a>

| Hành vi offline | Vì sao hỏng khi online | Bước |
|---|---|---|
| Một nhân vật trong scene | Mỗi người chơi cần một nhân vật, và server quyết định ai sở hữu nhân vật nào | [Bước 03](offline-to-online/step-03-player-spawning.md) |
| `RedCharacter.Update` đọc bàn phím | Mọi nhân vật trong một tiến trình sẽ di chuyển theo cùng một bàn phím | [Bước 03](offline-to-online/step-03-player-spawning.md), [Bước 04](offline-to-online/step-04-player-input.md) |
| Di chuyển theo frame với `Time.deltaTime` | Server và client phải chạy cùng một bước và replay được nó | [Bước 04](offline-to-online/step-04-player-input.md) |
| Level vô tận từ `Random.value` | Mỗi tiến trình sẽ dựng ra mặt đất khác nhau | [Bước 02](offline-to-online/step-02-shared-level.md) |
| Kẻ địch giết trong callback của chúng | Nhân vật được dự đoán hoặc interpolate có thể ở chỗ khác so với trên server | [Bước 06](offline-to-online/step-06-death-and-respawn.md) |
| Điểm số và màn hình kết thúc | Không có một nhân vật chính duy nhất và lượt chạy không có kết thúc | [Bước 06](offline-to-online/step-06-death-and-respawn.md) |
| Tạm dừng bằng `Time.timeScale` | Server và người chơi khác vẫn tiếp tục chạy | [Bước 03](offline-to-online/step-03-player-spawning.md) |
| Chùy chờ nhân vật tới gần | Mỗi tiến trình sẽ khởi động chùy ở thời điểm khác nhau | [Bước 07](offline-to-online/step-07-moving-hazards.md) |

Quá trình chuyển đổi xử lý từng điểm trên bắt đầu ở [từ offline lên online](offline-to-online/README.md).
