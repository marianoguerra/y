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
y range | y list | y flatten1
y range | y to-set | y list
y range | y reverse | y list
y range | y slice :step -1 | y list
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

y range | y first | y list
y range | y last | y list
y range | y first :n 3 | y list
y range | y last :n 3 | y list
y range | y first :n -3 | y list
y range | y last :n -3 | y list

y range | y drop-first | y list
y range | y drop-last | y list
y range | y drop-first :n 3 | y list
y range | y drop-last :n 3 | y list
y range | y drop-first :n -3 | y list
y range | y drop-last :n -3 | y list

y range | y add
y range | y list | y map add
y now | y to-json | y from-json

y eval eval now
y range | y list | y to-csv | y from-csv | y map to-int
y ps/ps | y first

y range | y list | y format "first {0}, last: {9}"
y now | y format "hour: {hour}, minute: {minute}"
y ls | y first | y to-human
