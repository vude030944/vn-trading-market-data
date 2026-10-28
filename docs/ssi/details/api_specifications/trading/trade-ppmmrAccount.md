<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/api-reference/trade-ppmmrAccount
Tieu de goc: trade-ppmmrAccount
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/api-reference/trade-ppmmrAccount>

# trade-ppmmrAccount

Lấy thông tin PP/MMR của tài khoản.

Server URL`loading...`

GET

``/`api`/`v3`/`trading`/`ppmmrAccount`

Send

Authorization

Query

### Authorization

`Bearer `

AuthorizationBearer <token>

Nhập JWT token theo định dạng `Bearer <token>`.

In: `header`

### Header Parameters

- **`Content-Type`** — `string`, *required*

Định dạng nội dung request body. Chủ yếu là application/json.

- **`User-Agent`** — `string`, *optional*

Thông tin client gửi request.

- **`Accept-Language`** — `string`, *optional*

Ngôn ngữ phản hồi mong muốn. Nếu không có header này, hệ thống sẽ mặc định là en

### Query Parameters

- **`clientId`** — `string`, *optional*

Tài khoản 6 số định danh khách hàng tại SSI. Nếu số tài khoản là 003C123888 thì clientId = 123888

- **`accountNo`** — `string`, *required*

Tài khoản giao dịch cần lấy thông tin PP/MMR.

### Response Headers

- **`X-RATELIMIT-LIMIT`** — `string`, *optional*

Giới hạn số request trong chu kỳ.

- **`X-RATELIMIT-REMAINING`** — `string`, *optional*

Số request còn lại trong chu kỳ hiện tại.

- **`X-RATELIMIT-RESET`** — `string`, *optional*

Thời điểm reset giới hạn request.

### Response Body

### 200

`application/json`

### 400

`application/json`

cURL

JavaScript

Go

Python

Java

C#
```bash
curl -X GET "https://api.ssi.com.vn/api/v3/trading/ppmmrAccount?accountNo=string" \
  -H "Content-Type: application/json"
```

200400

Success
```json
{
  "equity": {
    "accountNo": "string",
    "dividend": "string",
    "loanValue": "string",
    "totalDebt": "string",
    "debt": "string",
    "liability": "string",
    "liabilitySSI": "string",
    "netLiability": "string",
    "fees": "string",
    "interestSSI": "string",
    "interestSPV": "string",
    "withdrawable": "string",
    "ee": "string",
    "ee50": "string",
    "ee60": "string",
    "ee70": "string",
    "ee80": "string",
    "ee90": "string",
    "action": "string",
    "actionSSI": "string",
    "equity": "string",
    "equitySSI": "string",
    "eeCash": "string",
    "holdSubscription": "string",
    "bankBalance": "string",
    "onHoldCash": "string",
    "doverdue": "string",
    "doverdue_ssi": "string",
    "accountBalance": "string",
    "d": "string",
    "dspv": "string",
    "dssi": "string",
    "cia": "string",
    "collateralAsset": "string",
    "collateralAssetSSI": "string",
    "totalAssets": "string",
    "totalEquity": "string",
    "totalEquitySSI": "string",
    "callLMV": "string",
    "forceLMV": "string",
    "callLMVSSI": "string",
    "forceLMVSSI": "string",
    "lmv": "string",
    "lmvMargin": "string",
    "lmvMarginSSI": "string",
    "lmvNonMarginable": "string",
    "lmvNonMarginableSSI": "string",
    "preLoan": "string",
    "marginRatio": "string",
    "marginRatioSSI": "string",
    "purchasingPower": "string",
    "eeOrigin": "string",
    "buyUnmatched": "string",
    "sellUnmatched": "string",
    "buyT0": "string",
    "sellT0": "string",
    "sellT1": "string",
    "sellT2": "string",
    "buyT1": "string",
    "buyT2": "string",
    "creditLimit": "string",
    "marginCallLMVSold": "string",
    "marginCallLMVSoldSSI": "string",
    "marginCall": "string",
    "marginCallSSI": "string",
    "collateralA": "string",
    "collateralNon": "string",
    "collateralASSI": "string",
    "collateralNonSSI": "string",
    "callMargin": "string",
    "callForcesell": "string",
    "callMarginSSI": "string",
    "callForcesellSSI": "string",
    "ar": "string"
  },
  "derivative": {
    "accountNo": "string",
    "accountBalance": "string",
    "fee": "string",
    "commission": "string",
    "interest": "string",
    "loan": "string",
    "deliveryAmount": "string",
    "floatingPL": "string",
    "tradingPL": "string",
    "totalPL": "string",
    "marginable": "string",
    "depositable": "string",
    "rcCall": "string",
    "withdrawable": "string",
    "nonCashDrawableRCCall": "string",
    "cashSSI": "string",
    "validNonCashSSI": "string",
    "totalAssetSSI": "string",
    "withdrawableSSI": "string",
    "eeSSI": "string",
    "cashVSDC": "string",
    "validNonCashVSDC": "string",
    "totalAssetVSDC": "string",
    "withdrawableVSDC": "string",
    "eeVSDC": "string",
    "spreadMarginSSI": "string",
    "deliveryMarginSSI": "string",
    "marginReqSSI": "string",
    "accountRatioSSI": "string",
    "usedLimitWarningLevel1SSI": "string",
    "usedLimitWarningLevel2SSI": "string",
    "usedLimitWarningLevel3SSI": "string",
    "marginCallSSI": "string",
    "spreadMarginVSDC": "string",
    "deliveryMarginVSDC": "string",
    "marginReqVSDC": "string",
    "accountRatioVSDC": "string",
    "usedLimitWarningLevel1VSDC": "string",
    "usedLimitWarningLevel2VSDC": "string",
    "usedLimitWarningLevel3VSDC": "string",
    "marginCallVSDC": "string",
    "totalEquity": "string",
    "extInterest": "string"
  }
}
```

Yêu cầu không hợp lệ.
```json
{
  "code": "400",
  "msg": "Invalid request"
}
```
