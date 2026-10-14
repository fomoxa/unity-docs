from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES


@diagram('rpc-directions')
def rpc_directions(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('The three kinds of RPC', 'Ba loại RPC'))
    blue, green, red = STROKES['server'], STROKES['client'], STROKES['danger']
    panels = [
        ('Server RPC', 'SendServerRpc', 'server'),
        ('Observers RPC', 'SendObserversRpc', 'observers'),
        ('Target RPC', 'SendTargetRpc(B, ...)', 'target'),
    ]
    for index, (title, method, kind) in enumerate(panels):
        x0 = 20 + index * 300
        if index:
            canvas.line(x0 - 10, 30, x0 - 10, 270, '#E5E7EB', 1)
        canvas.text(x0 + 140, 40, title, 15, 700, 'middle')
        canvas.text(x0 + 140, 60, method, 12, 500, 'middle', MUTED, mono=True)
        canvas.box(x0 + 80, 78, 120, 44, 'server', 'Server')
        clients = [('A', x0 + 10), ('B', x0 + 102), ('C', x0 + 194)]
        for name, cx in clients:
            observer = kind == 'server' or name != 'C'
            if observer:
                canvas.box(cx, 206, 76, 44, 'client', name)
            else:
                canvas.box(cx, 206, 76, 44, 'neutral', name, dashed=True)
        canvas.pill(x0 + 48, 266, t('owner', 'owner'), 'client', 10.5)
        canvas.pill(x0 + 232, 266, t('not observer', 'không observe'), 'neutral', 10.5) if kind != 'server' else None
        if kind == 'server':
            canvas.arrow([(x0 + 48, 206), (x0 + 118, 122)], green, label=t('runs', 'chạy'), label_at=0.45,
                         label_offset=(-18, 0))
            canvas.arrow([(x0 + 140, 206), (x0 + 140, 126)], red, dashed=True, label=t('dropped', 'bị bỏ'),
                         label_at=0.5, label_offset=(30, 4))
        elif kind == 'observers':
            canvas.arrow([(x0 + 118, 122), (x0 + 48, 206)], blue)
            canvas.arrow([(x0 + 140, 122), (x0 + 140, 206)], blue)
        else:
            canvas.arrow([(x0 + 140, 122), (x0 + 140, 206)], blue)
    canvas.text(20, 306, t('A server RPC from a client that does not own the object is dropped, unless it is declared with RequireOwnership = false.',
                           'Server RPC từ client không sở hữu object sẽ bị bỏ, trừ khi được khai báo với RequireOwnership = false.'),
                12, color=MUTED)
    return canvas


@diagram('reliable-ordering')
def reliable_ordering(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 360, t('A lost reliable message holds back the ones after it',
                                'Một message reliable bị mất giữ lại các message phía sau'))
    blue, red, accent, muted = STROKES['server'], STROKES['danger'], STROKES['accent'], STROKES['muted']
    sender_y, receiver_y = 100, 260
    canvas.text(30, sender_y + 4, t('Sender', 'Bên gửi'), 13, 700)
    canvas.text(30, receiver_y + 4, t('Receiver', 'Bên nhận'), 13, 700)
    canvas.line(110, sender_y, 890, sender_y, '#D1D5DB', 1.5)
    canvas.line(110, receiver_y, 890, receiver_y, '#D1D5DB', 1.5)

    sends = [(10, 140, 'ok'), (11, 210, 'lost'), (12, 280, 'ok'), (13, 350, 'ok')]
    for seq, x, fate in sends:
        canvas.circle(x, sender_y, 5, blue)
        canvas.text(x, sender_y - 12, f'#{seq}', 12, 700, 'middle', blue, mono=True)
        if fate == 'lost':
            mid = (x + 35, (sender_y + receiver_y) / 2)
            canvas.arrow([(x, sender_y + 6), mid], red, dashed=True, end=False)
            canvas.text(mid[0] + 2, mid[1] + 6, '✕', 18, 700, 'middle', red)
            continue
        canvas.arrow([(x, sender_y + 6), (x + 60, receiver_y - 8)], blue)

    canvas.circle(440, sender_y, 5, muted)
    canvas.text(440, sender_y - 12, t('unreliable', 'unreliable'), 11.5, 600, 'middle', MUTED)
    canvas.arrow([(440, sender_y + 6), (500, receiver_y - 8)], muted)
    canvas.pill(500, receiver_y + 22, t('handled at once', 'xử lý ngay'), 'neutral', 10.5)

    canvas.pill(200, receiver_y + 22, t('#10 handled', '#10 được xử lý'), 'client', 10.5)
    canvas.rect(320, receiver_y + 40, 120, 44, *KINDS['accent'][:2], radius=8)
    canvas.text(380, receiver_y + 58, t('#12, #13 wait', '#12, #13 chờ'), 12, 700, 'middle', KINDS['accent'][2])
    canvas.text(380, receiver_y + 75, t('for #11', 'cho #11'), 11.5, 400, 'middle', MUTED)
    canvas.line(340, receiver_y, 340, receiver_y + 40, accent, 1, dashed=True)
    canvas.line(410, receiver_y, 410, receiver_y + 40, accent, 1, dashed=True)

    canvas.line(210, sender_y - 52, 640, sender_y - 52, accent, 1.2)
    canvas.line(210, sender_y - 58, 210, sender_y - 30, accent, 1.2)
    canvas.line(640, sender_y - 58, 640, sender_y - 30, accent, 1.2)
    canvas.text(425, sender_y - 60, t('no acknowledgement within the retransmission timeout',
                                      'không có acknowledgement trong retransmission timeout'),
                11.5, 600, 'middle', KINDS['accent'][2])
    canvas.circle(640, sender_y, 5, blue)
    canvas.text(640, sender_y - 12, t('#11 again', '#11 gửi lại'), 12, 700, 'middle', blue)
    canvas.arrow([(640, sender_y + 6), (700, receiver_y - 8)], blue)
    canvas.pill(740, receiver_y + 22, t('#11, #12, #13 handled in order', '#11, #12, #13 được xử lý theo thứ tự'), 'client', 10.5)
    canvas.text(890, 346, t('time →', 'thời gian →'), 11.5, 500, 'end', MUTED)
    return canvas


