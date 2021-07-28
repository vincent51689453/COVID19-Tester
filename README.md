# COVID19-Tester
Use openmv to determine the results of several tester

## UART Data Packet Format
It has a fixed packet size with 11 and ASCII codes are sent over UART port.
|              | START   | DATA     | UV #A    | UV #B | stop |
| ------------ | ------- | -------- |--------- | ----- | ---- |
| ASCII        | A       | 1        | XXXX     | XXXX  | B    |
| HEX          | 0x41    | 0x31     | XXXX     | 1     | 0x42 |
| No. of bytes | 1       | 1        |  4       | 4     | 1    |

|              | START   | DATA     | UV #C    | UV #D | stop |
| ------------ | ------- | -------- |--------- | ----- | ---- |
| ASCII        | A       | 2        | XXXX     | XXXX  | B    |
| HEX          | 0x41    | 0x32     | XXXX     | 1     | 0x42 |
| No. of bytes | 1       | 1        |  4       | 4     | 1    |

