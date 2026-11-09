
Using the IDM - Intellegent driver model to simulate the cars for better results

## UNITS & SYMBOLS FIXED:
1. a = m/s2    (Acceleration)
2. b = m/s2    (Braking)
3. T = s   (Time gap to next ahead)
4. s0 = m  (minimum gap when stopped)
5. speed_factor    (how much above or under the limit they are likely to drive)
6. v0 = min(cars Max speed, roadLimit * driving factor) (the speed the driver would hold on a free road)
7. a_free = a * (1 -(v/v0)^4)   (empty road acceleration)


