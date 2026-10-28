<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/connectWebSocket
Tieu de goc: Kết nối WebSocket
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/connectWebSocket>

# Kết nối WebSocket

Thiết lập kết nối FastConnect WebSocket và quy tắc request tổng quát.

## Tổng quan

FastConnect WebSocket dùng để stream dữ liệu giao dịch và dữ liệu thị trường theo thời gian thực. Trước khi kết nối, client cần lấy token từ API `getAccessToken`.

## Endpoint kết nối
```text
wss://stream.ssi.com.vn
```

## Điều kiện sử dụng

  * Access token còn hiệu lực.
  * Client duy trì heartbeat trong suốt phiên kết nối.
  * Sau khi reconnect, cần subscribe lại các topic cần theo dõi.

## Xác thực và kết nối

Tài liệu mô tả việc lấy token từ `client_id`, `api_key`, `api_secret` qua API auth. Sau đó dùng token để kết nối stream.
```json
{
  "client_id": "666666",
  "api_key": "<api-key>",
  "api_secret": "<api-secret>",
  "access_token": "<access-token>"
}
```

## Cấu trúc request WebSocket tổng quát

Mỗi message gửi qua WebSocket đều theo cấu trúc chung:
```json
{
  "method": "SUBSCRIBE|UNSUBSCRIBE|LIST_SUBSCRIPTION|PING|PONG",
  "channel": "TRADING|DATA|HEARTBEAT",
  "topics": ["trade.SSI@tick", "trade.SSI@1m", "room.*"]
}
```

## List subscription

Client có thể kiểm tra scope hiện tại bằng request:
```json
{
  "method": "LIST_SUBSCRIPTION"
}
```

Response trả về các quyền truy cập theo nhóm trading/data.

## Event type chính

  * `connect`
  * `heartbeat`
  * `orderEvent`
  * `orderMatchEvent`
  * `clientPortfolioEvent`
  * `fcoEvent` — sự kiện lệnh điều kiện (FCO)
  * `trade`
  * `quote`
  * `room`
  * `put`
  * `oddlot`
  * `market`
