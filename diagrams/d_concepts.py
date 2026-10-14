from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES, INK, text_width


def translator(language):
    return lambda english, vietnamese: pick(language, english, vietnamese)


@diagram('layers')
def layers(language):
    t = translator(language)
    canvas = Canvas(920, 470, t('The layers on both ends of a connection', 'Các tầng ở hai đầu một kết nối'))
    rows = [
        ('plain', t('Your game', 'Game của bạn'), t('MonoBehaviours, NetworkBehaviours, models', 'MonoBehaviour, NetworkBehaviour, model')),
        ('host', 'Fomoxa.Unity', t('layer 2: Unity integration', 'tầng 2: tích hợp Unity')),
        ('code', 'Fomoxa.Networking', t('layer 1: the Core, no UnityEngine', 'tầng 1: Core, không có UnityEngine')),
        ('neutral', 'Fomoxa.Net', t('framing, handshake, heartbeat', 'framing, handshake, heartbeat')),
        ('neutral', t('Transport', 'Transport'), t('UDP, TCP, WebSocket or loopback', 'UDP, TCP, WebSocket hoặc loopback')),
    ]
    columns = [(60, t('Client process', 'Tiến trình client'), 'client'), (540, t('Server process', 'Tiến trình server'), 'server')]
    top, height, gap, width = 74, 54, 14, 320
    for x, title, kind in columns:
        canvas.text(x + width / 2, 50, title, 15, 700, 'middle', STROKES[kind])
        for index, (row_kind, name, body) in enumerate(rows):
            y = top + index * (height + gap)
            canvas.box(x, y, width, height, row_kind, name, [body], title_size=14, body_size=12,
                       title_mono=index in (1, 2, 3))
    bottom = top + 4 * (height + gap) + height
    canvas.arrow([(380, bottom - height / 2), (540, bottom - height / 2)], LINE, start=True,
                 label=t('network', 'mạng'), label_offset=(0, -10))

    flow = STROKES['accent']
    canvas.arrow([(44, top + 10), (44, bottom - 10)], flow, width=2)
    canvas.arrow([(876, bottom - 10), (876, top + 10)], flow, width=2)
    canvas.text(30, bottom + 34, t('A message from the client passes down its stack, across the network and up the server\'s stack.',
                                   'Message từ client đi xuống các tầng của client, qua mạng, rồi đi lên các tầng của server.'),
                12.5, 400, color=MUTED)
    canvas.text(30, bottom + 54, t('Messages from the server travel the same way in the opposite direction.',
                                   'Message từ server đi theo đường ngược lại.'), 12.5, 400, color=MUTED)
    return canvas


@diagram('send-queue')
def send_queue(language):
    t = translator(language)
    canvas = Canvas(920, 290, t('Sends go into a queue that is flushed into bundles', 'Lệnh gửi đi vào hàng đợi rồi được flush thành bundle'))
    sends = ['SendServerRpc(...)', t('state change', 'state thay đổi'), t('transform update', 'cập nhật transform'), 'Send(...)']
    canvas.text(30, 40, t('Your code and the package', 'Code của bạn và package'), 13, 700, color=MUTED)
    for index, label in enumerate(sends):
        y = 72 + index * 44
        canvas.pill(30, y, label, 'code', 11.5, mono=index in (0, 3), anchor='start')
        canvas.arrow([(196, y), (262, 126 + index * 16)], LINE)

    canvas.text(270, 40, t('Send queue of one connection', 'Hàng đợi gửi của một kết nối'), 13, 700, color=MUTED)
    canvas.rect(270, 106, 250, 88, *KINDS['neutral'][:2], radius=10)
    for index in range(6):
        fill = KINDS['accent'][0] if index % 3 == 0 else KINDS['code'][0]
        canvas.rect(284 + index * 38, 126, 30, 48, fill, '#9CA3AF', 5, stroke_width=1)
    canvas.lines(270, 218, [t('Message Capacity: 1024 messages', 'Message Capacity: 1024 message'),
                            t('Byte Capacity: 1 MiB', 'Byte Capacity: 1 MiB'),
                            t('Reliable Window: 1024 unacknowledged', 'Reliable Window: 1024 chưa được xác nhận')], 11.5, color='#374151', gap=18)

    canvas.arrow([(520, 150), (600, 150)], LINE, label=t('flush', 'flush'), label_offset=(0, -10))
    canvas.text(560, 182, t('once per tick', 'mỗi tick một lần'), 11, 400, 'middle', MUTED)

    canvas.text(606, 40, t('Bundles, one transport frame each', 'Bundle, mỗi bundle là một frame'), 13, 700, color=MUTED)
    for row, count in enumerate((4, 2)):
        y = 82 + row * 74
        canvas.rect(606, y, 200, 54, '#FFFFFF', STROKES['server'], 8)
        for index in range(count):
            canvas.rect(616 + index * 46, y + 10, 38, 34, KINDS['code'][0], '#9CA3AF', 5, stroke_width=1)
        canvas.arrow([(806, y + 27), (862, y + 27)], STROKES['server'])
    canvas.text(880, 150, t('to', 'tới'), 11, 400, 'middle', MUTED)
    canvas.text(880, 166, 'transport', 11, 600, 'middle', INK)
    canvas.lines(606, 236, [t('At most the frame budget per bundle:', 'Mỗi bundle tối đa bằng frame budget:'),
                            t('1200 bytes over UDP, the largest Fomoxa', '1200 byte với UDP, frame lớn nhất của'),
                            t('frame over TCP and WebSocket.', 'Fomoxa với TCP và WebSocket.')], 11.5, color='#374151', gap=17)
    return canvas


