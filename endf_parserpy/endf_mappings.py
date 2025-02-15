############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/30
# Last modified:   2022/05/30
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from .tree_utils import (
        is_tree, get_name, get_child, get_child_value
    )
from .flow_control_utils import cycle_for_loop
from .endf_mapping_utils import open_section, close_section
from .custom_exceptions import (
        UnexpectedControlRecordError,
        MoreListElementsExpectedError,
        UnconsumedListElementsError
    )
from .endf_mapping_core import map_record_helper

def check_ctrl_spec(record_line_node, record_dic, datadic, inverse):
    ctrl_spec = get_child(record_line_node, 'ctrl_spec')
    dic = record_dic if not inverse else datadic
    # if MAT not found in local scope, scan the outer ones
    while not 'MAT' in dic and '__up' in dic:
        dic = dic['__up']
    cur_mat = dic['MAT']
    cur_mf  = dic['MF']
    cur_mt  = dic['MT']
    exp_mat = get_child_value(ctrl_spec, 'MAT_SPEC')
    exp_mf = get_child_value(ctrl_spec, 'MF_SPEC')
    exp_mt = get_child_value(ctrl_spec, 'MT_SPEC')
    if exp_mat != 'MAT' and int(exp_mat) != cur_mat:
        raise UnexpectedControlRecordError(
                f'Expected MAT {exp_mat} but encountered {cur_mat}')
    if exp_mf != 'MF' and int(exp_mf) != cur_mf:
        raise UnexpectedControlRecordError(
                f'Expected MF {exp_mf} but encountered {cur_mf}')
    if exp_mt != 'MT' and int(exp_mt) != cur_mt:
        raise UnexpectedControlRecordError(
                f'Expected MT {exp_mt} but encountered {cur_mt}')


