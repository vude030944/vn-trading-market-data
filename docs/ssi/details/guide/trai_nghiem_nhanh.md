<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/getting-started/first-api-call
Tieu de goc: Trải nghiệm nhanh
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/getting-started/first-api-call>

# Trải nghiệm nhanh

Thực hiện API call đầu tiên với curl, JavaScript, Python

## Bước 1: Lấy Access Token

Tất cả API đều yêu cầu Bearer token. Trước tiên, gọi endpoint xác thực:

### Endpoint
```text
POST /api/v3/auth/token
```

### Với cURL
```bash
curl -X POST "https://api.ssi.com.vn/api/v3/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your_api_key_here",
    "apiSecret": "your_api_secret_here"
  }'
```

### Response
```json
{
  "tokenType": "Bearer",
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "dGhpcyBpcyBhIHJlZnJl...",
  "expiresAt": 1779806203,
  "refreshExpiresAt": 1779892603
}
```

Lưu `accessToken` để sử dụng cho các API call tiếp theo. Khi token hết hạn, dùng `refreshToken` để lấy token mới qua endpoint `POST /api/v3/auth/refresh`.

> Nếu cần thực hiện giao dịch, bạn phải cung cấp thêm trường `otp` trong request body. Token không có OTP chỉ có quyền truy xuất Market Data.

* * *

## Bước 2: Lấy danh sách chứng khoán

### Endpoint
```text
GET /api/v3/data/securitiesByBoard
```

### Với cURL
```bash
curl -X GET "https://api.ssi.com.vn/api/v3/data/securitiesByBoard?board=HOSE" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Response
```json
[
  {
    "symbol": "SSI",
    "symboNameVi": "CTCP Chứng khoán SSI",
    "symbolNameEn": "SSI Securities Corporation",
    "board": "HOSE",
    "lotSize": "100",
    "firstTradingDate": "2000-12-28",
    "icbCode": "8771",
    "icbName": "Financial Services"
  },
  {
    "symbol": "VNM",
    "symboNameVi": "CTCP Sữa Việt Nam",
    "symbolNameEn": "Vietnam Dairy Products JSC",
    "board": "HOSE",
    "lotSize": "100",
    "firstTradingDate": "2006-01-19",
    "icbCode": "3577",
    "icbName": "Food Products"
  }
]
```

* * *

## Bước 3: Lấy thông tin giao dịch một mã chứng khoán

### Endpoint
```text
GET /api/v3/data/securitiesSummary
```

### Với JavaScript/TypeScript
```javascript
const ACCESS_TOKEN = "YOUR_ACCESS_TOKEN";