@diagram('heartbeat')
def heartbeat(language):
    t = translator(language)
    canvas = Canvas(920, 200, t('How long a silent connection survives', 'Một kết nối im lặng tồn tại bao lâu'))
    left, right, axis = 60, 860, 110
    scale = (right - left) / 22
    canvas.line(left, axis, right, axis, LINE, 1.5)
    for second in range(0, 23, 5):
        x = left + second * scale
        canvas.line(x, axis - 4, x, axis + 4, LINE, 1.5)
        canvas.text(x, axis + 20, f'{second} s', 11, 400, 'middle', MUTED)
    points = [
        (0, 'neutral', t('last message', 'message cuối')),
        (5, 'accent', t('probe sent', 'gửi probe')),
        (20, 'danger', t('stops with Timeout', 'dừng với Timeout')),
    ]
    for second, kind, label in points:
        x = left + second * scale
        canvas.circle(x, axis, 7, KINDS[kind][1])
        canvas.pill(x, axis - 30, label, kind, 11)
    y = 160
    canvas.arrow([(left, y), (left + 5 * scale, y)], STROKES['accent'], start=True)
    canvas.text(left + 2.5 * scale, y + 22, 'Heartbeat Interval Seconds = 5', 11.5, 500, 'middle', INK, mono=True)
    canvas.arrow([(left + 5 * scale, y), (left + 20 * scale, y)], STROKES['danger'], start=True)
    canvas.text(left + 12.5 * scale, y + 22, 'Heartbeat Timeout Seconds = 15', 11.5, 500, 'middle', INK, mono=True)
    return canvas


