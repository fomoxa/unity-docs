# Project

Server console là một project console .NET thông thường, biên dịch file mã nguồn từ package và từ project Unity thay vì tham chiếu assembly đã build. Trang này dựng một project như vậy.

## Bố cục thư mục <a href="#folder-layout" id="folder-layout"></a>

Project cần ba thư mục trên đĩa: package `com.fomoxa.networking`, project Unity và project console. Các ví dụ trên trang này đặt chúng cạnh nhau:

```text
com.fomoxa.networking/        clone of https://github.com/fomoxa/com.fomoxa.networking
MyGame/                       the Unity project
    Assets/Network/Models/
    Assets/Network/Generated/
    Server~/                  the console project
        MyGame.Server.csproj
        Program.cs
```

Unity bỏ qua thư mục có tên kết thúc bằng `~`, nên `Server~` bên trong project Unity không bị import và các thư mục `bin`, `obj` của nó không làm phiền Editor.

## File project <a href="#the-project-file" id="the-project-file"></a>

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <Nullable>disable</Nullable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <Game>..</Game>
    <Core Condition="'$(Core)' == ''">$(Game)/../com.fomoxa.networking</Core>
  </PropertyGroup>

  <ItemGroup>
    <Compile Include="$(Core)/Runtime/Core/**/*.cs" />
    <Compile Include="$(Core)/Standalone~/**/*.cs" />
    <Compile Include="$(Game)/Assets/Network/Models/**/*.cs" />
    <Compile Include="$(Game)/Assets/Network/Generated/**/*.cs" />
    <Compile Include="*.cs" />
  </ItemGroup>

  <ItemGroup>
    <None Include="$(Game)/Assets/Network/Generated/*.fomoxascene" Link="Scenes/%(Filename)%(Extension)" CopyToOutputDirectory="PreserveNewest" />
  </ItemGroup>

  <ItemGroup>
    <Reference Include="Fomoxa.Attributes">
      <HintPath>$(Core)/Runtime/Plugins/Fomoxa.Attributes.dll</HintPath>
    </Reference>
    <Reference Include="Fomoxa.Net">
      <HintPath>$(Core)/Runtime/Plugins/Fomoxa.Net.dll</HintPath>
    </Reference>
  </ItemGroup>

</Project>
```

| Phần | Lý do |
|---|---|
| `EnableDefaultCompileItems` false | Project tự liệt kê mã nguồn của nó, nên không lấy nhầm script của project Unity |
| `Core` | Thư mục của package. Điều kiện cho phép truyền thư mục khác bằng `-p:Core=<folder>` |
| `Runtime/Core/**` và `Standalone~/**` | Tầng 1 và backend console, dưới dạng mã nguồn |
| Models và Generated | Model của bạn và codec, adapter, hằng số `FomoxaPrefabs` và `FomoxaScenes` được sinh ra |
| `*.fomoxascene` | Các scene file, copy vào thư mục `Scenes` cạnh file chạy |
| `Fomoxa.Attributes`, `Fomoxa.Net` | Các DLL đi kèm, tham chiếu từ package |

File `FomoxaUnityRegistration.cs` được sinh ra sẽ biên dịch thành rỗng bên ngoài Unity, nên chương trình console tự gọi `FomoxaAdapters.RegisterAll`, như trang sau cho thấy. Model dùng type của Unity như `UnityEngine.Vector3`, cùng codec của chúng trong `UnityCodecs/`, không biên dịch được khi không có Unity. Hãy cho các model mà server console cần dùng field thông thường.

## Code game dùng chung với Unity <a href="#game-code-shared-with-unity" id="game-code-shared-with-unity"></a>

Code mà cả game Unity và server console cùng chạy, như luật di chuyển hay bộ sinh level, có thể nằm trong một assembly của project Unity có assembly definition đặt `noEngineReferences`. Project console khi đó biên dịch cả thư mục đó:

```xml
<Compile Include="$(Game)/Assets/Scripts/Simulation/**/*.cs" />
```

Code như vậy không được dùng `UnityEngine` và phải viết bằng C# 9.

## RPC khai báo bằng attribute <a href="#rpcs-declared-with-attributes" id="rpcs-declared-with-attributes"></a>

Source generator cho RPC xử lý `EntityBehaviour` cũng như `NetworkBehaviour`. Để dùng `[ServerRpc]` và `[ClientRpc]` trong project console, hãy tham chiếu nó như một analyzer:

```xml
<ItemGroup>
  <Analyzer Include="$(Core)/Runtime/Core/Generators/Fomoxa.Networking.Generators.dll" />
</ItemGroup>
```

Nếu không, hãy đăng ký RPC trong `OnRegisterRpcs`, như mô tả trong [RPC](../messaging/rpc.md).

## Build và chạy <a href="#building-and-running" id="building-and-running"></a>

```
dotnet run --project Server~ -c Release
```

Khi package nằm ở chỗ khác, hãy truyền thư mục của nó: `dotnet run --project Server~ -c Release -p:Core=/path/to/com.fomoxa.networking`. Mỗi lần model hoặc scene thay đổi trong Unity, hãy để Editor sinh code và xuất scene file, rồi build lại project console; server và client build từ model khác nhau sẽ thất bại ở handshake với `SchemaConflict`.

Trang [runtime](runtime.md) viết `Program.cs`.
