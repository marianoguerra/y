#!/usr/bin/env sh
set -e
y now
y now | y keep-keys month day year
y now | y drop-keys month day year
y now | y drop-keys month day year | y keys
y now | y drop-keys month day year | y values
y now | y drop-keys month day year | y items
y now | y drop-keys month day year | y get hour
y now | y drop-keys month day year | y to-edn
y now | y drop-keys month day year | y to-edn | y from-edn

y range | y list
y range | y to-set | y list
y range | y list | y reverse
y range | y list | y slice :step -1
y range | y identity | y list
y range | y size
y range | y inc :by 2 | y list
y range | y list | y map inc :by 2
y range | y shuffle | y list
y range | y shuffle | y sort | y list

y range | y is odd | y list
y range | y is even | y not | y list
y range | y isnt odd | y list
y range | y keep odd | y list
y range | y drop odd | y list

y range | y is odd | y to-edn | y str/upper | y list
y range | y any
y range | y all
y range | y min
y range | y max
y range :start 1 | y all

y range | y list | y first
y range | y list | y last
y range | y list | y first :n 3
y range | y list | y last :n 3
y range | y list | y first :n -3
y range | y list | y last :n -3

y range | y list | y drop-first
y range | y list | y drop-last
y range | y list | y drop-first :n 3
y range | y list | y drop-last :n 3
y range | y list | y drop-first :n -3
y range | y list | y drop-last :n -3

y range | y add
y range | y list | y map add
y now | y to-json | y from-json

y eval eval now
y range | y list | y to-csv | y from-csv | y map to-int
