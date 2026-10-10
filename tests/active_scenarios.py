# Runtime review/disable tests using only buttons on this exact ROM's checkpoint.
m.load(out/'coverage.state')
runtime=[0,3,8,9,10,11,12,13,14,15,16]
def active_ids():
    # Native row ABI: 4-byte label pointer, three u16 fields, padded to 12 bytes.
    ptr=m.symbols['sActiveRows']
    return [m.read(ptr+i*12+4,2) for i in range(m.read('sActiveCount',1))]
def bulk_off():
    open_menu();m.tap(SELECT);m.tap(START)
    if any(setting(i)!=(1 if i==13 else 0) for i in runtime):m.tap(A)
    close_menu()
bulk_off()
open_menu();m.tap(SELECT)
check(m.read('sModPage',1)==9 and active_ids()==[], 'Active review opens empty and excludes default EXP 1x and editor settings')
snap('active-empty');m.tap(START)
check(m.read('sConfirm',2)==43, 'Disable all with no active mods does not request confirmation')
m.tap(B);check(m.read('sModPage',1)==0, 'Back from active review returns to Main rather than the party editor')
close_menu()
for p,row,id in [(0,0,0),(0,3,3),(1,5,8),(1,6,9),(2,0,10),(2,1,11),(2,2,12),(2,4,14),(3,2,15),(3,3,16)]:
    toggle(p,row,id,1)
open_menu();page(2);number(3,13,4);close_menu()
open_menu();page(0);number(1,1,25);number(2,2,7);number(4,4,2);number(5,5,32);close_menu()
open_menu();page(1);number(1,7,3);close_menu()
open_menu();page(3);number(4,17,1);number(8,18,64);close_menu()
open_menu();page(4);select(6);m.tap(RIGHT);m.tap(B)
nonruntime={i:setting(i) for i in range(43) if i not in runtime}
party=m.bytes(m.symbols['gPlayerParty'],600);bag=bag_count(13);stock=m.bytes(m.symbols['sStock'],18)
snap('active-main');select(5);m.tap(A)
check(active_ids()==runtime, 'Active review lists all 11 distinct runtime effects exactly once, including shared money and shiny toggles')
check(m.read('sActiveCount',1)==11, 'Active count includes nondefault EXP without counting wild parameters or party drafts')
snap('active-all')
# Cross the seven-row page boundary, then remove the last two effects safely.
select(10);snap('active-second-page');m.tap(LEFT);m.tap(RIGHT);m.tap(L);m.tap(R)
check(active_ids()==runtime, 'Review left/right and shoulder inputs cannot accidentally enable, alter or disable effects')
m.tap(A)
check(setting(16)==0 and active_ids()==runtime[:-1], 'A disables only highlighted fast walking and removes its row')
check(m.read('sModCursor',2)<=m.read('sActiveCount',1)+1, 'Removing the final effect clamps cursor within the review actions')
select(9);m.tap(A)
check(setting(15)==0 and active_ids()==runtime[:-2], 'Individual wall disable needs no enable-risk confirmation')
select(7);m.tap(A)
check(setting(13)==1 and 13 not in active_ids(), 'Individual EXP disable restores neutral 1x rather than zero')
check(all(setting(i)==1 for i in [0,3,8,9,10,11,12,14]), 'Individual disables preserve every unrelated enabled effect')
m.tap(START);check(m.read('sConfirm',2)!=43, 'Bulk disable asks for confirmation when effects are enabled')
m.tap(B)
check(active_ids()==[i for i in runtime if i not in [13,15,16]], 'Cancelling bulk disable preserves all effects')
m.tap(START);m.tap(A)
check(active_ids()==[] and all(setting(i)==(1 if i==13 else 0) for i in runtime), 'Confirmed bulk disable clears every effect and restores EXP 1x')
check({i:setting(i) for i in nonruntime}==nonruntime, 'Bulk disable preserves all selected parameters and unapplied party draft fields')
check(m.bytes(m.symbols['gPlayerParty'],600)==party and bag_count(13)==bag, 'Bulk disable preserves actual Pokemon and already granted bag items')
check(m.bytes(m.symbols['sStock'],18)==stock, 'Bulk disable preserves custom shop stock')
check(m.read('gModMenuOpen',1)==1 and m.read('sModCursor',2)==0, 'Bulk disable leaves the review open at a valid empty-state cursor')
snap('active-disabled');m.tap(B)
check(m.read('sModPage',1)==0 and m.read('sModCursor',2)==5, 'Returning to Main restores the Active mods row selection')
close_menu();open_menu();m.tap(SELECT)
check(active_ids()==[], 'Reopening the native menu preserves disabled session state')
close_menu()
# Exercise repeated list shrinkage down to zero, with no confirmation or stale rows.
for p,row,id in [(1,5,8),(2,3,13)]:
    if id==13:
        open_menu();page(p);number(row,id,2);close_menu()
    else:toggle(p,row,id,1)
open_menu();m.tap(SELECT);m.tap(A)
check(active_ids()==[13] and setting(8)==0, 'Disabling the first of two effects retains the next effect and correct cursor')
m.tap(A)
check(active_ids()==[] and setting(13)==1, 'Disabling the last effect produces the empty state without stale rows')
m.tap(A);check(m.read('sConfirm',2)==43, 'Empty-state Disable all row remains safe after repeated removal')
close_menu();before=position();m.frames(LEFT,32);m.frames(0,30)
check(m.callback()=='CB2_Overworld' and position()!=before, 'Normal gameplay remains responsive after review and disable operations')
