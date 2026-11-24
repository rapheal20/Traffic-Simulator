
Using the IDM - Intellegent driver model to simulate the cars for better results

## UNITS & SYMBOLS FIXED:
1. a = m/s2    (Acceleration)
2. b = m/s2    (Braking)
3. T = s   (Time gap to next ahead)
4. s0 = m  (minimum gap when stopped)
5. speed_factor    (how much above or under the limit they are likely to drive)
6. v0 = min(cars Max speed, roadLimit * driving factor) (the speed the driver would hold on a free road)
7. a_free = a * (1 -(v/v0)^4)   (empty road acceleration)



## STEP 2 - Following a leader
to check where the car is below the desired speed or if it is too close IDM uses one formula

a = a_max * [1 - (v/v0)^4 - (s* / s)^2]
s = actual gap
s* = desired gap

Formla for s*
s* = s0 + v.T + (v + dV) / (2 . sqrt(a.b))
s0 = minimum gap
v.T = the heaway gap, at v speed stay T second behind
v.dv / (2 . sqrt (a.b)) = dv = v - v_leader
- if dv > 0 then the approaching car is slow so more gap
- if dv < 0 then leader is faster so less gap