@diagram('frame-ticks')
def frame_ticks(language):
    t = translator(language)
    canvas = Canvas(920, 250, t('Frames of different lengths run whole ticks', 'Frame dài ngắn khác nhau chạy trọn từng tick'))
    left, right = 70, 880
    scale = (right - left) / 250
    frames = [(0, 16, 0), (16, 32, 0), (32, 48, 1), (48, 98, 1), (98, 240, 3)]
    canvas.text(left - 12, 72, t('frames', 'frame'), 12, 600, 'end', MUTED)
    for index, (start, end, ticks) in enumerate(frames):
        x0, x1 = left + start * scale, left + end * scale
        kind = 'accent' if ticks == 3 else 'neutral'
        canvas.rect(x0 + 1, 52, x1 - x0 - 2, 36, KINDS[kind][0], KINDS[kind][1], 6)
        label = {0: t('0 ticks', '0 tick'), 1: t('1 tick', '1 tick'), 3: t('3 ticks, 2 dropped', '3 tick, bỏ 2')}[ticks]
        if x1 - x0 > 60:
            canvas.text((x0 + x1) / 2, 75, label, 11.5, 600, 'middle', KINDS[kind][2])
        else:
            canvas.text((x0 + x1) / 2, 75, str(ticks), 11.5, 600, 'middle', KINDS[kind][2])
    axis = 130
    canvas.text(left - 12, axis + 4, t('ticks due', 'tick tới hạn'), 12, 600, 'end', MUTED)
    canvas.line(left, axis, right, axis, LINE, 1.5)
    due = [round(n * 1000 / 30, 1) for n in range(1, 8)]
    for index, ms in enumerate(due):
        x = left + ms * scale
        ran = index < 5
        canvas.circle(x, axis, 6, STROKES['server'] if ran else '#FFFFFF', None if ran else STROKES['danger'], 2)
    for ms in range(0, 251, 50):
        x = left + ms * scale
        canvas.text(x, axis + 24, f'{ms} ms', 11, 400, 'middle', MUTED)
    canvas.circle(left + 6, 192, 6, STROKES['server'])
    canvas.text(left + 20, 196, t('a tick that runs', 'tick được chạy'), 12)
    canvas.circle(left + 186, 192, 6, '#FFFFFF', STROKES['danger'], 2)
    canvas.text(left + 200, 196, t('a tick beyond Max Ticks Per Frame (3), dropped', 'tick vượt Max Ticks Per Frame (3), bị bỏ'), 12)
    canvas.text(left, 226, t('Tick Rate 30: one tick every 33.3 ms of unscaled time.', 'Tick Rate 30: mỗi 33.3 ms thời gian unscaled có một tick.'),
                12, 400, color=MUTED)
    return canvas


@diagram('tick-order')
def tick_order(language):
    t = translator(language)
    steps = [
        ('both', False, 'OnPreTick', t('TimeManager.Tick increases, OnPreTick fires', 'TimeManager.Tick tăng, OnPreTick chạy')),
        ('both', False, t('Receive', 'Nhận'), t('first tick of the frame only; the client updates its clock', 'chỉ ở tick đầu của frame; client cập nhật đồng hồ')),
        ('client', True, t('Place bodies', 'Đặt body'), t('bodies it does not predict follow their transforms', 'body không được dự đoán đi theo transform')),
        ('client', False, t('Predict', 'Dự đoán'), t('reconcile, then gather, apply and send input', 'reconcile, rồi gather, apply và gửi input')),
        ('server', False, t('Apply input', 'Áp input'), t('input of this tick for every object', 'input của tick này cho mọi object')),
        ('both', True, t('Step physics', 'Bước physics'), t('one step, then query contacts', 'một bước, rồi truy vấn contact')),
        ('split', False, t('Record', 'Ghi lại'), (t('record the predicted state', 'ghi predicted state'), t('send reconcile states to owners', 'gửi reconcile state cho owner'))),
        ('both', True, t('Contact events', 'Contact event'), t('enter, stay and exit callbacks', 'callback enter, stay và exit')),
        ('both', False, 'OnTick, OnPostTick', t('your per-tick game logic', 'logic game theo tick của bạn')),
        ('server', False, t('Capture', 'Chụp lại'), t('observers, state and transforms are queued', 'observer, state và transform được đưa vào hàng đợi')),
        ('both', False, 'Flush', t('both send queues are sent', 'cả hai hàng đợi gửi được gửi đi')),
    ]
    row, top = 42, 78
    canvas = Canvas(920, top + len(steps) * row + 62, t('The order of work in one tick', 'Thứ tự công việc trong một tick'))
    client_x, server_x, lane = 230, 570, 320
    canvas.text(client_x + lane / 2, 50, t('Client', 'Client'), 15, 700, 'middle', STROKES['client'])
    canvas.text(server_x + lane / 2, 50, t('Server', 'Server'), 15, 700, 'middle', STROKES['server'])
    canvas.rect(client_x, 62, lane, len(steps) * row + 8, '#F7FCF9', '#D1FAE5', 10)
    canvas.rect(server_x, 62, lane, len(steps) * row + 8, '#F6F9FF', '#DBEAFE', 10)
    for index, (who, physics, name, detail) in enumerate(steps):
        y = top + index * row
        canvas.circle(34, y + 15, 12, LINE)
        canvas.text(34, y + 19.5, str(index + 1), 12, 700, 'middle', '#FFFFFF')
        canvas.text(56, y + 20, name, 13, 600, color=INK, mono=name.startswith('On') or name == 'Flush')
        spans = []
        if who == 'both':
            spans = [(client_x + 10, server_x + lane - 10, 'neutral', detail)]
        elif who == 'client':
            spans = [(client_x + 10, client_x + lane - 10, 'client', detail)]
        elif who == 'server':
            spans = [(server_x + 10, server_x + lane - 10, 'server', detail)]
        else:
            spans = [(client_x + 10, client_x + lane - 10, 'client', detail[0]),
                     (server_x + 10, server_x + lane - 10, 'server', detail[1])]
        for x0, x1, kind, label in spans:
            fill, stroke, ink = KINDS[kind]
            canvas.rect(x0, y + 2, x1 - x0, 28, fill, stroke, 6, dashed=physics, stroke_width=1.2)
            canvas.text((x0 + x1) / 2, y + 20.5, label, 11.5, 500, 'middle', ink)
    legend = top + len(steps) * row + 30
    canvas.rect(30, legend - 12, 34, 18, '#FFFFFF', LINE, 5, dashed=True, stroke_width=1.2)
    canvas.text(74, legend + 2, t('only with physics simulation on', 'chỉ khi bật mô phỏng physics'), 12)
    canvas.rect(330, legend - 12, 34, 18, KINDS['neutral'][0], KINDS['neutral'][1], 5, stroke_width=1.2)
    canvas.text(374, legend + 2, t('on both sides, wherever the manager runs a server or a client', 'ở cả hai phía, nơi manager chạy server hoặc client'), 12)
    return canvas


