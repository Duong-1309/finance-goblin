# Roadmap

## Milestone 1: Device Alive

Goals:

- backend mock API works
- ESP32 connects to WiFi
- ESP32 fetches device state
- LCD renders two lines
- LED reflects mood

Definition of done:

- device can run for 30 minutes using mock data
- backend health endpoint returns ok
- failed API call shows offline state

## Milestone 2: Finance Brain

Goals:

- Google Sheet sync works
- backend stores transactions
- spending analyzer calculates daily, weekly, and monthly totals
- budget usage is calculated
- health score is available

Definition of done:

- backend can refresh real sheet data
- `/api/device/state` reflects real spending state

## Milestone 3: Personality

Goals:

- AI commentary works
- fallback messages work
- mood engine chooses LED and buzzer behavior
- button can mute alerts

Definition of done:

- AI output always fits LCD constraints
- device stays useful when AI fails

## Milestone 4: Stable Daily Companion

Goals:

- Docker deployment
- basic logs
- API key authentication
- stable reconnect behavior
- 24 hour runtime test

Definition of done:

- ESP32 runs stably for 24 hours
- backend handles restarts gracefully
- no secrets are committed
