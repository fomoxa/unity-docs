from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES


@diagram('topology')
def topology(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 400, t('A dedicated server and a host, each with clients',
                                'Một dedicated server và một host, mỗi bên có các client'))
    blue, green = STROKES['server'], STROKES['client']

    canvas.text(30, 38, t('Dedicated server', 'Dedicated server'), 15, 700)
    canvas.text(30, 58, t('A process that only runs the server, often without graphics',
                          'Tiến trình chỉ chạy server, thường không có đồ họa'), 12, 400, color=MUTED)
    canvas.box(150, 84, 180, 64, 'server', t('Server', 'Server'), [t('owns the game state', 'nắm game state')])
    clients = [(30, 'Client A'), (180, 'Client B'), (330, 'Client C')]
    for x, name in clients:
        canvas.box(x, 248, 120, 52, 'client', name, [t('a player', 'một người chơi')])
        top = (x + 60, 248)
        server = (240 + (x - 180) * 0.45, 148)
        canvas.arrow([(top[0] - 9, top[1]), (server[0] - 9, server[1] + 2)], green)
        canvas.arrow([(server[0] + 9, server[1] + 2), (top[0] + 9, top[1])], blue)

    canvas.line(470, 30, 470, 330, '#E5E7EB', 1)

    canvas.text(500, 38, t('Host', 'Host'), 15, 700)
    canvas.text(500, 58, t('One process runs the server and a player\'s client',
                           'Một tiến trình chạy server cùng client của một người chơi'), 12, 400, color=MUTED)
    canvas.rect(560, 76, 330, 104, *KINDS['host'][:2], radius=12)
    canvas.text(575, 96, t('Host process', 'Tiến trình host'), 12, 600, color=KINDS['host'][2])
    canvas.box(578, 108, 120, 56, 'server', t('Server', 'Server'))
    canvas.box(752, 108, 120, 56, 'client', t('Client', 'Client'), [t('host player', 'người chơi host')])
    canvas.arrow([(698, 128), (752, 128)], LINE, start=True)
    canvas.text(725, 154, t('loopback', 'loopback'), 11, 500, 'middle', MUTED)
    for x, name, anchor in [(560, 'Client B', 608), (720, 'Client C', 668)]:
        canvas.box(x, 248, 120, 52, 'client', name, [t('a player', 'một người chơi')])
        top = x + 60
        canvas.arrow([(top - 9, 248), (anchor - 9, 166)], green)
        canvas.arrow([(anchor + 9, 166), (top + 9, 248)], blue)

    legend_y = 356
    canvas.arrow([(30, legend_y), (66, legend_y)], green)
    canvas.text(76, legend_y + 4, t('client to server: input and server RPCs',
                                    'client tới server: input và server RPC'), 12)
    canvas.arrow([(420, legend_y), (456, legend_y)], blue)
    canvas.text(466, legend_y + 4, t('server to clients: spawns, state, transforms and client RPCs',
                                     'server tới client: spawn, state, transform và client RPC'), 12)
    return canvas


@diagram('workflow')
def workflow(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 236, t('The four steps a game takes to use the package',
                                'Bốn bước một game đi qua để dùng package'))
    cards = [
        (t('Declare models', 'Khai báo model'),
         [t('C# classes marked with', 'Class C# đánh dấu bằng'), t('[Network] and [Codec].', '[Network] và [Codec].'),
          t('The package generates', 'Package sinh codec'), t('their codecs.', 'cho chúng.')],
         'code'),
        (t('Add a NetworkManager', 'Thêm NetworkManager'),
         [t('One per scene, with a', 'Một cái cho mỗi scene,'), t('transport such as', 'kèm một transport như'),
          'UdpNetworkTransport.'],
         'neutral'),
        (t('Make network prefabs', 'Tạo network prefab'),
         [t('NetworkObject on the root,', 'NetworkObject ở root,'), t('NetworkBehaviour scripts', 'các script NetworkBehaviour'),
          t('for the networked logic.', 'cho logic networking.')],
         'neutral'),
        (t('Start and spawn', 'Khởi động và spawn'),
         [t('Start a server, a client', 'Khởi động server, client'), t('or a host from code. The', 'hoặc host từ code. Server'),
          t('server spawns objects.', 'spawn các object.')],
         'server'),
    ]
    width, gap, top = 196, 30, 34
    for index, (title, body, kind) in enumerate(cards):
        x = 22 + index * (width + gap)
        fill, stroke, ink = KINDS[kind]
        canvas.rect(x, top, width, 172, fill, stroke, 12)
        canvas.circle(x + 26, top + 28, 14, stroke)
        canvas.text(x + 26, top + 33, str(index + 1), 14, 700, 'middle', '#FFFFFF')
        canvas.text(x + 46, top + 33, title, 13.5, 700, color=ink)
        canvas.lines(x + 16, top + 70, body, 12.5, color='#374151', gap=19)
        if index < len(cards) - 1:
            canvas.arrow([(x + width + 4, top + 86), (x + width + gap - 4, top + 86)], LINE)
    return canvas