@diagram('model-codecs')
def model_codecs(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 270, t('One model with two codecs', 'Một model có hai codec'))
    accent = STROKES['accent']

    canvas.text(30, 38, t('Model', 'Model'), 15, 700)
    canvas.rect(30, 54, 300, 168, '#FFFFFF', '#D1D5DB', 10)
    canvas.text(46, 80, 'class Status', 13.5, 700, mono=True)
    canvas.text(46, 102, '[Codec("net")] [Codec("compact")]', 11.5, 500, color=MUTED, mono=True)
    canvas.line(46, 116, 314, 116, '#E5E7EB', 1)
    canvas.text(46, 142, 'Health', 12.5, 600, mono=True)
    canvas.text(130, 142, 'u32', 12.5, 500, color=MUTED, mono=True)
    canvas.pill(250, 138, 'net', 'server', 10, mono=True)
    canvas.pill(298, 138, 'compact', 'accent', 10, mono=True, anchor='middle')
    canvas.text(46, 178, 'Title', 12.5, 600, mono=True)
    canvas.text(130, 178, 'string', 12.5, 500, color=MUTED, mono=True)
    canvas.pill(250, 174, 'net', 'server', 10, mono=True)

    rows = [
        (54, 'server', 'StatusNetCodec', t('Health, Title', 'Health, Title'), t('message id A', 'message id A'), 'StatusNetAdapter'),
        (148, 'accent', 'StatusCompactCodec', 'Health', t('message id B', 'message id B'), 'StatusCompactAdapter'),
    ]
    canvas.text(400, 38, t('Written by fomoxac', 'Do fomoxac viết'), 15, 700)
    canvas.text(670, 38, t('Written by the package', 'Do package viết'), 15, 700)
    for top, kind, codec, fields, message_id, adapter in rows:
        canvas.box(400, top, 220, 74, kind, codec, [fields, message_id], title_mono=True)
        canvas.box(670, top, 220, 74, 'plain', adapter, ['IMessageCodec<Status>'], title_mono=True, mono_body=True)
        canvas.arrow([(620, top + 37), (670, top + 37)], LINE)
        canvas.arrow([(330, 138 if kind == 'server' else 150), (400, top + 37)], STROKES[kind])
    canvas.text(30, 254, t('Each codec carries only its own fields and has its own message id, channel and adapter.',
                           'Mỗi codec chỉ mang field của nó và có message id, channel và adapter riêng.'), 12, color=MUTED)
    return canvas


