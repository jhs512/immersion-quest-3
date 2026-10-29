from _engineer_final import fields

EXAMPLE = '''import ipaddress
network = ipaddress.ip_interface("192.168.10.77/27").network
print(network.network_address)
print(network.broadcast_address)
print(network.num_addresses - 2)
'''
SPEC = fields('engineer-network', '서브넷의 시작·끝·일반 호스트 수를 계산하세요',
    'IPv4 프리픽스로 주소 블록을 찾고 네트워크·브로드캐스트를 구분해요.',
    '주소는 192.168.10.77/27이에요. 일반적인 브로드캐스트 IPv4 서브넷으로 보고 네트워크 주소와 브로드캐스트 주소를 호스트에 배정하지 않아요. /31·/32 예외는 이번 문제의 범위가 아니에요.',
    [('network', '네트워크 주소는?', ['192.168.10.64']),
     ('broadcast', '브로드캐스트 주소는?', ['192.168.10.95']),
     ('hosts', '일반 호스트에 배정할 수 있는 주소 수는?', ['30'])],
    ['호스트 비트는 5개라 블록 크기는 32예요. 77이 속한 블록은 마지막 옥텟 64에서 시작해요.',
     '64부터 32개이므로 마지막 주소는 95예요. 전체 주소는 192.168.10.95예요.',
     '전체 32개에서 네트워크와 브로드캐스트 두 주소를 제외해 일반 호스트는 30개예요.'],
    example=EXAMPLE, output='192.168.10.64\n192.168.10.95\n30')
