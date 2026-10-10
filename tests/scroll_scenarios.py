# Full cycles use only controller input; expected choices come from native data.
m.load(out/'coverage.state')
valid_items=[i for i in range(1,375) if m.read(m.symbols['gItems']+i*44+14,2)==i and m.read(m.symbols['gItems']+i*44+26,1)]
held_items=[0]+[i for i in valid_items if m.read(m.symbols['gItems']+i*44+26,1)!=2 and not 121<=i<=132]
def first_choice(row):
    select(row);m.tap(A)
    for _ in range(400):
        if m.read('sBrowseIndex',2)==0:break
        m.tap(UP,wait=8)
    else:raise AssertionError('Cannot reach first browser choice')
    m.tap(A)
def cycle_choices(row,index,choices,name):
    first_choice(row)
    check(setting(index)==choices[0],name+' browser commits first valid choice')
    for key,direction in [(RIGHT,1),(LEFT,-1)]:
        start=choices.index(setting(index))
        for step in range(1,len(choices)+1):
            m.tap(key,wait=8)
            assert setting(index)==choices[(start+step*direction)%len(choices)],str((name,step,direction,setting(index),choices[(start+step*direction)%len(choices)]))
            assert m.read('sBrowser',1)==43,name+' unexpectedly opened browser'
        check(True,name+(' full Right cycle skips invalid choices and wraps' if direction==1 else ' full Left cycle skips invalid choices and wraps'))
    m.tap(R);check(setting(index)==choices[min(10,len(choices)-1)],name+' R advances ten valid choices')
    m.tap(L);check(setting(index)==choices[0],name+' L returns ten valid choices')
    m.tap(L);check(setting(index)==choices[0],name+' L clamps at first valid choice')
    m.tap(LEFT);m.tap(R)
    check(setting(index)==choices[-1] and m.read('sBrowser',1)==43,name+' R clamps at last valid choice without opening browser')
open_menu();page(1);cycle_choices(0,6,valid_items,'Item selector');close_menu()
open_menu();page(0);cycle_choices(1,1,list(range(1,387)),'Wild species selector');close_menu()
open_menu();page(4);cycle_choices(1,20,list(range(1,387)),'Party species selector')
cycle_choices(7,26,held_items,'Held-item selector');select(10);m.tap(A)
for slot in range(4):cycle_choices(slot,39+slot,list(range(355)),'Move slot '+str(slot+1))
close_menu()
# Browsing party drafts must not apply them; restore the controller-created state.
m.load(out/'coverage.state')