@diagram('code-generation')
def code_generation(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 420, t('How the package generates code from models',
                                'Package sinh code từ model như thế nào'))
    accent = STROKES['accent']

    canvas.text(24, 34, t('Inputs', 'Đầu vào'), 13, 700, color=MUTED)
    inputs = [
        (t('Your models', 'Model của bạn'), t('Models Folder of FomoxaSettings', 'Models Folder của FomoxaSettings')),
        (t('Package system models', 'System model của package'), t('copied to FomoxaSystemModels/', 'copy vào FomoxaSystemModels/')),
        (t('RPC models', 'RPC model'), t('written to Generated/RpcModels/ for', 'viết vào Generated/RpcModels/ cho')),
    ]
    for index, (title, body) in enumerate(inputs):
        y = 48 + index * 76
        lines = [body] if index < 2 else [body, t('RPCs without a model', 'RPC không có model')]
        canvas.box(24, y, 250, 62, 'code', title, lines, align='left', title_size=13, body_size=11.5)
        canvas.arrow([(274, y + 31), (330, 142 + index * 18)], LINE)

    canvas.box(334, 128, 150, 64, 'accent', 'fomoxac', [t('model compiler', 'trình biên dịch model')], title_mono=True)

    canvas.text(560, 34, t('Generated Folder', 'Generated Folder'), 13, 700, color=MUTED)
    outputs = [
        ('fomoxac', [t('<Model>NetCodec.cs per model', '<Model>NetCodec.cs cho mỗi model'),
                     'NetSchema.cs, Handshake.cs, Runtime.cs']),
        (t('package', 'package'), [t('UnityCodecs/ for Unity types', 'UnityCodecs/ cho type của Unity'),
                                   t('<Model>NetAdapter.cs per codec', '<Model>NetAdapter.cs cho mỗi codec'),
                                   'FomoxaAdapters.cs, FomoxaUnityRegistration.cs']),
        (t('prefab and scene steps', 'bước prefab và scene'), ['FomoxaPrefabList.asset, FomoxaPrefabs.cs',
                                                               'FomoxaSceneList.asset, FomoxaScenes.cs']),
    ]
    y = 48
    for index, (who, lines) in enumerate(outputs):
        h = 30 + len(lines) * 18
        canvas.rect(560, y, 336, h, '#FFFFFF', '#D1D5DB', 8)
        canvas.pill(574, y + 15, who, 'accent' if index == 0 else 'neutral', 10.5, anchor='start')
        canvas.lines(574, y + 44, lines, 11.5, color='#374151', mono=True, gap=18)
        if index < 2:
            canvas.arrow([(484, 160), (556, y + h / 2)], accent if index == 0 else LINE)
        y += h + 12

    canvas.line(24, 306, 896, 306, '#E5E7EB')
    canvas.text(24, 334, t('When Play Mode or a player starts', 'Khi Play Mode hoặc bản build khởi động'), 13, 700, color=MUTED)
    steps = [
        ('FomoxaUnityRegistration', t('registers schema and codecs', 'đăng ký schema và codec')),
        ('FomoxaRegistry.Default', t('holds them for every manager', 'giữ chúng cho mọi manager')),
        ('NetworkManager.Awake', t('reads the registry', 'đọc registry')),
    ]
    for index, (title, body) in enumerate(steps):
        x = 24 + index * 300
        canvas.box(x, 348, 272, 56, 'server' if index == 2 else 'neutral', title, [body], title_mono=True, title_size=12.5)
        if index < 2:
            canvas.arrow([(x + 274, 376), (x + 298, 376)], LINE)
    return canvas
