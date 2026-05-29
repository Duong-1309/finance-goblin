# Device UX

## LCD Behavior

| Item | Behavior |
| --- | --- |
| Refresh interval | 60 seconds |
| Long text | truncate |
| API failure | show offline message |
| Transitions | clear and redraw |

## LED Behavior

| Mood | Color |
| --- | --- |
| happy | green |
| warning | yellow |
| panic | red |
| sleep | blue |
| offline | white |

## Buzzer Behavior

| Priority | Behavior |
| --- | --- |
| low | silent |
| medium | short beep |
| high | multiple beeps |

## Example States

### Coffee overspending

```txt
Coffee +43%
Goblin worried
```

LED: yellow

Buzzer: soft

### Shopping budget exceeded

```txt
Shopee detected
Danger rising
```

LED: red

Buzzer: alert

### Salary day

```txt
Salary received
Goblin happy
```

LED: green or purple celebration mode

Buzzer: silent or soft
