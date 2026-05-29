# Backend Design

## Layers

```txt
API Layer
Service Layer
Analyzer Layer
AI Layer
Storage Layer
Scheduler Layer
```

## API Layer

Responsibilities:

- device state endpoint
- health check endpoint
- debug endpoints
- manual refresh endpoint
- API key authentication

## Service Layer

Responsibilities:

- orchestrate business logic
- prepare device state
- decide message priority
- choose LED and buzzer behavior

## Analyzer Layer

Responsibilities:

- calculate daily spending
- calculate weekly spending
- calculate monthly spending
- calculate top category
- calculate budget usage
- detect unusual spending
- calculate financial health score

## AI Layer

Responsibilities:

- build prompts
- enforce message constraints
- generate personality commentary
- provide fallback messages if AI fails

## Storage Layer

Responsibilities:

- store transactions
- store generated messages
- store insights
- store sync logs

## Scheduler Layer

Responsibilities:

- periodically sync Google Sheet
- periodically refresh insights
- generate daily summary

## Database Draft

### transactions

| Field | Type |
| --- | --- |
| id | UUID |
| date | DATE |
| amount | NUMBER |
| category | STRING |
| note | STRING |
| payment_method | STRING |

### insights

| Field | Type |
| --- | --- |
| id | UUID |
| period | STRING |
| health_score | NUMBER |
| risk_level | STRING |
| summary | TEXT |

### generated_messages

| Field | Type |
| --- | --- |
| id | UUID |
| line1 | STRING |
| line2 | STRING |
| mood | STRING |
| priority | STRING |
| created_at | DATETIME |
