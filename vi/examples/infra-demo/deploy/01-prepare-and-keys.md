# 03.1 Chuẩn bị, cổng trống, khoá và chứng chỉ

Lên đầu tài liệu: [03-TRIEN-KHAI-K8S](README.md) · Tiếp: [02-build-image.md](02-build-images.md)

## Bước 1. Chuẩn bị và kiểm tra cổng trống <a href="#step-1-prepare-and-check-free-ports" id="step-1-prepare-and-check-free-ports"></a>

Mục tiêu: đứng đúng thư mục và chắc chắn các cổng mà cluster sắp chiếm chưa bị ai giữ.

Lệnh:

```bash
cd ~/fomoxa-infra-demo

# Is Docker running?
docker info --format 'Docker {{.ServerVersion}} - OK'

# Does any container already hold a port we need? (compose Nakama, an old cluster, ...)
docker ps --format '{{.Names}}\t{{.Ports}}' | grep -E ':(7777|9600|9643|7350)->' || echo "The ports are free"

# Does any process outside Docker listen on them? (the mock cluster from document 02, ...)
ss -ltnu | grep -E ':(7777|9600|9643|7350)\b' || echo "Nothing is listening"
```

Ý nghĩa: cluster k3d đưa 4 cổng của máy bạn vào cluster; nếu cổng đã bị giữ, `k3d cluster create` sẽ thất bại giữa chừng.

Kết quả mong đợi:

```
Docker 27.3.1 - OK
The ports are free
Nothing is listening
```

Lỗi thường gặp:

| Triệu chứng | Cách xử lý |
|---|---|
| Thấy `fomoxa-test-nakama-1` giữ `7350` | đó là `docker compose` của dev local: `docker compose -f deploy/compose.yaml down`. Nếu không tắt, các script test sẽ test nhầm Nakama của compose và báo thành công giả |
| Cụm giả (tài liệu 02) đang chạy | tắt nó (Ctrl+C): nó cũng dùng 9600/9643 |
| Docker không chạy | [01, Bước 3](../getting-started/prepare-environment.md#step-3-install-docker) |

## Bước 2. Sinh khoá và chứng chỉ (secrets) <a href="#step-2-generate-keys-and-the-certificate" id="step-2-generate-keys-and-the-certificate"></a>

Mục tiêu: tạo các khoá ngẫu nhiên mà các dịch vụ dùng để xác thực lẫn nhau, mật khẩu/khoá riêng cho Nakama và chứng chỉ TLS. Tất cả nằm trong `deploy/secrets/` (đã được `.gitignore`, không bao giờ commit).

Vì sao cần: directory chỉ nhận backend/pod/gateway nào xuất trình đúng khoá; backend chỉ nhận pod có khoá riêng; Nakama dùng khoá riêng thay vì `defaultkey`.

Lệnh:

```bash
mkdir -p deploy/secrets/directory deploy/secrets/nakama deploy/secrets/tls

# gen <file> <bytes>: write <bytes> random bytes as hex (2 characters per byte), no trailing newline
gen() { openssl rand -hex "$2" | tr -d '\n' > "$1"; echo "  + $1 ($(wc -c < "$1") characters)"; }

# --- keys for the directory and the programs that connect to it ---
gen deploy/secrets/directory/root     32   # the directory's root key (MUST be exactly 64 hex characters)
gen deploy/secrets/directory/admin    24   # admin rights (drain, read the pod list)
gen deploy/secrets/directory/backend  24   # backend asks for tickets
gen deploy/secrets/directory/gateway  24   # gateway reads the pod list
gen deploy/secrets/directory/pod      24   # game servers register rooms
gen deploy/secrets/backend-pod        24   # game servers report player counts and scores to the backend (port 9602)

# --- Nakama: its own keys and passwords (instead of defaultkey, defaulthttpkey, admin:admin, localdb) ---
gen deploy/secrets/nakama/server-key       16   # clients and the backend log in to Nakama
gen deploy/secrets/nakama/http-key         24   # only the backend calls internal RPCs (kv_get, verify_ticket, ...)
gen deploy/secrets/nakama/console-password 16   # Nakama admin console password
gen deploy/secrets/nakama/session-key      24   # encrypts session tokens
gen deploy/secrets/nakama/refresh-key      24   # encrypts refresh tokens
gen deploy/secrets/nakama/db-password      16   # Postgres password

# --- self-signed TLS certificate for the TLS proxy (port 9643) ---
openssl req -x509 -newkey rsa:2048 -nodes -days 730 \
    -keyout deploy/secrets/tls/tls.key -out deploy/secrets/tls/tls.crt \
    -subj "/CN=fomoxa.local" \
    -addext "subjectAltName=DNS:fomoxa.local,DNS:localhost,IP:127.0.0.1" \
    -addext "extendedKeyUsage=serverAuth" 2>/dev/null
chmod 600 deploy/secrets/tls/tls.key

# SHA-256 fingerprint of the certificate (the "pin"). The client uses it to confirm it talks to the right proxy
openssl x509 -in deploy/secrets/tls/tls.crt -outform DER | openssl dgst -sha256 -hex | awk '{print toupper($NF)}'
```

Ý nghĩa từng phần:
- `openssl rand -hex N` in N byte ngẫu nhiên thành 2N ký tự hex. `tr -d '\n'` bỏ ký tự xuống dòng (khoá phải không có dòng thừa).
- Chứng chỉ tự ký chỉ để dev/nội bộ. Môi trường thật nên dùng chứng chỉ do CA cấp (xem [05, mục TLS](../operations/03-tls-and-keys.md#tls-between-client-and-backend)).

Hoặc chạy gọn: `./scripts/gen-keys.sh` (sinh 12 khoá ở trên) và `./scripts/gen-tls-cert.sh` (sinh chứng chỉ + in pin). Cả hai không ghi đè file đã có (thêm `-f` để ép tạo lại).

Kết quả mong đợi (từ `gen-keys.sh` và `gen-tls-cert.sh`):

```
=== Sinh keys cho Fomoxa ===
  + directory/root
  + directory/admin
  + directory/backend
  + directory/gateway
  + directory/pod
  + secrets/backend-pod
  + nakama/server-key
  + nakama/http-key
  + nakama/console-password
  + nakama/session-key
  + nakama/refresh-key
  + nakama/db-password
Hoan tat sinh keys tai /home/you/fomoxa-infra-demo/deploy/secrets
Da tao /home/you/fomoxa-infra-demo/deploy/secrets/tls/tls.crt va tls.key (CN=fomoxa.local)
Van tay SHA-256 (pin): FB3FF3780A89AD4A3CB83402C454F0247AA0238C1B304EA8DB475497B73C94DE
```

Kiểm tra:

```bash
find deploy/secrets -type f | sort
wc -c deploy/secrets/directory/root deploy/secrets/directory/backend deploy/secrets/nakama/http-key
```

Phải thấy 14 file (12 khoá + `tls.crt` + `tls.key`); `root` đúng 64 byte, `backend` 48, `http-key` 48.

Lỗi thường gặp:

| Triệu chứng | Cách xử lý |
|---|---|
| `openssl: command not found` | `sudo apt install -y openssl` |
| Khoá `root` không đúng 64 ký tự | tạo lại bằng `gen deploy/secrets/directory/root 32`: directory từ chối khoá gốc sai độ dài |
| Đã có cluster cũ chạy với khoá cũ mà bạn sinh lại khoá | secret trong cluster vẫn là khoá cũ → lệch. Sau khi sinh lại phải làm lại [Bước 8](04-secrets.md#step-8-namespace-and-secrets) và restart các deployment |

