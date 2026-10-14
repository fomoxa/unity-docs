from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES


@diagram('network-manager-parts')
def network_manager_parts(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 404, t('What a NetworkManager is made of',
                                'NetworkManager gồm những gì'))
    blue, green = STROKES['server'], STROKES['client']

    canvas.text(30, 38, t('In the scene', 'Trong scene'), 15, 700)
    canvas.text(30, 58, t('Components you add and set in the Inspector',
                          'Các component bạn thêm và chỉnh trong Inspector'), 12, 400, color=MUTED)
    fill, stroke, ink = KINDS['neutral']
    canvas.rect(30, 76, 300, 288, '#FFFFFF', stroke, 12)
    canvas.text(46, 98, t('GameObject "Network Manager"', 'GameObject "Network Manager"'), 12, 600, color=ink)
    canvas.box(46, 112, 268, 76, 'accent', 'NetworkManager',
               [t('tick rate, timing, queues,', 'tick rate, timing, hàng đợi,'),
                t('prefab and scene lists', 'danh sách prefab và scene')])
    canvas.box(46, 202, 268, 64, 'code', 'UdpNetworkTransport',
               [t('the Transport field', 'field Transport')], title_mono=True)
    canvas.box(46, 280, 268, 64, 'code', 'RigidbodyPhysics',
               [t('the Physics field', 'field Physics')], title_mono=True)

    canvas.text(420, 38, t('Set up in Awake', 'Được dựng trong Awake'), 15, 700)
    canvas.text(420, 58, t('Reached through properties of the NetworkManager',
                           'Truy cập qua các property của NetworkManager'), 12, 400, color=MUTED)
    canvas.rect(420, 76, 470, 288, '#FFFFFF', KINDS['neutral'][1], 12, dashed=True)
    canvas.box(440, 96, 205, 72, 'server', 'ServerManager',
               [t('listens, spawns, observers', 'lắng nghe, spawn, observer')], title_mono=True)
    canvas.box(665, 96, 205, 72, 'client', 'ClientManager',
               [t('connects, reconnects', 'kết nối, kết nối lại')], title_mono=True)
    canvas.box(440, 280, 205, 64, 'neutral', 'TimeManager',
               [t('ticks and tick events', 'tick và event của tick')], title_mono=True)
    canvas.box(665, 280, 205, 64, 'neutral', 'TransportManager',
               [t('the transport factory', 'transport factory')], title_mono=True)
    canvas.box(440, 188, 205, 72, 'plain', 'Prefabs',
               [t('prefabs it can spawn', 'prefab có thể spawn')], title_mono=True)
    canvas.box(665, 188, 205, 72, 'plain', 'Scenes',
               [t('network scenes it can load', 'network scene có thể load')], title_mono=True)

    canvas.arrow([(314, 150), (420, 150)], LINE, label=t('sets up', 'dựng'), label_offset=(0, -7))
    canvas.arrow([(314, 234), (367, 234), (367, 386), (767, 386), (767, 344)], LINE, dashed=True,
                  label='CreateFactory()', label_at=0.55, label_offset=(0, -6), label_mono=True)
    return canvas


