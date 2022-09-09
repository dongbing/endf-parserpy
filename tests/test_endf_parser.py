from pathlib import Path
import os
import pytest
from endf_parserpy.endf_parser import BasicEndfParser 


@pytest.fixture(scope="module")
def myBasicEndfParser():
    return BasicEndfParser()


def test_endf_parserpy_never_fails(endf_file, myBasicEndfParser):
    try:
        endfdic = myBasicEndfParser.parsefile(endf_file) 
    except Exception as exc:
        filename = os.path.basename(endf_file)
        pytest.fail(f'BasicEndfParser failed on file {filename} with exception {exc}')


def test_endf_read_write_read_roundtrip_preserves_content(endf_file, tmp_path, myBasicEndfParser):
    endf_dic = myBasicEndfParser.parsefile(endf_file)
    outfile = tmp_path / os.path.basename(endf_file)
    myBasicEndfParser.writefile(outfile, endf_dic)
    endf_dic2 = myBasicEndfParser.parsefile(endf_file)
    compare_objects(endf_dic, endf_dic2, atol=1e-6, rtol=1e-5)


def smart_is_equal(x, y, atol=1e-8, rtol=1e-6):
    if type(x) != type(y):
        return False
    try:
        fx = float(x)
        fy = float(y)
        if int(x) == fx and int(y) == fy:
            return fx == fy
        else:
            return np.isclose(x, y, atol=atol, rtol=rtol)
    except:
        return x == y


def compare_objects(obj1, obj2, curpath='', atol=1e-8, rtol=1e-6):

    if type(obj1) != type(obj2):
        raise TypeError('type mismatch found, obj1: {obj1}, obj2: {obj2}')

    if isinstance(obj1, dict):
        only_in_obj1 = set(obj1).difference(obj2)
        if len(only_in_obj1) > 0:
            raise IndexError(f'at path {curpath}: only obj1 contains {only_in_obj1}') 
        only_in_obj2 = set(obj2).difference(obj1)
        if len(only_in_obj2) > 0:
            raise IndexError(f'at path {curpath}: only obj2 contains {only_in_obj2}')

        for key in obj1:
            compare_objects(obj1[key], obj2[key], '.'.join((curpath, str(key))), atol=atol, rtol=rtol)

    else:
        if isinstance(obj1, str):
            if obj1 != obj2:
                raise ValueError(f'at path {curpath}: strings differ ({obj1} != {obj2})')

        elif hasattr(obj1, '__iter__'):
            len_obj1 = len(tuple(obj1))
            len_obj2 = len(tuple(obj2))
            if len_obj1 != len_obj2:
                raise ValueError(f'Length mismatch at {curpath} ({len_obj1} vs {len_obj2})')

            for i, (subel1, subel2) in enumerate(zip(obj1, obj2)):
                compare_objects(subel1, subel2, f'{curpath}[{str(i)}]', atol=atol, rtol=rtol)  
        else:
            if not smart_is_equal(obj1, obj2, atol=atol, rtol=rtol):
                raise ValueError(f'Value mismatch at {curpath} ({obj1} vs {obj2})') 