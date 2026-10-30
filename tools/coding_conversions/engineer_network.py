"""engineer-network: the final challenge's code-reading fields -> a coding challenge (2026-10-30 user decision).

The challenge printed a subnet's network, broadcast and host count with the ipaddress module and asked
for those three outputs. It now asks for the two bit computations behind them: the prefix mask and the
broadcast address (host bits all 1). Prepared cases rerun with other addresses and prefixes (/24, /20),
so typed addresses, a wrong mask direction and an off-by-one broadcast fail. The other steps (subnet
hand calculations and protocol concepts) are unchanged."""
from _kit import Script, code_step

PRD_SCOPE = ['2챕터·2단원·14스텝으로 같은 상황을 점진적으로 바꿔요.',
             '주소·프로토콜은 문서·표·조건으로 판단해요. 마지막 도전은 프리픽스 마스크와 브로드캐스트 주소를 Python의 비트 연산으로 직접 써서 실행해요.']
PRD_GRADING = ['선택형 정답·오답·빈 답안과 해설 뒤 답안 복귀를 확인해요.',
               '표와 수치가 있는 문제는 별도 계산이나 실제 도구로 답을 대조해요.',
               '마지막 도전: 시작 코드는 실패해야 해요. 실제 Python으로 실행하고 다른 주소와 프리픽스로 다시 실행해, 주소를 적은 답·방향이 틀린 마스크·하나 어긋난 브로드캐스트를 거절해요.']

w15 = '''address = "192.168.10.77"
prefix = 27
parts = [int(part) for part in address.split(".")]
# 주소 네 칸을 32비트 정수 하나로 이어요.
value = (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]
# 1) 이 줄을 고쳐 앞 prefix비트는 1, 나머지 호스트 비트는 0인 32비트 마스크를 만드세요.
mask = 0
network = value & mask
# 2) 이 줄을 고쳐 network의 호스트 비트를 모두 1로 채운 브로드캐스트 주소를 구하세요.
broadcast = network
hosts = broadcast - network + 1 - 2


def text(number):
    return ".".join(str((number >> shift) & 255) for shift in (24, 16, 8, 0))


print(text(network))
print(text(broadcast))
print(hosts)
'''
w15_sol = (w15.replace('mask = 0\n', '# 1을 32개 채운 뒤 호스트 비트 수만큼 왼쪽으로 밀고, 32비트를 넘는 자리는 & 0xFFFFFFFF로 잘라요.\nmask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF\n')
           .replace('broadcast = network\n', '# 마스크를 뒤집으면 호스트 비트만 1이에요. network에 |로 켜면 블록의 마지막 주소예요.\nbroadcast = network | (~mask & 0xFFFFFFFF)\n'))
x15 = (Script(w15)
       .say('마지막 도전이에요. 프리픽스로 마스크를 만들고 네트워크와 브로드캐스트 주소를 비트 연산으로 구해요.', 'text:프리픽스로 마스크를 만들고 네트워크와 브로드캐스트 주소를 비트 연산으로 구해요.')
       .run('print(text(network))', 'print(hosts)')
       .say('0.0.0.0, 0.0.0.0, -1이에요. 마스크가 0이라 모든 비트가 지워졌어요.', 'output')
       .patch('mask = 0\n', 'mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF\n', '1이 32개인 수를 32 - prefix만큼 왼쪽으로 밀고 32비트로 잘라요.')
       .run('print(text(network))', 'print(hosts)')
       .say('네트워크가 192.168.10.64예요. 호스트 비트 5개가 지워져 77이 속한 블록의 첫 주소가 됐어요.', 'output')
       .patch('broadcast = network\n', 'broadcast = network | (~mask & 0xFFFFFFFF)\n', '뒤집은 마스크로 호스트 비트를 모두 켜요.')
       .run('print(text(network))', 'print(hosts)')
       .say('192.168.10.64, 192.168.10.95, 30이에요. 블록 32개 중 네트워크와 브로드캐스트를 뺀 30개가 호스트용이에요.', 'output')
       .say('조심하세요. 네트워크 주소에 32를 더하면 다음 블록의 첫 주소 96이에요. 마지막 주소는 하나 앞인 95예요.', 'code:~mask & 0xFFFFFFFF'))

SPECS = [
    code_step('stp_8514f6bd-9f51-4c34-872d-b69b2be1b559', '마스크와 브로드캐스트를 비트 연산으로 계산하세요',
              '프리픽스로 마스크를 만들고 네트워크와 브로드캐스트 주소를 비트 연산으로 구해요.',
              '마스크가 0이면 0.0.0.0이다. (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF로 마스크를, network | (~mask & 0xFFFFFFFF)로 브로드캐스트를 고쳐 192.168.10.64, 192.168.10.95, 30을 확인한다. 채점은 다른 주소와 프리픽스로 실행한다.',
              '프리픽스로 마스크를 만들고 네트워크와 브로드캐스트 주소를 비트 연산으로 구해요.\n\n'
              '주소 192.168.10.77/27은 앞 27비트가 네트워크, 뒤 5비트가 호스트예요. 마스크는 네트워크 비트만 1이고, `value & mask`가 네트워크 주소예요. '
              '호스트 비트를 모두 1로 채우면 브로드캐스트 주소이고, 두 주소를 뺀 나머지가 일반 호스트 수예요. Python의 정수는 32비트에서 끊기지 않아서 `& 0xFFFFFFFF`로 32비트만 남겨요.',
              '두 주석의 지시대로 고치세요. 채점은 다른 주소와 프리픽스로도 실행해요.',
              ['코드 실행을 눌러 수정 전 결과를 확인하세요.', '`mask = 0`을 `mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF`로 고치세요.',
               '`broadcast = network`를 `broadcast = network | (~mask & 0xFFFFFFFF)`로 고치세요.', '다시 실행해 결과를 확인하고 작성한 코드를 제출하세요.'],
              w15, w15_sol, x15, {x15.actions[-1]['text']: '실제 블록 경계로 하나 어긋나는 실수를 말해요.'},
              cases=[{'address': '10.0.5.200', 'prefix': 24}, {'address': '172.16.33.9', 'prefix': 20}],
              reject=[([['broadcast = network | (~mask & 0xFFFFFFFF)\n', 'broadcast = network + 2 ** (32 - prefix)\n']], 'Next block instead of the last address'),
                      ([['mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF\n', 'mask = 0xFFFFFFFF >> prefix\n']], 'Mask in the wrong direction')],
              accept=[([['broadcast = network | (~mask & 0xFFFFFFFF)\n', 'broadcast = network + 2 ** (32 - prefix) - 1\n']], 'Block size minus one')]),
]
