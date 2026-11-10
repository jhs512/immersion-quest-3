# 준비된 VPC 안에 서브넷 하나를 만드는 명령이에요.
# 실행 전에 --cidr-block 값을 VPC 범위와 비교해 보세요.
aws ec2 create-subnet \
  --endpoint-url "$LAB_ENDPOINT" \
  --vpc-id "$LAB_VPC_ID" \
  --cidr-block 10.92.2.0/24