@diagram('host-mode')
def host_mode(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 376, t('A host: one process, one instance per object',
                                'Host: một tiến trình, mỗi object một instance'))
    blue, green = STROKES['server'], STROKES['client']

    canvas.rect(30, 30, 520, 300, *KINDS['host'][:2], radius=14)
    canvas.text(50, 56, t('Host process, one NetworkManager', 'Tiến trình host, một NetworkManager'),
                13, 700, color=KINDS['host'][2])
    canvas.box(56, 78, 170, 64, 'client', 'ClientManager', [t('the host player', 'người chơi host')], title_mono=True)
    canvas.box(354, 78, 170, 64, 'server', 'ServerManager', [t('the server', 'server')], title_mono=True)
    canvas.arrow([(226, 100), (354, 100)], green)
    canvas.arrow([(354, 120), (226, 120)], blue)
    canvas.text(290, 90, t('loopback', 'loopback'), 11.5, 600, 'middle', MUTED)
    canvas.text(290, 138, t('in process', 'trong tiến trình'), 11, 400, 'middle', MUTED)

    canvas.rect(150, 196, 280, 110, '#FFFFFF', KINDS['accent'][1], 12)
    canvas.text(290, 220, t('Player object, a single instance', 'Object Player, một instance duy nhất'),
                13, 600, 'middle', KINDS['accent'][2])
    canvas.text(290, 244, t('server values, no second decode', 'giữ giá trị của server, không decode lại'),
                12, 400, 'middle', MUTED)
    canvas.text(290, 266, t('no interpolation, no prediction', 'không interpolation, không prediction'),
                12, 400, 'middle', MUTED)
    canvas.text(290, 288, t('hidden while not observed', 'bị ẩn khi không được observe'), 12, 400, 'middle', MUTED)
    canvas.arrow([(141, 142), (141, 172), (200, 196)], green, label='OnStartClient', label_mono=True,
                 label_at=0.3, label_offset=(-6, 0), label_anchor='end', label_bg=False)
    canvas.arrow([(439, 142), (439, 172), (380, 196)], blue, label='OnStartServer', label_mono=True,
                 label_at=0.3, label_offset=(6, 0), label_anchor='start', label_bg=False)

    canvas.box(690, 78, 200, 64, 'client', 'Client B', [t('remote player', 'người chơi từ xa')])
    canvas.box(690, 196, 200, 110, 'neutral', t('Its own copy', 'Bản sao riêng'),
               [t('of the Player object,', 'của object Player,'),
                t('interpolated or predicted', 'interpolation hoặc prediction')])
    canvas.arrow([(690, 100), (524, 100)], green)
    canvas.arrow([(524, 120), (690, 120)], blue)
    canvas.text(607, 90, t('transport', 'transport'), 11.5, 600, 'middle', MUTED)
    canvas.text(607, 138, t('for example UDP', 'ví dụ UDP'), 11, 400, 'middle', MUTED)
    canvas.arrow([(790, 142), (790, 196)], LINE, dashed=True)

    legend_y = 358
    canvas.arrow([(30, legend_y), (66, legend_y)], green)
    canvas.text(76, legend_y + 4, t('to the server', 'tới server'), 12)
    canvas.arrow([(200, legend_y), (236, legend_y)], blue)
    canvas.text(246, legend_y + 4, t('from the server', 'từ server'), 12)
    return canvas


@diagram('multi-transport')
def multi_transport(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 300, t('One server, two transports',
                                'Một server, hai transport'))
    blue, green = STROKES['server'], STROKES['client']

    canvas.rect(520, 30, 370, 236, *KINDS['server'][:2], radius=14)
    canvas.text(540, 56, t('Server, one NetworkManager', 'Server, một NetworkManager'), 13, 700, color=KINDS['server'][2])
    canvas.box(540, 72, 330, 52, 'accent', 'MultiNetworkTransport', [t('the Transport field', 'field Transport')],
               title_mono=True)
    canvas.box(540, 140, 330, 50, 'plain', t('Entry 0: UdpNetworkTransport', 'Entry 0: UdpNetworkTransport'),
               [t('port of StartConnection, 7777', 'port của StartConnection, 7777')], title_size=13)
    canvas.box(540, 202, 330, 50, 'plain', t('Entry 1: WebSocketNetworkTransport', 'Entry 1: WebSocketNetworkTransport'),
               [t('port in the entry, 8080', 'port ghi trong entry, 8080')], title_size=13)

    canvas.box(30, 120, 250, 64, 'client', t('Desktop client', 'Client desktop'),
               [t('frame budget 1200 bytes', 'frame budget 1200 byte')])
    canvas.box(30, 202, 250, 64, 'client', t('Browser client (WebGL)', 'Client trình duyệt (WebGL)'),
               [t('largest Fomoxa frame', 'frame Fomoxa lớn nhất')])
    canvas.arrow([(280, 158), (540, 165)], green, start=True, label='UDP :7777', label_mono=True)
    canvas.arrow([(280, 234), (540, 227)], green, start=True, label='ws://…:8080', label_mono=True)
    canvas.text(30, 70, t('Each client connects through the first entry its platform can run:',
                          'Mỗi client kết nối qua entry đầu tiên mà nền tảng của nó chạy được:'), 12, 400, color=MUTED)
    canvas.text(30, 90, t('a WebGL build skips UDP and uses WebSocket.',
                          'bản build WebGL bỏ qua UDP và dùng WebSocket.'), 12, 400, color=MUTED)
    return canvas
