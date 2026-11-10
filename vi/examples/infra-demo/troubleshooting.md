# 07: Xử lý sự cố

Cách dùng: tìm triệu chứng của bạn → đọc nguyên nhân → chạy cách xử lý. Nếu chưa biết lỗi nằm ở đâu, chạy [bộ lệnh chẩn đoán nhanh](#quick-diagnostic-commands) trước.

Mục lục: [Chẩn đoán nhanh](#quick-diagnostic-commands) · [Docker, k3d, kubectl](#1-docker-k3d-kubectl) · [Pod và image](#2-pods-and-images) · [Agones và game server](#3-agones-and-game-servers) ·
[Nakama](#4-nakama) · [Backend và tài khoản](#5-backend-and-accounts) · [Kết nối của client](#6-client-connection) · [TLS](#7-tls) · [Giám sát, NetworkPolicy](#8-monitoring-and-networkpolicy) · [Cụm giả và kiểm thử](#9-mock-cluster-and-tests)

## Bộ lệnh chẩn đoán nhanh <a href="#quick-diagnostic-commands" id="quick-diagnostic-commands"></a>

```bash
kubectl config current-context                       # must be k3d-fomoxa
kubectl get nodes
kubectl get pods -A | grep -vE 'Running|Completed'   # every pod in any namespace that is NOT in a good state
kubectl get pods,svc -n fomoxa
kubectl get fleet,gs -n fomoxa
kubectl get events -n fomoxa --sort-by=.lastTimestamp | tail -15
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
docker port k3d-fomoxa-serverlb
free -h
```

Cách đọc: dòng đầu phải ra `k3d-fomoxa`; lệnh thứ ba nên rỗng (hoặc chỉ có pod đang khởi động); `docker port` phải có `7777/udp`, `9600`, `9643`, `7350`; `free -h` cột `available` dưới ~2 GB là nguy hiểm.

## 1. Docker, k3d, kubectl <a href="#1-docker-k3d-kubectl" id="1-docker-k3d-kubectl"></a>

### `Cannot connect to the Docker daemon` <a href="#cannot-connect-to-the-docker-daemon" id="cannot-connect-to-the-docker-daemon"></a>
- Nguyên nhân: WSL2: Docker Desktop chưa chạy hoặc chưa bật WSL Integration. Linux: dịch vụ docker chưa chạy.
- Xử lý: WSL2: mở Docker Desktop → *Settings → Resources → WSL Integration* → bật cho Ubuntu → *Apply & Restart*. Linux: `sudo systemctl start docker`.
- Kiểm tra: `docker info --format '{{.ServerVersion}}'` in được phiên bản.

### `permission denied while trying to connect to the Docker daemon socket` <a href="#permission-denied-while-trying-to-connect-to-the-docker-daemon-socket" id="permission-denied-while-trying-to-connect-to-the-docker-daemon-socket"></a>
- Xử lý: `sudo usermod -aG docker "$USER" && newgrp docker` (hoặc đăng xuất/đăng nhập lại).

### `port is already allocated` / không tạo được cluster <a href="#port-is-already-allocated-or-the-cluster-cannot-be-created" id="port-is-already-allocated-or-the-cluster-cannot-be-created"></a>
- Nguyên nhân: 7777/9600/9643/7350 đã bị giữ (compose Nakama, cụm cũ, cụm giả, ứng dụng khác).
- Xử lý:

```bash
docker ps --format '{{.Names}}\t{{.Ports}}' | grep -E ':(7777|9600|9643|7350)->'      # which container holds it?
ss -ltnup | grep -E ':(7777|9600|9643|7350)\b'                                          # which process holds it?
docker compose -f deploy/compose.yaml down        # if it is the compose Nakama
k3d cluster delete fomoxa                         # if it is an old cluster
```

### `kubectl` báo sai/không thấy tài nguyên <a href="#kubectl-shows-the-wrong-thing-or-finds-no-resources" id="kubectl-shows-the-wrong-thing-or-finds-no-resources"></a>
- Nguyên nhân: `kubectl` đang trỏ cluster khác (rất hay gặp khi có nhiều cluster).
- Xử lý: `kubectl config get-contexts` rồi `kubectl config use-context k3d-fomoxa`. Mọi lệnh nên kèm `-n fomoxa` (hoặc đặt mặc định: `kubectl config set-context --current --namespace=fomoxa`).

### `k3d image import` chạy rất lâu <a href="#k3d-image-import-takes-very-long" id="k3d-image-import-takes-very-long"></a>
- Bình thường với image vài trăm MB; đợi. Kiểm tra: `docker exec k3d-fomoxa-server-0 crictl images | grep fomoxa`.

### Cluster đã tạo mà thiếu cổng (client không nối được 9600/7777) <a href="#the-cluster-is-missing-ports-the-client-cannot-reach-9600-or-7777" id="the-cluster-is-missing-ports-the-client-cannot-reach-9600-or-7777"></a>
- Nguyên nhân: k3d chỉ nhận `--port` lúc tạo cluster.
- Xử lý: xoá và tạo lại: `k3d cluster delete fomoxa` rồi lặp [03, Bước 5-9](deploy/03-cluster-and-agones.md#step-5-create-the-k3d-cluster).

## 2. Pod và image <a href="#2-pods-and-images" id="2-pods-and-images"></a>

| Trạng thái pod | Nguyên nhân thường gặp | Xử lý |
|---|---|---|
| `ImagePullBackOff` / `ErrImagePull` | image `fomoxa-*:latest` chưa có trong k3d (chúng không có trên Docker Hub) | `k3d image import fomoxa-<tên>:latest -c fomoxa`, rồi `kubectl rollout restart deployment/<tên> -n fomoxa` |
| `CreateContainerConfigError` | thiếu secret hoặc thiếu khoá trong secret | `kubectl describe pod <pod> -n fomoxa` (dòng `Error:` ghi rõ secret/khoá thiếu); làm lại [03, Bước 8](deploy/04-secrets.md#step-8-namespace-and-secrets) |
| `CrashLoopBackOff` | ứng dụng thoát ngay | `kubectl logs <pod> -n fomoxa --previous` đọc lý do |
| `Pending` rất lâu | thiếu CPU/RAM trong node | `kubectl describe pod <pod> -n fomoxa` (mục *Events*: `Insufficient memory`); giảm số pod (`kubectl scale fleet ... --replicas=2`) hoặc tăng RAM Docker/WSL2 |
| `Init:Error` (nakama) | initContainer `migrate` không nối được Postgres | xem mục [Nakama](#4-nakama) |
| `Evicted` / `OOMKilled` | hết bộ nhớ, bị giới hạn `limits` | `kubectl describe pod ...` mục *Last State*; tăng RAM máy hoặc nới `limits` trong manifest |

Sau mỗi lần build lại image: nhớ import + restart. Với Fleet phải xoá và apply lại ([05](operations/01-status-and-updates.md#updating-after-rebuilding-an-image)). Dấu hiệu quên: sửa mã xong mà hành vi không đổi.

## 3. Agones và game server <a href="#3-agones-and-game-servers" id="3-agones-and-game-servers"></a>

### `helm repo add` báo 404 <a href="#helm-repo-add-returns-404" id="helm-repo-add-returns-404"></a>
- Dùng nhầm URL cũ. Đúng: `helm repo add agones https://agones.dev/chart/stable --force-update`.

### `helm install` hết giờ (`timed out waiting for the condition`) <a href="#helm-install-times-out-timed-out-waiting-for-the-condition" id="helm-install-times-out-timed-out-waiting-for-the-condition"></a>
- Nguyên nhân: pod Agones chưa lên (kéo image chậm), hoặc allocator tranh cổng 443 với Traefik (đã tắt bằng `agones.allocator.install=false`).
- Xử lý:

```bash
kubectl get pods -n agones-system
kubectl describe pod <pod> -n agones-system | tail -20
helm uninstall agones -n agones-system && helm install agones agones/agones --namespace agones-system \
    --set "agones.allocator.install=false" --set "agones.ping.install=false" --wait --timeout 10m
```

### GameServer mãi ở `Starting`, không lên `Ready` <a href="#a-gameserver-stays-in-starting-and-never-reaches-ready" id="a-gameserver-stays-in-starting-and-never-reaches-ready"></a>
- Nguyên nhân: container game không gọi được sidecar Agones hoặc không nối được directory.
- Xử lý:

```bash
GS=$(kubectl get gs -n fomoxa -o name | head -1 | cut -d/ -f2)
kubectl logs "$GS" -n fomoxa -c fomoxa-server --tail=30
kubectl logs "$GS" -n fomoxa -c agones-gameserver-sidecar --tail=30
```

  Tìm: `Connection refused` tới `directory...:9500` (directory chưa lên / khoá `pod` lệch giữa `fomoxa-pod-key` và `fomoxa-directory-keys`); `ReadyAsync attempt ...` (sidecar chưa sẵn sàng, đợi 30 giây).

### Game server `Ready` nhưng không bao giờ `Allocated` <a href="#a-game-server-is-ready-but-never-allocated" id="a-game-server-is-ready-but-never-allocated"></a>
- Nguyên nhân: chưa có người chơi nào thật sự nối UDP vào pod. `Allocated` chỉ xảy ra khi người chơi đầu tiên kết nối (không phải khi có người xin phòng).
- Xử lý: xem [client không nối được](#6-client-connection). Log pod phải có `[Pod] peer N la '<tên>'` rồi `[Agones] first player joined -> Allocate`.

### Pod `Shutdown` sau ~30 giây khi mọi người rời <a href="#a-pod-goes-to-shutdown-about-30-seconds-after-everyone-leaves" id="a-pod-goes-to-shutdown-about-30-seconds-after-everyone-leaves"></a>
- Không phải lỗi. Phòng trống 30 giây thì pod tự tắt (`[Agones] room empty, shutting down`) và Fleet tạo pod mới `Ready`. Người quay lại trong 30 giây thì việc tắt bị huỷ.

### Nhiều pod nhưng chỉ có vài phòng <a href="#many-pods-but-few-rooms" id="many-pods-but-few-rooms"></a>
- Mỗi pod giữ một phòng trong `arena:1..16`. Quá 16 pod thì pod thừa không có phòng (không dùng được). Đừng đặt `maxReplicas` > 16 nếu không mở rộng `FOMOXA_ROOM` trong `fleet.yaml`.

## 4. Nakama <a href="#4-nakama" id="4-nakama"></a>

### `lua runtime error` / RPC trả lỗi lạ <a href="#lua-runtime-error-or-an-rpc-returns-a-strange-error" id="lua-runtime-error-or-an-rpc-returns-a-strange-error"></a>
```bash
kubectl logs deploy/nakama -n fomoxa | grep -iE 'lua|error' | tail
```
- Nguyên nhân thường gặp: sửa `main.lua` nhưng quên cập nhật ConfigMap trong `nakama.yaml` (hoặc ngược lại), hoặc lỗi cú pháp Lua.
- Xử lý: bắt lỗi lệch bằng [kiểm tra tĩnh](testing.md#5-static-checks-generated-code-yaml-shell-lua-monitoring-config); sau khi sửa `kubectl apply -f deploy/k8s/nakama.yaml && kubectl rollout restart deployment/nakama -n fomoxa`.

### Ghép trận: một người `waiting` mãi <a href="#matchmaking-one-player-stays-waiting" id="matchmaking-one-player-stays-waiting"></a>
- Nguyên nhân: phòng cụ thể (ví dụ `arena:1`) cần đúng 2 người cùng xin phòng đó trong vòng 30 giây; hoặc hai người xin hai phòng khác nhau; hoặc hàng chờ cũ chưa xoá.
- Xử lý: dùng "Tự động ghép trận" (`auto`); hoặc xoá hàng chờ bằng `reset_match` (cần `http_key`), xem [03, Bước 12.2](deploy/07-test-nakama.md#step-12-test-nakama-with-curl).

### Người vừa chơi xong xin phòng khác lại bị đưa vào phòng cũ <a href="#a-player-who-just-finished-a-match-asks-for-another-room-and-lands-in-the-old-one" id="a-player-who-just-finished-a-match-asks-for-another-room-and-lands-in-the-old-one"></a>
- Đã sửa trong `main.lua` (poll không còn trả kết quả của trận cũ). Nếu còn gặp, kiểm tra Nakama đang chạy đúng bản `main.lua` mới (so ConfigMap, restart Nakama).

### `401 Unauthorized` khi gọi Nakama <a href="#401-unauthorized-from-nakama" id="401-unauthorized-from-nakama"></a>
- Sai `server-key`/`http-key`. Cụm K8s dùng khoá riêng trong secret `fomoxa-nakama`; `docker compose` dùng `defaultkey`/`defaulthttpkey`. Xem [03, Bước 12](deploy/07-test-nakama.md#step-12-test-nakama-with-curl).

### `{"code":7,...,"message":"chi backend duoc goi RPC nay"}` <a href="#code7messagechi-backend-duoc-goi-rpc-nay" id="code7messagechi-backend-duoc-goi-rpc-nay"></a>
- Không phải lỗi. Người chơi (token Bearer) không được gọi các RPC nội bộ; chỉ backend (có `http_key`) gọi được.

### Đổi mật khẩu DB làm Nakama không khởi động <a href="#changing-the-db-password-stops-nakama-from-starting" id="changing-the-db-password-stops-nakama-from-starting"></a>
- Triệu chứng: pod `nakama` `Init:Error`/`CrashLoopBackOff`, log `password authentication failed for user "postgres"`.
- Nguyên nhân: mật khẩu `postgres` được lưu trong volume dữ liệu ngay lần khởi tạo đầu; đổi secret `db-password` sau đó không đổi mật khẩu thật trong CSDL.
- Xử lý (mất dữ liệu):

```bash
kubectl delete deployment nakama postgres -n fomoxa
kubectl delete pvc postgres-data -n fomoxa
kubectl apply -f deploy/k8s/postgres.yaml -f deploy/k8s/nakama.yaml
```

  Hoặc giữ dữ liệu: đặt lại secret về giá trị cũ (file `deploy/secrets/nakama/db-password` cũ), hoặc vào Postgres đổi mật khẩu trước: `kubectl exec -n fomoxa deploy/postgres -- psql -U postgres -c "ALTER USER postgres PASSWORD '<mật-khẩu-mới>';"` rồi mới cập nhật secret.

### Console Nakama (7351) không vào được <a href="#the-nakama-console-7351-is-unreachable" id="the-nakama-console-7351-is-unreachable"></a>
- Console không mở ra ngoài. Dùng `kubectl port-forward -n fomoxa svc/nakama-console 7351:7351`, mật khẩu trong secret (xem [05, mục 2](operations/01-status-and-updates.md#2-reaching-internal-services)).

## 5. Backend và tài khoản <a href="#5-backend-and-accounts" id="5-backend-and-accounts"></a>

### Đăng nhập báo "kho tài khoản không trả lời" / "Nakama không trả lời" <a href="#login-says-the-account-store-or-nakama-is-not-responding" id="login-says-the-account-store-or-nakama-is-not-responding"></a>
- Backend không nói chuyện được với Nakama (tài khoản lưu trong Nakama storage).
- Xử lý: `kubectl get pods -n fomoxa | grep nakama`; `kubectl logs deploy/backend -n fomoxa | grep -i nakama`; kiểm `Fomoxa__Nakama__HttpKey` của backend trùng `http-key` trong secret (backend lấy từ cùng secret `fomoxa-nakama` nên chỉ lệch khi bạn sửa tay).

### "Nakama đang bật: hãy đăng nhập bằng tài khoản" <a href="#nakama-đang-bật-hãy-đăng-nhập-bằng-tài-khoản-nakama-is-on-log-in-with-an-account" id="nakama-đang-bật-hãy-đăng-nhập-bằng-tài-khoản-nakama-is-on-log-in-with-an-account"></a>
- Backend có Nakama từ chối đăng nhập chỉ bằng tên. Dùng thẻ Đăng ký/Đăng nhập (mật khẩu), hoặc kiểu khách `-autojoin ... -device:<id>`.

### "tên này đã có người dùng" / "sai tên hoặc mật khẩu" / "thử sai quá nhiều lần" <a href="#tên-này-đã-có-người-dùng-sai-tên-hoặc-mật-khẩu-or-a-too-many-tries-lock" id="tên-này-đã-có-người-dùng-sai-tên-hoặc-mật-khẩu-or-a-too-many-tries-lock"></a>
- Tên đã đăng ký (không phân biệt hoa thường) / sai mật khẩu / 5 lần sai liên tiếp → khoá tên đó 60 giây (đợi một phút).

### Quên mật khẩu và mất mã khôi phục <a href="#forgot-the-password-and-lost-the-recovery-code" id="forgot-the-password-and-lost-the-recovery-code"></a>
- Không có công cụ đặt lại thủ công. Cách tạm: xoá bản ghi `account` của tên đó trong console Nakama (*Storage*) để đăng ký lại ([05, mục 7](operations/02-drain-and-accounts.md#7-accounts-and-player-data)).

### Mã khôi phục không hiện sau khi đăng ký <a href="#the-recovery-code-does-not-show-after-registering" id="the-recovery-code-does-not-show-after-registering"></a>
- Mã chỉ lưu tạm 10 phút trong bộ nhớ backend và client lấy một lần ngay sau đăng ký. Nếu client đóng ngay hoặc backend restart đúng lúc đó thì mất. Dùng đổi mật khẩu (khi còn đăng nhập) hoặc đăng ký tài khoản khác.

### Bảng điểm trống / kỷ lục không lưu <a href="#the-scoreboard-is-empty-or-records-are-not-saved" id="the-scoreboard-is-empty-or-records-are-not-saved"></a>
- Pod phải nối được backend ở cổng 9602 (log pod phải có `[Backend] da ket noi`). Không có → kiểm secret `fomoxa-backend-pod-key` và Service `backend-pods`: `kubectl get svc backend-pods -n fomoxa`.
- Người chơi khách (không tài khoản) vẫn lên bảng điểm nhưng kỷ lục không được lưu.

## 6. Kết nối của client <a href="#6-client-connection" id="6-client-connection"></a>

### Đăng nhập được nhưng vào phòng thì treo ở "Đang kết nối game server" <a href="#login-works-but-joining-a-room-hangs-at-connecting-to-the-game-server" id="login-works-but-joining-a-room-hangs-at-connecting-to-the-game-server"></a>
- Nguyên nhân thường gặp nhất: `public_address` sai. Directory trả về địa chỉ này cho client; chạy local phải là `127.0.0.1:7777`.
- Xử lý:

```bash
kubectl get configmap directory-config -n fomoxa -o jsonpath='{.data.directory\.toml}' | grep public_address
docker port k3d-fomoxa-serverlb | grep 7777
```

  Phải có `public_address = "127.0.0.1:7777"` và `7777/udp -> 0.0.0.0:7777`. Client ở máy khác: xem [05, mục 14](operations/05-scaling-security-backup.md#14-changing-the-public-address-publicaddress).

### Client Windows không nối được cụm trong WSL2 <a href="#a-windows-client-cannot-reach-a-cluster-in-wsl2" id="a-windows-client-cannot-reach-a-cluster-in-wsl2"></a>
- Triệu chứng: TCP 9600 đăng nhập được nhưng UDP 7777 không tới.
- Nguyên nhân: chuyển tiếp `localhost` của WSL2 không đáng tin với UDP. Docker Desktop (WSL Integration) publish cổng container ra thẳng `localhost` của Windows, kể cả UDP.
- Xử lý: dùng Docker Desktop thay vì Docker Engine tự cài trong WSL2 ([01, Bước 3A](getting-started/prepare-environment.md#3a-wsl2-ubuntu-on-windows-docker-desktop)); kiểm tra từ PowerShell Windows `Test-NetConnection 127.0.0.1 -Port 9600`. Cách khác: chạy client trong WSL2/Linux hoặc dùng cụm giả ([02](getting-started/quickstart-mock-cluster.md)).

### "Không có game server chạy phiên bản X" <a href="#không-có-game-server-chạy-phiên-bản-x-no-game-server-runs-version-x" id="không-có-game-server-chạy-phiên-bản-x-no-game-server-runs-version-x"></a>
- Phiên bản client (`Player Settings → Version`, mặc định `1.0`) khác `FOMOXA_VERSION` của pod (`fleet.yaml`, mặc định `1.0`). Directory chỉ ghép pod cùng phiên bản (`filter = "pod.version == client.version"`). Cụm giả mặc định bỏ qua kiểm tra này.

### Lỗi bắt tay giao thức ("handshake failed" / "schema"), bản `MyGame.exe` cũ không vào được <a href="#handshake-or-schema-errors-an-old-mygameexe-cannot-get-in" id="handshake-or-schema-errors-an-old-mygameexe-cannot-get-in"></a>
- Bản build client cũ lệch "vân tay giao thức" với backend/pod mới. Build lại cả ba cùng lúc ([04, Sinh lại mã](unity-client.md#regenerating-code-after-changing-a-model-or-rpc)).

### Vào được phòng nhưng không thấy người khác / không có nhân vật <a href="#you-enter-a-room-but-see-nobody-or-have-no-character" id="you-enter-a-room-but-see-nobody-or-have-no-character"></a>
- Prefab chưa đăng ký với `NetworkManager`: chạy lại Tools → Demo → Rebuild Scene; Console không được có `[Demo] prefab:` lỗi ([04](unity-client.md#step-2-build-the-two-scenes-rebuild-scene)).

### Space làm thoát phòng <a href="#space-leaves-the-room" id="space-leaves-the-room"></a>
- HUD đang hiện và nút giữ focus. Bản hiện tại ẩn HUD khi đang chơi và các nút không nhận focus bàn phím; nếu vẫn gặp, build lại client từ mã mới nhất.

### Camera không đi theo nhân vật <a href="#the-camera-does-not-follow-the-character" id="the-camera-does-not-follow-the-character"></a>
- Console: có `[Player] spawn on client ... mine=True` không? Nếu không thì nhân vật của bạn chưa spawn (kết nối chưa vào pod). Dòng `[Camera] chưa thấy nhân vật của mình sau 8 giây` xác nhận điều đó.

## 7. TLS <a href="#7-tls" id="7-tls"></a>

| Triệu chứng | Nguyên nhân | Xử lý |
|---|---|---|
| "không kết nối được backend: TlsRejected (vân tay chứng chỉ ... không khớp)" | pin trong client khác chứng chỉ server đang trình | lấy pin đúng: `openssl s_client -connect 127.0.0.1:9643 </dev/null 2>/dev/null \| openssl x509 -noout -fingerprint -sha256`, bỏ dấu `:`; hoặc `./scripts/gen-tls-cert.sh` in pin của file hiện có. Chứng chỉ đã tạo lại thì phải cập nhật pin ở mọi client |
| "không kết nối được backend: Failed" khi dùng `-backend:...:9643` | proxy TLS không chạy hoặc cổng 9643 chưa được map | `kubectl get pods -n fomoxa \| grep tls-proxy`; `docker port k3d-fomoxa-serverlb \| grep 9643` (cluster tạo trước khi có cổng 9643 thì phải tạo lại) |
| `tls-proxy` `CrashLoopBackOff` | thiếu/sai secret `fomoxa-tls` | `kubectl get secret fomoxa-tls -n fomoxa`; tạo lại ([03, Bước 8](deploy/04-secrets.md#step-8-namespace-and-secrets)) |
| Muốn dùng chứng chỉ CA thật nhưng client vẫn đòi pin | để trống pin, truyền `-tls` | [05, mục 8.4](operations/03-tls-and-keys.md#84-production-with-a-domain-name) |

## 8. Giám sát và NetworkPolicy <a href="#8-monitoring-and-networkpolicy" id="8-monitoring-and-networkpolicy"></a>

### Prometheus target `DOWN` hoặc không có target <a href="#a-prometheus-target-is-down-or-there-are-no-targets" id="a-prometheus-target-is-down-or-there-are-no-targets"></a>
- Nguyên nhân: pod thiếu annotation `prometheus.io/scrape: "true"`; hoặc NetworkPolicy chặn namespace `monitoring`; hoặc pod chưa mở cổng metrics.
- Xử lý: `kubectl get pod <pod> -n fomoxa -o jsonpath='{.metadata.annotations}'`; trong pod: `kubectl exec -n fomoxa deploy/backend -- ...` (backend: cổng 9610), game server (cổng 9611). Nếu đã bật NetworkPolicy, policy `metrics-from-monitoring` phải có (xem `deploy/k8s/networkpolicy.yaml`).

### Sau khi bật NetworkPolicy có thứ không nối được <a href="#something-stopped-connecting-after-turning-on-networkpolicy" id="something-stopped-connecting-after-turning-on-networkpolicy"></a>
- Gỡ ngay để xác nhận nguyên nhân: `kubectl delete -f deploy/k8s/networkpolicy.yaml`. Nếu hết lỗi thì policy thiếu một luồng; xem bảng luồng ở đầu file đó.

### Grafana không có dữ liệu <a href="#grafana-shows-no-data" id="grafana-shows-no-data"></a>
- *Connections → Data sources → Prometheus → Save & test*; kiểm tra Prometheus `Status → Targets` trước.

## 9. Cụm giả và kiểm thử <a href="#9-mock-cluster-and-tests" id="9-mock-cluster-and-tests"></a>

| Triệu chứng | Xử lý |
|---|---|
| `Address already in use` khi chạy cụm giả | `ss -ltnp \| grep -E '9600\|9500\|9643\|9602'`; tắt cụm giả/ cụm k3d đang chạy; hoặc đổi cổng bằng `--players=`, `--directory=`... |
| `--selftest` thất bại ở "Dang ky trung ten" khi chạy vào backend thật | tài khoản được lưu lâu dài; selftest đã dùng tên ngẫu nhiên, nếu vẫn gặp thì chạy lại |
| `test-nakama.sh` dừng: "cổng 7350 đang trỏ tới container ... compose" | bạn đang test nhầm Nakama của compose. Tắt compose, hoặc cố ý: `ALLOW_COMPOSE=1 ./scripts/test-nakama.sh` |
| `test-p5`: "Truoc khi join da co N pod Allocated" | còn người chơi cũ; đợi pod trống 30 giây tự tắt, hoặc `kubectl delete gs --all -n fomoxa` |
| `test-p5` báo "Ky vong 2 pod Allocated nhung thuc te la 0" | client không vào được pod: xem [mục 6](#6-client-connection); đọc `logs/p5-k8s-*.log` |
| `test-real-backend.sh`: `Connection refused` ngay đầu selftest | backend chưa kịp lên (tăng `sleep 6` trong script) hoặc cổng 9600/9500 đang bị chiếm |
| `dotnet publish` lỗi NuGet | máy không ra được `api.nuget.org`; kiểm tra mạng/proxy |
| Build image .NET báo `NU1301` | container build không ra được Internet (proxy). Cấu hình proxy cho Docker daemon |

## Khi vẫn chưa tìm ra <a href="#if-you-still-cannot-find-it" id="if-you-still-cannot-find-it"></a>

Thu thập và gửi kèm khi báo lỗi:

```bash
kubectl get pods,svc,fleet,gs -n fomoxa -o wide
kubectl describe pod <failing-pod> -n fomoxa | tail -40
kubectl logs <failing-pod> -n fomoxa --tail=100
git rev-parse --short HEAD
```

Với client: file log của Unity (`%USERPROFILE%\AppData\LocalLow\<Company>\MyGame\Player.log` trên Windows) hoặc `-logFile` bạn đã truyền.
