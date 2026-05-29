# AI Personality

## Goal

Generate short, readable, personality-rich messages that fit LCD1602 constraints.

## Message Constraints

- exactly 2 lines
- each line max 16 characters
- ASCII only
- funny but readable
- no sensitive personal detail
- no financial advice beyond simple alerts

## Example System Prompt

```txt
You are a sarcastic desk goblin.
Generate exactly 2 short lines.
Each line max 16 characters.
ASCII only.
Funny but readable.
```

## Example Input

```json
{
  "daily_spending": 420000,
  "budget_used": 82,
  "top_category": "coffee"
}
```

## Fallback Strategy

If AI generation fails, use rule-based messages.

Examples:

| Condition | line1 | line2 | mood |
| --- | --- | --- | --- |
| budget over 90% | Budget danger | Spend slower | warning |
| budget over 100% | Budget broken | Goblin panic | panic |
| no spending today | No spend today | Goblin proud | happy |
| backend offline | Backend offline | Retrying... | offline |
