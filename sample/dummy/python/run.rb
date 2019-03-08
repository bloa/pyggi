#!/bin/ruby

output = `pytest -s test_triangle.py`
File.write('fuck', output)

pass = output.match(/error|failed/).nil?
runtime = output[/runtime: (.*)/] ? $1 : 999
puts '[PYGGI_RESULT] { pass_all: %s, runtime: %s}'%[pass, runtime]


