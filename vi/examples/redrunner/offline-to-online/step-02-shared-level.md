# Bước 02: Level dùng chung

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, mọi tiến trình dựng cùng một level hữu hạn. Server chọn một seed và giữ nó làm state của một network object trong scene, và mỗi client dựng level khi seed tới.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 01, package đã được cài và `Play.unity` có một `Network Manager`, nhưng level vẫn vô tận và được dựng trong lúc nhân vật chạy.

## Vấn đề <a href="#problem" id="problem"></a>

```
Offline:
TerrainGenerator.Update
  ↓
character near the last block?
  ↓
ChooseFrom (Random.value)
  ↓
next block
```

Khi online, mỗi tiến trình sẽ rút số ngẫu nhiên của riêng nó, nên mỗi người chơi sẽ chạy trên mặt đất khác nhau và server sẽ mô phỏng một level không ai thấy. Chỉ dựng level quanh một nhân vật cũng không được, vì server không có một nhân vật duy nhất để đi theo.

Server có thể gửi từng khối, nhưng không cần. Nếu server và mọi client chạy cùng code bố trí với cùng một seed, chỉ seed cần đi qua mạng.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [State](../../../synchronization/state.md)
- [Scene object](../../../objects/spawning.md#scene-objects)
- [Model và codec](../../../messaging/models.md)
- [Channel và độ tin cậy](../../../messaging/channels.md)

## Thiết kế <a href="#design" id="design"></a>

```
Server                                  Client
OnStartServer                           OnStartClient / state callback
  ↓                                       ↓
Seed = random                           Seed from LevelState
  ↓                                       ↓
TerrainGenerator.Build(seed)            TerrainGenerator.Build(seed)
  ↓                                       ↓
22 foreground blocks                    the same 22 blocks
         ── LevelState { Seed } ──→
```

`TerrainGenerationSettings.Layout(seed)` biến một seed thành danh sách khối bằng một `System.Random` riêng, nên code khác rút số từ `UnityEngine.Random` không thể làm thay đổi bố trí, và `TerrainGenerator.Build` tạo toàn bộ tiền cảnh một lần. Phần nền gồm đồi và mây không bao giờ chạm vào nhân vật, nên nó vẫn ngẫu nhiên và chỉ được dựng trên client, quanh người chơi cục bộ.

Seed là một state field của `NetworkLevel`, một `NetworkBehaviour` trên một scene object, và package sinh một model, `LevelState`, từ field đó. Package spawn scene object khi server khởi động và gửi state của chúng tới mọi client tham gia, nên seed tới được người vào muộn mà không cần code thêm.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/TerrainGeneration/LevelBlock.cs
Assets/Scripts/RedRunner/TerrainGeneration/TerrainGenerationSettings.cs
Assets/Scripts/RedRunner/TerrainGeneration/TerrainGenerator.cs
Assets/Generation Settings.asset
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scenes/Play.unity
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Bố trí level từ seed <a href="#lay-out-the-level-from-a-seed" id="lay-out-the-level-from-a-seed"></a>

`TerrainGenerationSettings` đã liệt kê các khối bắt đầu, giữa và kết thúc cùng số lượng mỗi loại. Giờ nó có thêm một method biến seed thành bố trí:

```csharp
public List<LevelBlock> Layout ( int seed )
{
	if ( m_StartBlocksCount <= 0 || m_MiddleBlocksCount <= 0 || m_EndBlocksCount <= 0 )
	{
		throw new System.InvalidOperationException ( name + " needs positive start, middle and end block counts to lay out a seeded level" );
	}
	System.Random random = new System.Random ( seed );
	List<LevelBlock> layout = new List<LevelBlock> ();
	float x = 0f;
	AddBlocks ( layout, m_StartBlocks, m_StartBlocksCount, LevelPart.Start, random, ref x );
	AddBlocks ( layout, m_MiddleBlocks, m_MiddleBlocksCount, LevelPart.Middle, random, ref x );
	AddBlocks ( layout, m_EndBlocks, m_EndBlocksCount, LevelPart.End, random, ref x );
	return layout;
}
```

`AddBlocks` chọn từng khối bằng `TerrainGenerator.ChooseFrom ( blocks, ( float )random.NextDouble () )`, một overload mới nhận giá trị ngẫu nhiên làm tham số, và `ChooseFrom ( blocks )` gốc giờ truyền `Random.value` vào nó. `LevelBlock` là một struct nhỏ giữ prefab của khối, vị trí x và phần level của nó.

### Dựng level một lần <a href="#build-the-level-once" id="build-the-level-once"></a>

Trước đây `Generate` thêm khối tiền cảnh tiếp theo trong lúc nhân vật chạy. Giờ `Build` tạo mọi khối của bố trí và bỏ qua các lần gọi sau, còn `Generate` chỉ lo phần nền:

```csharp
public virtual void Build ( int seed )
{
	if ( m_Built )
	{
		return;
	}
	m_Built = true;
	foreach ( LevelBlock levelBlock in m_Settings.Layout ( seed ) )
	{
		if ( levelBlock.Part == LevelPart.End && m_EndX <= 0f )
		{
			m_EndX = levelBlock.X;
		}
		CreateBlock ( levelBlock.Prefab, new Vector3 ( levelBlock.X, 0f, 0f ) );
	}
}
```

`Generate` return sớm khi không có nhân vật để đi theo, và `Follow ( Character )` đặt một nhân vật; bước 05 gọi nó với người chơi cục bộ. `EndX`, nơi khối kết thúc bắt đầu, được dùng ở bước 06. `TerrainGenerator` không còn subscribe `GameManager.OnReset`, vì level giờ tồn tại suốt thời gian server chạy.

### Làm level hữu hạn <a href="#make-the-level-finite" id="make-the-level-finite"></a>

Trong `Assets/Generation Settings.asset`, đặt Middle Blocks Count thành 20 và End Blocks Count thành 1. Project không có prefab khối kết thúc, nên hãy thêm `Assets/Prefabs/Blocks/Start.prefab` vào End Blocks, khiến level kết thúc trên chính nền bắt đầu. Với các số lượng vô tận ban đầu, `Layout` ném exception.

### Giữ seed trên một network object <a href="#keep-the-seed-on-a-network-object" id="keep-the-seed-on-a-network-object"></a>

`Assets/Scripts/RedRunner/Networking/NetworkLevel.cs`, viết cho `com.fomoxa.networking` 0.5.0:

```csharp
[NetworkStateModel("LevelState")]
public sealed partial class NetworkLevel : NetworkBehaviour
{
    [SerializeField]
    private TerrainGenerator m_Generator;

    [NetworkState(OnChanged = nameof(OnSeedChanged))]
    private uint seed;

    public uint Seed => seed;

    public TerrainGenerator Generator => m_Generator;

    public override void OnStartServer()
    {
        seed = (uint)new System.Random().Next(1, int.MaxValue);
        Build();
    }

    public override void OnStartClient()
    {
        Build();
    }

    private void OnSeedChanged(uint previous, uint current) => Build();

    private void Build()
    {
        if (seed != 0)
        {
            m_Generator.Build((int)seed);
        }
    }
}
```

`[NetworkState]` đưa `seed` vào state của object. Sau lần biên dịch tiếp theo, package ghi một model có field `Seed` vào `Networking/Generated/StateModels/LevelState.cs`, và Unity biên dịch lại; Play Mode bị chặn cho tới khi model đó tồn tại. Class là `partial` vì một source generator trong package thêm code copy field sang model và ngược lại. State luôn đi trên channel reliable ordered.

`[NetworkStateModel("LevelState")]` đặt tên cho model, nếu không nó sẽ là `NetworkLevelState`. Console server ở [bước 13](../rapier-and-console/step-13-console-server.md) biên dịch cùng model sinh ra và nhận ra nó qua một message id suy ra từ tên, nên tên được đặt ở đây, trước khi có gì phụ thuộc vào nó. Field không có tiền tố `m_` vì field của model lấy tên từ nó: `seed` thành `Seed`.

Trên server, `OnStartServer` chọn seed và dựng level. Trên client, package đã ghi seed nhận được vào `seed` trước khi gọi `OnStartClient`. `OnChanged` lo trường hợp seed tới muộn hơn: package ghi field, rồi gọi `OnSeedChanged` với giá trị cũ và mới. Ở host mode, server và client dùng chung một instance, và lần `Build` thứ hai return ngay.

Trong `Play.unity`, tạo một GameObject ở gốc tên `Network Level` có `NetworkObject` và `NetworkLevel`, đặt object `Terrain Generator` vào field Generator và lưu scene, việc này gán cho `NetworkObject` một scene object id. Package tắt scene object khi scene load và bật chúng khi chúng spawn, nên level giữ trống cho tới khi server khởi động.

## Test <a href="#test" id="test"></a>

Chưa có gì khởi động server, nên hãy khởi động một server từ một component tạm trong Play Mode:

```csharp
server.ServerManager.StartConnection(0);
```

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Ở frame tiếp theo, `NetworkLevel.Seed` khác 0 và generator báo `IsBuilt`.
- Scene chứa 22 khối tiền cảnh ở đúng các vị trí mà `Settings.Layout(seed)` liệt kê.
- `Layout` trả về cùng các khối với cùng seed và các khối khác với seed khác.

Bài kiểm tra riêng của bản port là `Tools/PortChecks/LevelCheck.cs`.

## Commit <a href="#commit" id="commit"></a>

```
Commit: 0b9d85f
Message: Build a finite level from a seed kept on a network object
```

Xem [`0b9d85f`](https://github.com/fomoxa/RedRunner/commit/0b9d85fb089698c82ec0bcfccede2d7b59028482) trên GitHub. Commit đó khai báo `LevelState` bằng tay với API 0.3, và [`1c1ded1`](https://github.com/fomoxa/RedRunner/commit/1c1ded158105091902d8d352157856eacf0cbc73) chuyển nó sang một field.

Tiếp tục với [bước 03: spawn người chơi](step-03-player-spawning.md).
