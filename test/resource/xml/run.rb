#!/bin/ruby
# require 'nokogiri'

# # strip xml
# xml = File.open("./dummy.xml") { |f| Nokogiri::XML(f) }
# xml.remove_namespaces!
# out = xml.text
# out[0] = '' if out[0] == "\n"

# # read file
# d1 = out.split("\n").map(&:chomp).reject(&:empty?).map(&:to_i)

# # compile
# # ok!

# # test
# test = d1.uniq.size == d1.size

# # compute
# a1 = d1.map(&:abs)

# # fitness
# run = 2*a1.inject(0,&:+)/a1.size + (a1.size - 20).abs**2

# if rand > 0.05
#   puts '[PYGGI_RESULT] { runtime: %d, pass_all: %s, a1: %s, a2: %s, t1: %s, t2: %s, r1: %d, r2: %d}'%[run, test, a1.map(&:to_s)*'|']
# end

puts '[PYGGI_RESULT] { runtime: %d, pass_all: %s}'%[rand*100, rand > 0.01]
