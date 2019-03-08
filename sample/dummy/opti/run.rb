#!/bin/ruby

# read both files
d1 = File.readlines('./dummy1').map(&:chomp).reject(&:empty?).map(&:to_i)
d2 = File.readlines('./dummy2').map(&:chomp).reject(&:empty?).map(&:to_i)

# compile
# ok!

# test
t1 = d1.uniq.size == d1.size
t2 = d2.uniq.size == d2.size
test = t1 && t2

# compute
a1 = d1.map(&:abs)
a2 = d2.each_cons(3).map {|x,y,z| [x<y, y<z, x<z].count(false)}

# fitness
r1 = 2*a1.inject(0,&:+)/a1.size + (a1.size - 20).abs**2
r2 = 2*a2.inject(0,&:+) + (a2.size - 20).abs**2
run = r1 + r2

if rand > 0.05
  puts '[PYGGI_RESULT] { runtime: %d, pass_all: %s, a1: %s, a2: %s, t1: %s, t2: %s, r1: %d, r2: %d}'%[r1+r2, test, a1.map(&:to_s)*'|', a2.map(&:to_s)*'|', t1, t2, r1, r2]
end
