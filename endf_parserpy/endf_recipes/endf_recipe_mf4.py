ENDF_RECIPE_MF4 = """

[MAT, 4, MT/ ZA, AWR, 0, LTT, 0, 0]HEAD
[MAT, 4, MT/ 0.0, AWR, LI, LCT, 0, 0]CONT

# Legendre coefficients
if LTT == 1 and LI == 0:
    [MAT, 4, MT/ 0.0, 0.0, 0, 0, NR, NE/ Eint ]TAB2
    for i=1 to NE:
        [MAT, 4, MT/ T, E[i] , LT, 0, NL[i], 0/ {a[i,l]}{l=1 to NL[i]} ]LIST
    endfor
endif

# Angular distributions over two energy ranges.
if LTT==3 and LI==0:
    # lower range given by Legendre coefficients
    [MAT, 4, MT/ 0.0, 0.0, 0, 0, NR, NE1/ Eint ]TAB2 (leg_int)
    for i=1 to NE1:
        [MAT, 4, MT/ T, E[i], LT, 0, NL[i], 0/
                     {al[i,j]}{j=1 to NL[i]} ]LIST
    endfor
    # higher range represented by probability distribution
    [MAT, 4, MT/ 0.0, 0.0, 0, 0, NR, NE2/ Eint ]TAB2 (ang_int)
    for i=NE1 to NE1+NE2-1:
        [MAT, 4, MT/ T,  E[i] , LT, 0, NR, NP/ mu / f ]TAB1 (angtable[i])
    endfor
endif
SEND
"""