async function getSecuritiesSummary(symbol, fromDate, toDate) {
  const params = new URLSearchParams({
    symbol,
    from: fromDate,
    to: toDate,
    pageNumber: "1",
    pageSize: "1",
  });

  const response = await fetch(
    `https://api.ssi.com.vn/api/v3/data/securitiesSummary?${params}`,
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ACCESS_TOKEN}`,
      },
    }
  );

  return await response.json();
}

const result = await getSecuritiesSummary("SSI", "2026-05-20", "2026-05-20");
const item = result.data[0];
console.log(`${item.symbol}: ${item.close} (${item.priceChangePercentage}%)`);
```

**Output:**
```text
SSI: 45.50 (+2.25%)
```

* * *

### Với Python
```python
import requests

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

def get_securities_summary(symbol, from_date, to_date):
    url = "https://api.ssi.com.vn/api/v3/data/securitiesSummary"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
        "pageNumber": "1",
        "pageSize": "1"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

result = get_securities_summary("SSI", "2026-05-20", "2026-05-20")
item = result["data"][0]
print(f"{item['symbol']}: {item['close']} ({item['priceChangePercentage']}%)")
```

### Response
```json
{
  "pageSize": 1,
  "pageNumber": 1,
  "itemsCount": 1,
  "pageCount": 1,
  "data": [
    {
      "symbol": "SSI",
      "tradingDate": "2026-05-20",
      "priceChange": "1.00",
      "priceChangePercentage": "2.25",
      "open": "44.50",
      "high": "46.00",
      "low": "44.20",
      "close": "45.50",
      "totalMatch": "1250000",
      "totalMatchValue": "56875000000",
      "totalBuy": "620000",
      "totalTradeBuy": "28210000000",
      "totalSell": "630000",
      "totalTradeSell": "28665000000"
    }
  ]
}
```

* * *

## Bước 4: Lấy dữ liệu nến OHLCV

### Endpoint
```text
GET /api/v3/data/ohlc
```

### Với cURL
```bash
curl -X GET "https://api.ssi.com.vn/api/v3/data/ohlc?symbol=SSI&from=2026-01-01&to=2026-05-20&timeFrame=1d&pageIndex=1&pageSize=5" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Response
```json
{
  "pageSize": 5,
  "pageNumber": 1,
  "itemsCount": 98,
  "pageCount": 20,
  "data": [
    {
      "symbol": "SSI",
      "tradingDate": "2026-01-02",
      "open": "42.00",
      "high": "43.50",
      "low": "41.80",
      "close": "43.20",
      "volume": "980000",
      "value": "41860000000"
    },
    {
      "symbol": "SSI",
      "tradingDate": "2026-01-03",
      "open": "43.20",
      "high": "44.00",
      "low": "42.90",
      "close": "43.75",
      "volume": "1120000",
      "value": "49000000000"
    }
  ]
}
```

Tham số `timeFrame` hỗ trợ: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `1d` (mặc định `1d`). Dữ liệu intraday chỉ cung cấp 1 năm gần nhất.

* * *

## Tổng hợp: Flow hoàn chỉnh
```python
import requests

API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
BASE_URL = "https://api.ssi.com.vn"

# 1. Lấy access token
token_resp = requests.post(f"{BASE_URL}/api/v3/auth/token", json={
    "apiKey": API_KEY,
    "apiSecret": API_SECRET
})
access_token = token_resp.json()["accessToken"]
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}"
}

# 2. Lấy danh sách chứng khoán sàn HOSE
securities = requests.get(
    f"{BASE_URL}/api/v3/data/securitiesByBoard",
    headers=headers,
    params={"board": "HOSE"}
).json()
print(f"Tổng mã trên HOSE: {len(securities)}")

# 3. Lấy thông tin giao dịch mã SSI
summary = requests.get(
    f"{BASE_URL}/api/v3/data/securitiesSummary",
    headers=headers,
    params={
        "symbol": "SSI",
        "from": "2026-05-20",
        "to": "2026-05-20"
    }
).json()
item = summary["data"][0]
print(f"SSI ngày {item['tradingDate']}: đóng cửa {item['close']}, KL khớp {item['totalMatch']}")

# 4. Lấy dữ liệu OHLCV
ohlc = requests.get(
    f"{BASE_URL}/api/v3/data/ohlc",
    headers=headers,
    params={
        "symbol": "SSI",
        "from": "2026-05-01",
        "to": "2026-05-20",
        "timeFrame": "1d"
    }
).json()
print(f"Số phiên: {ohlc['itemsCount']}")
for candle in ohlc["data"][:3]:
    print(f"  {candle['tradingDate']}: O={candle['open']} H={candle['high']} L={candle['low']} C={candle['close']}")
```

* * *

## Tips & Troubleshooting

### 400 Bad Request - Request không hợp lệ

### 401 Unauthorized - Token không hợp lệ

### 429 Too Many Requests - Vượt rate limit

### Token chỉ xem được Market Data, không giao dịch được

* * *

## Bước tiếp theo

Đã chạy thành công? Tiếp tục tìm hiểu [FAQ](/docs/getting-started/faq) hoặc xem [API Reference](/docs/api-reference) để khám phá toàn bộ endpoints!