@diagram('tick-numbers')
def tick_numbers(language):
    t = translator(language)
    canvas = Canvas(920, 300, t('The three tick numbers of a remote client', 'Ba số tick của một client từ xa'))
    left, right = 150, 880
    first, last = 96, 107
    scale = (right - left) / (last - first)
    rows = [(92, t('Server', 'Server'), 'server'), (196, t('Client', 'Client'), 'client')]
    for y, label, kind in rows:
        canvas.text(left - 20, y + 5, label, 14, 700, 'end', STROKES[kind])
        canvas.line(left, y, right, y, '#D1D5DB', 1.5)
        for tick in range(first, last + 1):
            x = left + (tick - first) * scale
            canvas.line(x, y - 5, x, y + 5, '#9CA3AF', 1.2)
            canvas.text(x, y + 22, str(tick), 11, 400, 'middle', MUTED)
    server_now = left + (100 - first) * scale
    canvas.circle(server_now, 92, 8, STROKES['server'])
    canvas.pill(server_now, 58, t('the server\'s tick now', 'tick hiện tại của server'), 'server', 11)
    estimate = left + (100 - first) * scale
    prediction = left + (104 - first) * scale
    canvas.circle(estimate, 196, 8, '#FFFFFF', STROKES['server'], 2.5)
    canvas.pill(estimate, 162, 'ServerTick', 'server', 11, mono=True)
    canvas.circle(prediction, 196, 8, STROKES['client'])
    canvas.pill(prediction, 162, 'PredictionTick', 'client', 11, mono=True)
    canvas.arrow([(estimate + 10, 246), (prediction - 10, 246)], STROKES['accent'], start=True)
    canvas.text((estimate + prediction) / 2, 268, t('about RTT/2 + Input Buffer ticks', 'khoảng RTT/2 + Input Buffer tick'), 12, 600, 'middle', KINDS['accent'][2])
    arrival = left + (102 - first) * scale
    canvas.arrow([(prediction - 6, 186), (arrival + 4, 104)], STROKES['client'], dashed=True,
                 label=t('input for tick 104', 'input cho tick 104'), label_at=0.68, label_offset=(74, 4))
    canvas.text(arrival, 132, t('arrives early', 'tới sớm'), 11, 400, 'middle', MUTED)
    return canvas


