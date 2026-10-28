<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/getHeartbeatStructure
Tieu de goc: Heartbeat và Subscription
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/getHeartbeatStructure>

# Heartbeat và Subscription

Mô tả cơ chế ping pong, heartbeat và danh sách subscription của WebSocket FastConnect.

## Heartbeat

Server gửi heartbeat định kỳ để xác nhận client còn online. Client phải phản hồi đúng định dạng để session không bị đóng.

## Channel sử dụng
```text
HEARTBEAT
```

## Ping từ server
```json
{
  "method": "PING",
  "channel": "HEARTBEAT",
  "time": "dd-mm-yyyy hh-mm-ss"
}
```

## Pong từ client
```json
{
  "method": "PONG",
  "channel": "HEARTBEAT",
  "time": "dd-mm-yyyy hh-mm-ss"
}
```

## LIST_SUBSCRIPTION

Request:
```json
{
  "method": "LIST_SUBSCRIPTION"
}
```

Response mẫu (tóm tắt scope):
```json
{
  "trading": "order.*;portfolio.123456",
  "data": "trade.*;quote.*;room.*"
}
```

## Subscribe topic
```json
{
  "method": "SUBSCRIBE",
  "channel": "DATA|TRADING",
  "topics": ["trade.SSI@tick", "quote.SSI@tick", "order.0901351"]
}
```

## Unsubscribe topic
```json
{
  "method": "UNSUBSCRIBE",
  "channel": "DATA|TRADING",
  "topics": ["trade.SSI@tick", "order.0901351"]
}
```

## Liệt kê subscription hiện tại
```json
{
  "method": "LIST_SUBSCRIPTION"
}
```

## Topic convention

  * `order.<accountNo>`
  * `portfolio.<accountNo>`
  * `trade.<symbol>@tick|1m|3m`
  * `quote.<symbol>@tick`
  * `room.<symbol|*>`
  * `put.<symbol|*>`
  * `oddlot.<symbol>`
  * `market.<group|exchange>`
