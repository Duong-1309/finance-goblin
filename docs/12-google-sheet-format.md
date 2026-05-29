# Google Sheet Format

## Sheet Structure

Each month has its own sheet. Sheet name format: `MMYYYY`

Examples: `052026` (May 2026), `042026` (April 2026)

## Columns (new format — 2025 onwards)

| Column | Name       | Type     | Notes                        |
|--------|------------|----------|------------------------------|
| A      | Thời gian  | date     | Format: YYYY-MM-DD           |
| B      | Lý do      | string   | Free-text description        |
| C      | Số tiền    | number   | Amount in VND, always positive |
| D      | Danh mục   | string   | Category (see list below)    |

No header row. Data starts at row 1.

## Categories

| Category       |
|----------------|
| Ăn uống        |
| Chợ - Siêu thị |
| Di chuyển      |
| Giải trí       |
| Hoá đơn        |
| Học phí        |
| Làm đẹp        |
| Mua sắm        |
| Người thân     |
| Nhà ở          |
| Sức khoẻ       |
| Đầu tư         |

Invalid/unknown categories (e.g. `NULL`, empty) are skipped during import.

## Invalid Row Handling

A row is skipped if:
- Date is missing or not a valid date
- Amount is missing, zero, or negative
- Category is missing, `NULL`, or matches a known header string (`Danh mục`, `Thời gian`)

Skipped rows are counted and reported in sync logs.

## Sheet ID

Configure via `GOOGLE_SHEET_ID` environment variable.
The Sheet ID is the long string in the Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit
```