@diagram('authority')
def authority(language):
    t = translator(language)
    canvas = Canvas(920, 316, t('What a client can send and what the package checks', 'Client gửi được gì và package kiểm tra gì'))
    canvas.box(30, 40, 150, 190, 'client', t('Client', 'Client'), [t('asks', 'xin phép')])
    canvas.box(740, 40, 150, 190, 'server', t('Server', 'Server'), [t('decides', 'quyết định')])
    paths = [
        ('server RPC', t('checked: the caller owns the object,', 'kiểm tra: người gọi là owner,'),
         t('unless RequireOwnership = false', 'trừ khi RequireOwnership = false'), 'client'),
        ('input', t('checked: the sender owns the object,', 'kiểm tra: người gửi là owner,'),
         t('and the tick is not past or too far ahead', 'và tick không quá cũ hay quá xa'), 'client'),
        (t('raw message', 'raw message'), t('not checked: the handler gets', 'không kiểm tra: handler nhận'),
         t('the sender\'s peer id', 'peer id của người gửi'), 'muted'),
    ]
    for index, (name, first, second, kind) in enumerate(paths):
        y = 56 + index * 66
        canvas.arrow([(184, y + 30), (736, y + 30)], STROKES[kind], dashed=kind == 'muted')
        canvas.text(206, y + 2, name, 12.5, 700, color=INK, mono=index < 2)
        canvas.text(330, y + 2, first, 12, 400, color='#374151')
        canvas.text(330, y + 19, second, 12, 400, color=MUTED)
    canvas.text(30, 266, t('The package checks who sends, not what is sent. Check values such as speeds and positions in your handler.',
                           'Package kiểm tra ai gửi, không kiểm tra nội dung gửi. Hãy tự kiểm tra các giá trị như tốc độ, vị trí trong handler.'),
                12.5, 600, color=KINDS['accent'][2])
    canvas.text(30, 292, t('Only the server spawns, despawns, changes owners, changes state, moves objects, loads network scenes and chooses observers.',
                           'Chỉ server spawn, despawn, đổi owner, đổi state, dời object, load network scene và chọn observer.'),
                12.5, 400, color=MUTED)
    return canvas


@diagram('prediction-loop')
def prediction_loop(language):
    t = translator(language)
    canvas = Canvas(920, 360, t('One input travels to the server and its result comes back', 'Một input đi lên server và kết quả quay về'))
    left, width = 120, 108
    client_y, server_y = 44, 236
    canvas.text(left - 16, client_y + 30, t('Owner\'s client', 'Client của owner'), 13, 700, 'end', STROKES['client'])
    canvas.text(left - 16, server_y + 30, t('Server', 'Server'), 13, 700, 'end', STROKES['server'])
    for index, tick in enumerate(range(12, 19)):
        x = left + index * width
        kind = 'accent' if tick in (12, 16) else 'client'
        canvas.rect(x + 4, client_y, width - 8, 52, *KINDS[kind][:2], radius=8, stroke_width=1.2)
        canvas.text(x + width / 2, client_y + 20, t(f'tick {tick}', f'tick {tick}'), 12, 700, 'middle', KINDS[kind][2])
        sub = {12: t('apply input 12', 'apply input 12'), 16: t('compare 12', 'so sánh 12')}.get(tick, t('predict', 'dự đoán'))
        canvas.text(x + width / 2, client_y + 38, sub, 11, 400, 'middle', MUTED)
    for index, tick in enumerate(range(10, 17)):
        x = left + index * width
        kind = 'accent' if tick == 12 else 'server'
        canvas.rect(x + 4, server_y, width - 8, 52, *KINDS[kind][:2], radius=8, stroke_width=1.2)
        canvas.text(x + width / 2, server_y + 20, t(f'tick {tick}', f'tick {tick}'), 12, 700, 'middle', KINDS[kind][2])
        if tick == 12:
            canvas.text(x + width / 2, server_y + 38, t('apply input 12', 'apply input 12'), 11, 400, 'middle', MUTED)
    canvas.arrow([(left + width * 0.6, client_y + 54), (left + width * 2.4, server_y - 2)], STROKES['client'],
                 label=t('input 12', 'input 12'), label_at=0.5, label_offset=(-34, 0))
    canvas.arrow([(left + width * 2.6, server_y - 2), (left + width * 4.4, client_y + 54)], STROKES['server'],
                 label=t('state of tick 12', 'state của tick 12'), label_at=0.5, label_offset=(-62, 0))
    replay_x = left + 4 * width + 24
    canvas.rect(replay_x, 128, 3 * width - 28, 86, '#FFFFFF', STROKES['danger'], 10, dashed=True)
    canvas.text(replay_x + 14, 150, t('On a mismatch:', 'Nếu không khớp:'), 12, 700, color=KINDS['danger'][2])
    canvas.text(replay_x + 14, 170, t('1. restore the server\'s state of tick 12', '1. khôi phục state của server ở tick 12'), 11.5, 400, color='#374151')
    canvas.text(replay_x + 14, 188, t('2. apply inputs 13, 14, 15 and 16 again', '2. apply lại input 13, 14, 15 và 16'), 11.5, 400, color='#374151')
    canvas.text(replay_x + 14, 206, t('3. keep predicting from tick 17', '3. dự đoán tiếp từ tick 17'), 11.5, 400, color='#374151')
    canvas.text(left, 322, t('The client runs ahead of the server, so its tick 16 happens at about the same time as the server\'s tick 14.',
                             'Client chạy trước server, nên tick 16 của client diễn ra cùng lúc với khoảng tick 14 của server.'),
                12, 400, color=MUTED)
    canvas.text(left, 342, t('Time flows to the right. Tick numbers are an example.', 'Thời gian chạy từ trái sang phải. Số tick chỉ là ví dụ.'),
                12, 400, color=MUTED)
    return canvas