@diagram('transform-updates')
def transform_updates(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 360, t('How NetworkTransform sends a movement and how a client shows it',
                                'NetworkTransform gửi một chuyển động thế nào và client hiển thị nó ra sao'))
    blue, red, green, muted = STROKES['server'], STROKES['danger'], STROKES['client'], STROKES['muted']
    server_y, client_y = 90, 240
    canvas.text(30, server_y + 4, 'Server', 13, 700)
    canvas.text(30, client_y + 4, 'Client', 13, 700)
    canvas.line(130, server_y, 890, server_y, '#D1D5DB', 1.5)
    canvas.line(130, client_y, 890, client_y, '#D1D5DB', 1.5)

    def x_of(tick):
        return 170 + (tick - 10) * 100

    for tick in range(10, 17):
        canvas.text(x_of(tick), server_y - 30, str(tick), 11.5, 600, 'middle', MUTED, mono=True)
    canvas.text(130, server_y - 30, 'tick', 11.5, 600, 'end', MUTED)
    canvas.line(x_of(10), server_y - 14, x_of(13), server_y - 14, blue, 3)
    canvas.text((x_of(10) + x_of(13)) / 2, server_y - 46, t('moving', 'đang di chuyển'), 12, 700, 'middle', blue)
    canvas.text(x_of(14) + 50, server_y - 46, t('stopped', 'đã dừng'), 12, 700, 'middle', MUTED)

    for tick in (10, 11, 12, 13):
        canvas.circle(x_of(tick), server_y, 6, blue)
        if tick == 12:
            mid = (x_of(tick) + 22, server_y + 62)
            canvas.arrow([(x_of(tick), server_y + 8), mid], red, dashed=True, end=False)
            canvas.text(mid[0] + 2, mid[1] + 7, '✕', 18, 700, 'middle', red)
            continue
        canvas.arrow([(x_of(tick), server_y + 8), (x_of(tick) + 45, client_y - 8)], blue, dashed=True)
        canvas.circle(x_of(tick) + 45, client_y, 5, blue)
        canvas.text(x_of(tick) + 45, client_y + 22, f'#{tick}', 11.5, 600, 'middle', blue, mono=True)

    canvas.circle(x_of(14), server_y, 6, '#FFFFFF', blue, 2)
    canvas.arrow([(x_of(14), server_y + 8), (x_of(14) + 45, client_y - 8)], blue, width=2.2)
    canvas.rect(x_of(14) + 30, client_y - 7, 30, 14, blue, blue, 3)
    canvas.text(x_of(14) + 60, client_y + 22, t('settle: exact final values', 'settle: giá trị cuối chính xác'),
                11.5, 600, 'start', blue)

    canvas.line(x_of(11) + 45, client_y + 40, x_of(13) + 45, client_y + 40, green, 1.5)
    canvas.line(x_of(11) + 45, client_y + 34, x_of(11) + 45, client_y + 46, green, 1.5)
    canvas.line(x_of(13) + 45, client_y + 34, x_of(13) + 45, client_y + 46, green, 1.5)
    canvas.text((x_of(11) + x_of(13)) / 2 + 45, client_y + 62,
                t('shown up to Interpolation Ticks (2) behind the newest snapshot,', 'hiển thị lùi tối đa Interpolation Ticks (2) tick so với snapshot mới nhất,'),
                12, 600, 'middle', KINDS['client'][2])
    canvas.text((x_of(11) + x_of(13)) / 2 + 45, client_y + 80,
                t('moving between received values over the lost #12', 'đi giữa các giá trị đã nhận, qua chỗ #12 bị mất'),
                12, 400, 'middle', MUTED)

    legend_y = 342
    canvas.arrow([(30, legend_y), (66, legend_y)], blue, dashed=True)
    canvas.text(76, legend_y + 4, t('unreliable update, carries its tick', 'update unreliable, mang số tick'), 12)
    canvas.arrow([(380, legend_y), (416, legend_y)], blue, width=2.2)
    canvas.text(426, legend_y + 4, t('reliable settle when the object stops', 'settle reliable khi object dừng'), 12)
    return canvas


@diagram('state-sync')
def state_sync(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('How a state change reaches the clients', 'Một thay đổi state tới client thế nào'))
    blue, green, muted = STROKES['server'], STROKES['client'], STROKES['muted']

    canvas.text(30, 38, t('Server, every tick', 'Server, mỗi tick'), 15, 700)
    canvas.box(30, 56, 190, 76, 'code', t('Your code', 'Code của bạn'), ['health.Current = 80'], mono_body=True)
    canvas.box(255, 56, 190, 76, 'server', t('Encode', 'Encode'),
               [t('after OnTick and', 'sau OnTick và'), 'OnPostTick'])
    canvas.box(480, 56, 190, 76, 'server', t('Compare bytes', 'So byte'),
               [t('with the state', 'với state'), t('sent last time', 'đã gửi lần trước')])
    canvas.box(705, 56, 185, 76, 'server', t('If they differ', 'Nếu khác nhau'),
               [t('send full state or delta,', 'gửi state đầy đủ hoặc delta,'), t('whichever is smaller', 'cái nào nhỏ hơn')])
    canvas.arrow([(220, 94), (255, 94)], LINE)
    canvas.arrow([(445, 94), (480, 94)], LINE)
    canvas.arrow([(670, 94), (705, 94)], LINE)
    canvas.arrow([(575, 132), (575, 160)], muted)
    canvas.pill(575, 172, t('same: nothing is sent', 'giống: không gửi gì'), 'neutral', 10.5)

    canvas.text(30, 220, t('Each observing client', 'Mỗi client đang observe'), 15, 700)
    canvas.box(480, 236, 190, 70, 'client', t('Decode', 'Decode'),
               [t('into your instance', 'vào instance của bạn')])
    canvas.box(705, 236, 185, 70, 'client', 'onChanged(previous)',
               [t('previous values', 'giá trị trước đó')], title_mono=True)
    canvas.arrow([(797, 132), (797, 190), (575, 190), (575, 236)], blue, width=2,
                 label=t('reliable, ordered', 'reliable, có thứ tự'), label_at=0.35, label_offset=(0, -7))
    canvas.arrow([(670, 271), (705, 271)], LINE)
    canvas.box(30, 236, 410, 70, 'accent', t('A delta that does not apply', 'Delta không áp được'),
               [t('the client drops it and sends StateResync;', 'client bỏ nó và gửi StateResync;'),
                t('the server answers with the full state', 'server trả lời bằng state đầy đủ')])
    return canvas
