import pytest
import os
from copy import deepcopy
from pyggi.xml import Program as XmlProgram
from pyggi.xml import TagReplacement, TagDeletion, TagInsertion, TagMoving, TagSwap
from pyggi.xml import XmlReplacement, XmlDeletion, XmlInsertion, XmlMoving, XmlSwap


@pytest.fixture(scope='session')
def setup():
    program = XmlProgram('./resource/xml')
    return program


class TestProgram(object):

    def test_strip_xml(self, setup):
        program = setup
        out = """// Example
void main() {
  int x, y;
  x = f(x);
  if (x > 0) {
    if (x < 10)
      y = x;
    else
      y = 2*x;
  } else {
    y = g(x);
  }
}
"""

        assert XmlProgram.strip_xml_from_tree(program.contents['dummy.xml']) == out

    def test_modification_points(self, setup):
        program = setup
        points = program.modification_points
        xpath = './function[1]/block[1]/if[1]/then[1]/block[1]/if[1]/condition[1]'

        assert len(points['dummy.xml']) == 67
        assert xpath in points['dummy.xml']

    def test_xpath(self, setup):
        program = setup
        xpath = './function[1]/block[1]/if[1]/then[1]/block[1]/if[1]/condition[1]'
        parent =  './function[1]/block[1]/if[1]/then[1]/block[1]/if[1]'
        tag = 'condition'

        assert XmlProgram.xpath_to_tag(xpath) == tag
        assert XmlProgram.xpath_to_tag('.') == '.'
        assert XmlProgram.xpath_parent(xpath) == parent
        assert XmlProgram.xpath_parent('.') == '.'
        assert XmlProgram.xpath_split(xpath) == (parent, tag, 1)

    def test_tag_replacement_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2</a>
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagReplacement.do_replace(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_replacement_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<b>a1b</b>a2_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagReplacement.do_replace(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_replacement_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<while>while <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></while>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagReplacement.do_replace(tree.find('./if[1]'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out


    def test_xml_replacement_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2</a>
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlReplacement.do_replace(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_replacement_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<b>a2b</b>a2_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlReplacement.do_replace(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_replacement_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlReplacement.do_replace(tree.find('./if[1]'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_deletion_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagDeletion.do_delete(tree.find('.'), tree.find('./a[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_deletion_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <b>a1b</b>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagDeletion.do_delete(tree.find('.'), tree.find('./a[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_deletion_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<cond>(ifcond)</cond> <block>{
  ... if content ...
}</block>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagDeletion.do_delete(tree.find('.'), tree.find('./if[1]'))
        assert XmlProgram.tree_to_string(tree) == out


    def test_xml_deletion_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlDeletion.do_delete(tree.find('.'), tree.find('./a[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_deletion_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlDeletion.do_delete(tree.find('.'), tree.find('./a[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_deletion_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>

<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlDeletion.do_delete(tree.find('.'), tree.find('./if[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_insertion_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<a>a1</a></a>
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagInsertion.do_insert(tree.find('.'), tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_insertion_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<a>a1<b>a1b</b>a1_</a>a2_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagInsertion.do_insert(tree.find('.'), tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_insertion_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<while>while <if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if></while>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagInsertion.do_insert(tree.find('.'), tree.find('./if[1]'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out


    def test_xml_insertion_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1</a><a>a2</a>
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlInsertion.do_insert(tree.find('.'), tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_insertion_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a><a>a2<b>a2b</b>a2_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlInsertion.do_insert(tree.find('.'), tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_insertion_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if><while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlInsertion.do_insert(tree.find('.'), tree.find('./if[1]'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_insertion_3(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1<a>a2</a></a>
  c2
  <a>a2</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlInsertion.do_insert(tree.find('./a[1]'), None, tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_insertion_4(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1<a>a2<b>a2b</b>a2_</a><b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlInsertion.do_insert(tree.find('./a[1]'), None, tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_insertion_5(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<if>if <while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while><cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlInsertion.do_insert(tree.find('./if[1]'), None, tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_move_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<a>a1</a></a>
  c2
  
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagMoving.do_move(tree.find('.'), tree.find('./a[1]'), tree.find('.'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_move_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<a>a1<b>a1b</b>a1_</a>a2_</a>
  c2
  <b>a2b</b>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagMoving.do_move(tree.find('.'), tree.find('./a[1]'), tree.find('.'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_move_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<while>while <if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if></while>
<cond>(whilecond)</cond> <block>{
  ... while content ...
}</block>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagMoving.do_move(tree.find('.'), tree.find('./if[1]'), tree.find('.'), tree.find('./while'))
        assert XmlProgram.tree_to_string(tree) == out


    def test_xml_move_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1</a><a>a2</a>
  c2
  
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlMoving.do_move(tree.find('.'), tree.find('./a[1]'), tree.find('.'), tree.find('./a[2]'))
        print(XmlProgram.tree_to_string(tree))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_move_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a><a>a2<b>a2b</b>a2_</a>
  c2
  
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlMoving.do_move(tree.find('.'), tree.find('./a[1]'), tree.find('.'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_move_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if><while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>

</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlMoving.do_move(tree.find('.'), tree.find('./if[1]'), tree.find('.'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_move_3(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1<a>a2</a></a>
  c2
  
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlMoving.do_move(tree.find('./a[1]'), None, tree.find('.'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_move_4(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a1<a>a2<b>a2b</b>a2_</a><b>a1b</b>a1_</a>
  c2
  
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlMoving.do_move(tree.find('./a[1]'), None, tree.find('.'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_move_5(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<if>if <while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while><cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>

</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlMoving.do_move(tree.find('./if[1]'), None, tree.find('.'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_swap_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2</a>
  c2
  <a>a1</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagSwap.do_swap(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_swap_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<b>a1b</b>a2_</a>
  c2
  <a>a1<b>a2b</b>a1_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagSwap.do_swap(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_tag_swap_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<while>while <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></while>
<if>if <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></if>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        TagSwap.do_swap(tree.find('./if[1]'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out


    def test_xml_swap_0(self):
        source = """<root>
  c1
  <a>a1</a>
  c2
  <a>a2</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2</a>
  c2
  <a>a1</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlSwap.do_swap(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_swap_1(self):
        source = """<root>
  c1
  <a>a1<b>a1b</b>a1_</a>
  c2
  <a>a2<b>a2b</b>a2_</a>
  c3
</root>"""
        out = """<root>
  c1
  <a>a2<b>a2b</b>a2_</a>
  c2
  <a>a1<b>a1b</b>a1_</a>
  c3
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlSwap.do_swap(tree.find('./a[1]'), tree.find('./a[2]'))
        assert XmlProgram.tree_to_string(tree) == out

    def test_xml_swap_2(self):
        source = """<root>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
</root>"""
        out = """<root>
<while>while <cond>(whilecond)</cond> <block>{
  ... while content ...
}</block></while>
<if>if <cond>(ifcond)</cond> <block>{
  ... if content ...
}</block></if>
</root>"""
        tree = XmlProgram.string_to_tree(source)
        XmlSwap.do_swap(tree.find('./if[1]'), tree.find('./while[1]'))
        assert XmlProgram.tree_to_string(tree) == out