@diagram('determinism')
def determinism(language):
    t = translator(language)
    rows = [
        (t('Protocol', 'Protocol'), t('every message has a fixed layout; schemas are compared in the handshake', 'mỗi message có layout cố định; schema được so ở handshake'), 'client', t('provided', 'có')),
        (t('Input', 'Input'), t('input belongs to a tick; missing input repeats the last one', 'input gắn với một tick; thiếu input thì lặp input trước'), 'client', t('provided', 'có')),
        (t('Tick', 'Tick'), t('fixed length TickDelta, one numbering on both sides', 'độ dài cố định TickDelta, cùng cách đánh số ở hai phía'), 'client', t('provided', 'có')),
        (t('Game logic', 'Logic game'), t('apply() must read only input, own state and TickDelta', 'apply() chỉ được đọc input, state riêng và TickDelta'), 'accent', t('your code', 'code của bạn')),
        (t('Physics', 'Physics'), t('Unity physics does not promise identical results', 'physics của Unity không bảo đảm kết quả giống hệt'), 'danger', t('not provided', 'không có')),
        (t('State', 'State'), t('matches() decides how close is close enough', 'matches() quyết định gần tới mức nào là đủ'), 'neutral', t('not required', 'không bắt buộc')),
    ]
    top, row = 40, 50
    canvas = Canvas(920, top + len(rows) * row + 70, t('What the package makes deterministic', 'Package làm cho phần nào tất định'))
    for index, (name, detail, kind, status) in enumerate(rows):
        y = top + index * row
        fill, stroke, ink = KINDS[kind]
        canvas.rect(30, y, 860, 40, fill, stroke, 8, stroke_width=1.2)
        canvas.text(48, y + 25, name, 13.5, 700, color=ink)
        canvas.text(190, y + 25, detail, 12.5, 400, color='#374151')
        width = text_width(status, 11) + 16
        canvas.pill(880 - width, y + 20, status, kind, 11, anchor='start')
    y = top + len(rows) * row + 16
    canvas.text(30, y + 14, t('Not in the package: lockstep, match recording and replay, deterministic random numbers, state hashing.',
                              'Không có trong package: lockstep, ghi và phát lại trận đấu, số ngẫu nhiên tất định, state hashing.'),
                12.5, 400, color=MUTED)
    canvas.text(30, y + 36, t('Prediction needs results that are close enough. Differences are corrected by reconciliation.',
                              'Prediction chỉ cần kết quả đủ gần. Chênh lệch được reconciliation sửa.'), 12.5, 400, color=MUTED)
    return canvas
