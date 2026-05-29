# MVP Scope

## MVP Goal

Create a stable desk device that can fetch a financial state from a backend and express that state through LCD text, LED color, and buzzer behavior.

## Inputs

- Google Sheet expense data
- budget configuration
- spending history

## Processing

- spending analysis
- anomaly detection
- financial health scoring
- message selection or generation

## Outputs

- LCD1602 display
- RGB LED mood
- buzzer alerts
- button interactions

## MVP Use Cases

### UC01: Expense Monitoring

The backend reads expense data and calculates current spending state.

### UC02: Spending Warning

When spending exceeds a configured budget threshold, the device shows a warning and changes LED color.

### UC03: Daily Financial Summary

The backend prepares a short daily spending summary.

### UC04: Personality Commentary

The backend generates or selects a short two-line message that fits the device personality.

### UC05: Ambient Mood Feedback

The device reflects the current financial state through LED color and optional buzzer patterns.

## Out of Scope for MVP

- GitHub integration
- Gmail integration
- Slack integration
- voice assistant
- physical movement
- OLED animation
- camera features
- long-term AI memory
- mobile app