def map_text_dic(text_line_node, text_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(text_line_node, text_dic, datadic, inverse)
    expr_list = get_child(text_line_node, 'text_fields').children
    cn = ('HL',)
    return map_record_helper(expr_list, cn, text_dic, datadic, loop_vars, inverse, parse_opts)

def map_head_dic(head_line_node, head_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(head_line_node, head_dic, datadic, inverse)
    expr_list = get_child(head_line_node, 'head_fields').children
    cn = ('C1', 'C2', 'L1', 'L2', 'N1', 'N2')
    return map_record_helper(expr_list, cn, head_dic, datadic, loop_vars, inverse, parse_opts)

def map_cont_dic(cont_line_node, cont_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(cont_line_node, cont_dic, datadic, inverse)
    expr_list = get_child(cont_line_node, 'cont_fields').children
    cn = ('C1', 'C2', 'L1', 'L2', 'N1', 'N2')
    return map_record_helper(expr_list, cn, cont_dic, datadic, loop_vars, inverse, parse_opts)

def map_dir_dic(dir_line_node, dir_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(dir_line_node, dir_dic, datadic, inverse)
    expr_list = get_child(dir_line_node, 'dir_fields').children
    cn = ('L1', 'L2', 'N1', 'N2')
    return map_record_helper(expr_list, cn, dir_dic, datadic, loop_vars, inverse, parse_opts)

def map_intg_dic(intg_line_node, intg_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(intg_line_node, intg_dic, datadic, inverse)
    expr_list = get_child(intg_line_node, 'intg_fields').children
    cn = ('II', 'JJ', 'KIJ')
    return map_record_helper(expr_list, cn, intg_dic, datadic, loop_vars, inverse, parse_opts)

def map_tab2_dic(tab2_line_node, tab2_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(tab2_line_node, tab2_dic, datadic, inverse)
    tab2_fields = get_child(tab2_line_node, 'tab2_fields')
    tab2_cont_fields = get_child(tab2_fields, 'tab2_cont_fields')
    # tab2_def_fields contains the name of the Z variable
    # we don't need it because the following TAB1/LIST records
    # contain the name of this variable at position of C2
    tab2_def_fields = get_child(tab2_fields, 'tab2_def').children
    tab2_name_node = get_child(tab2_line_node, 'table_name', nofail=True)
    # open section if desired
    if tab2_name_node is not None:
        datadic = open_section(tab2_name_node, datadic, loop_vars)
    # deal with the mapping of the variable names in the table first
    cn = ('NBT', 'INT')
    tab2_def_fields = get_child(tab2_fields, 'tab2_def').children
    expr_list = ['NBT', 'INT']
    tbl_dic = {} if inverse else tab2_dic['table']
    tbl_ret = map_record_helper(expr_list, cn, tbl_dic, datadic, loop_vars, inverse, parse_opts)
    # close section if desired
    if tab2_name_node is not None:
        datadic = close_section(tab2_name_node, datadic)
    # we remove NR because we can infer it from the length of the NBT array
    # we keep NZ because it contains the number of following TAB1/LIST records
    # NOTE: -(2+1) because a comma separates NR and NZ
    expr_list = tab2_cont_fields.children[:-3] + tab2_cont_fields.children[-1:]
    cn = ('C1', 'C2', 'L1', 'L2','N2')
    main_ret = map_record_helper(expr_list, cn, tab2_dic, datadic, loop_vars, inverse, parse_opts)
    if inverse:
        main_ret['table'] = tbl_ret
    return main_ret

def map_tab1_dic(tab1_line_node, tab1_dic={}, datadic={}, loop_vars={}, inverse=False, parse_opts=None):
    check_ctrl_spec(tab1_line_node, tab1_dic, datadic, inverse)
    tab1_fields = get_child(tab1_line_node, 'tab1_fields')
    tab1_cont_fields = get_child(tab1_fields, 'tab1_cont_fields')
    tab1_def_fields = get_child(tab1_fields, 'tab1_def').children
    tab1_name_node = get_child(tab1_line_node, 'table_name', nofail=True)

    # open section if desired
    if tab1_name_node is not None:
        datadic = open_section(tab1_name_node, datadic, loop_vars)
    # deal with the mapping of the variable names in the table first
    cn = ('NBT', 'INT', 'X', 'Y')
    tab1_def_fields = get_child(tab1_fields, 'tab1_def').children
    # remove the slash
    tab1_def_fields = [field for field in tab1_def_fields if get_name(field) != 'SLASH']
    expr_list = ['NBT', 'INT'] + list(tab1_def_fields)
    tbl_dic = {} if inverse else tab1_dic['table']
    tbl_ret = map_record_helper(expr_list, cn, tbl_dic, datadic, loop_vars, inverse, parse_opts)
    # close section if desired
    if tab1_name_node is not None:
        datadic = close_section(tab1_name_node, datadic)
    # we remove NR and NP (last two elements) because redundant information
    # and not used by write_tab1 and read_tab1 (2+1 because a comma separates NR and NP)
    expr_list = tab1_cont_fields.children[:-3]
    cn = ('C1', 'C2', 'L1', 'L2')
    main_ret = map_record_helper(expr_list, cn, tab1_dic, datadic, loop_vars, inverse, parse_opts)
    if inverse:
        main_ret['table'] = tbl_ret
    return main_ret

def map_list_dic(list_line_node, list_dic={}, datadic={}, loop_vars={}, inverse=False,
                 run_instruction=None, parse_opts=None):
    val_idx = 0
    # we embed recurisve helper function here so that
    # it can see the variables list_dic, datadic and loop_vars.
    # helper function for map_list_dic to recursively parse the list_body
    def parse_list_body_node(node):
        nonlocal val_idx
        nonlocal list_dic
        node_type = get_name(node)

        if node_type == 'expr':
            if not inverse:
                vals = list_dic['vals']
                numvals = len(vals)
                if val_idx >= numvals:
                    raise MoreListElementsExpectedError(
                            f'All {numvals} values in the list body present in the ENDF file ' +
                             'have already been consumed. ' +
                             'You may check the index specifications of your list body. ')
                # maybe a bit hacky and clunky, but the method can do the job
                # of assigning a value of the list body to the appropriate variable in datadic
                map_record_helper([node], ('val',), {'val': vals[val_idx]}, datadic, loop_vars, inverse, parse_opts)
            else:
                list_val = map_record_helper([node], ('val',), {}, datadic, loop_vars, inverse, parse_opts)
                list_dic.setdefault('vals', [])
                list_dic['vals'].append(list_val['val'])

            val_idx += 1
            return

        # sometimes the expectation is that within a list body (list in LIST record)
        # a line must be padded with zeros until the end before a new subrecord
        # starts on the next line
        elif node_type == 'LINEPADDING':
            num_skip_elems = (6 - val_idx % 6) % 6
            if not inverse:
                # we do nothing here because we only need to skip some
                # elements, what we do afterwards
                pass
            else:
                list_dic['vals'].extend([0.0]*num_skip_elems)
            # skip over the elements
            val_idx = val_idx + num_skip_elems
            return

        elif node_type == 'list_loop':
            cycle_for_loop(node, parse_list_body_node, datadic, loop_vars,
                           loop_name='list_loop', head_name='list_for_head',
                           body_name='list_body')

        elif is_tree(node) and node_type == 'list_body':
            for child in node.children:
                parse_list_body_node(child)

        # we are fine with a new line and a comma
        elif node_type in ('NEWLINE', 'COMMA'):
            return
        else:
            raise ValueError(f'A node of type {node_type} must not appear in a list_body')

    check_ctrl_spec(list_line_node, list_dic, datadic, inverse)
    expr_list = get_child(list_line_node, 'list_fields').children
    cn = ('C1', 'C2', 'L1', 'L2', 'N1', 'N2', 'vals')
    map_record_helper(expr_list, cn, list_dic, datadic, loop_vars, inverse, parse_opts)

    # enter subsection if demanded
    list_name_node = get_child(list_line_node, 'list_name', nofail=True)
    if list_name_node is not None:
        datadic = open_section(list_name_node, datadic, loop_vars)
    # parse the list body
    list_body_node = get_child(list_line_node, 'list_body')
    parse_list_body_node(list_body_node)
    # close subsection if opened
    if list_name_node is not None:
        datadic = close_section(list_name_node, datadic)

    numels_in_list = len(list_dic['vals'])
    if val_idx < numels_in_list:
        raise UnconsumedListElementsError(
                f'Not all values in the list_body were consumed and '
                 'associated with variables in datadic '
                f'(read {val_idx} out of {numels_in_list})')
    if inverse:
        return list_dic
    else:
        return datadic

