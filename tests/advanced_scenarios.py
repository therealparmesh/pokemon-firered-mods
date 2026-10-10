# Executed in the input-driven acceptance harness namespace.
def number(row, setting_id, desired):
    select(row)
    for _ in range(150):
        current=setting(setting_id)
        if current==desired:return
        diff=desired-current
        m.tap((R if diff>0 else L) if abs(diff)>=10 else (RIGHT if diff>0 else LEFT))
    raise AssertionError('Numeric setting did not converge')
def browser(row, desired):
    select(row);m.tap(A)
    for _ in range(400):
        idx=m.read('sBrowseIndex',2);count=m.read('sBrowseCount',2);ptr=m.read('sBrowseIds')
        ids=[m.read(ptr+i*2,2) for i in range(count)]
        target=ids.index(desired)
        if idx==target:m.tap(A);return
        diff=target-idx
        m.tap((R if diff>0 else L) if abs(diff)>=10 else (DOWN if diff>0 else UP))
    raise AssertionError('Browser did not converge')
def toggle(page_row,row,id,value):
    open_menu();page(page_row);select(row)
    if setting(id)!=value:
        m.tap(A)
        if m.read('sConfirm',2)!=43:m.tap(A)
    close_menu()
def walk_to(x,y,order=(0,1)):
    for axis in order:
        target=(x,y)[axis]
        for _ in range(500):
            pos=struct.unpack('<hh',position())
            if pos[axis]==target:break
            m.frames((RIGHT if target>pos[axis] else LEFT) if axis==0 else (DOWN if target>pos[axis] else UP),1)
        else:raise AssertionError('Cannot walk to '+str((x,y))+' from '+str(pos))
        m.frames(0,30)
def flag(id):return bool(m.read(m.read('gSaveBlock1Ptr')+0xEE0+id//8,1)&(1<<(id%8)))
def location():return m.bytes(m.read('gSaveBlock1Ptr')+4,2)
def dismiss(n=30):
    for _ in range(n):m.tap(A,wait=30)
def wait_command():
    for _ in range(400):
        if m.read('gBattlerControllerFuncs')&~1 in m.all_symbols['HandleInputChooseAction']:return
        m.tap(A,wait=20)
    check(False,'Battle reaches command selection')
def move(slot):
    m.tap(A);m.tap(UP);m.tap(LEFT)
    if slot&1:m.tap(RIGHT)
    if slot&2:m.tap(DOWN)
    m.tap(A)
def finish_battle():
    for _ in range(300):
        if m.callback()=='CB2_Overworld':m.frames(0,120);return
        if m.callback()=='CB2_UpdatePartyMenu':
            tasks=m.tasks()
            if 'Task_HandleChooseMonInput' in tasks and m.read(m.symbols['gPartyMenu']+11,1)!=1:
                m.tap(B,wait=60) # Decline optional Shift-style switching.
            elif 'Task_HandleChooseMonInput' in tasks:
                for _ in range(12):
                    slot=m.read(m.symbols['gPartyMenu']+9,1)
                    if slot<m.read('gPlayerPartyCount',1) and slot!=m.read('gBattlerPartyIndexes',1) and pokemon(m.symbols['gPlayerParty']+slot*100)['hp']:
                        m.tap(A);m.tap(A);break
                    m.tap(DOWN);m.tap(RIGHT)
            elif 'Task_HandleSelectionMenuInput' in tasks:m.tap(A)
            else:m.tap(B,wait=30)
        else:m.tap(A,wait=30)
    check(False,'Battle returns to overworld')
def configure_party(moves,species=None,level=80):
    open_menu();page(4)
    if species:number(1,20,species)
    number(2,21,level)
    select(10);m.tap(A)
    for i,v in enumerate(moves):browser(i,v)
    m.tap(B);select(11);m.tap(A);m.tap(A,wait=80);close_menu()
    open_menu();page(3);select(0);m.tap(A);close_menu()
def start_battle(species=1,level=5):
    open_menu();page(0);select(0)
    if not setting(0):m.tap(A)
    number(1,1,species);number(2,2,level)
    select(7);m.tap(A,wait=500);wait_command()

def stat(id):return m.read(m.read('gSaveBlock1Ptr')+0x1200+id*4)^m.read(m.read('gSaveBlock2Ptr')+0xF20)

# Confirm world actions refuse missing progression and can be cancelled.
old=location();open_menu();page(3);select(5);m.tap(A);m.tap(A)
check(location()==old and m.read('gModMenuOpen',1),'Teleport refuses missing starter progression')
select(6);m.tap(A);m.tap(A)
check(not flag(0x829),'Dex completion refuses missing Pokedex progression')
close_menu()
# Reach the ordinary Oak starter sequence through the game's real coordinate script.
toggle(3,2,15,1) # confirmation required
if not setting(15):
    open_menu();page(3);select(2);m.tap(A);m.tap(A);close_menu()
walk_to(17,9);m.frames(LEFT,60);m.frames(0,600)

walk_to(11,14);m.frames(DOWN,128);m.frames(0,600)

walk_to(19,8);dismiss(120)
snap('oak-introduction')
m.save(out/'story-lab.state')
check(location()==bytes([4,3]),'Native house/stair/door warps and Oak introduction complete with walls enabled')
m.frames(RIGHT,128);m.frames(0,80);blocked=position();m.frames(RIGHT,64);m.frames(0,30)
check(position()==blocked,'Walls preserve the native Oak lab Pokeball object collision')
walk_to(15,12,(1,0));m.tap(UP);m.tap(A)
for _ in range(100):
    if flag(0x828):break
    m.tap(A,wait=30)
check(flag(0x828),'Native starter selection earns teleport prerequisite')
for _ in range(120):
    if m.callback()=='CB2_NamingScreen':m.tap(START,wait=30);m.tap(A,wait=80)
    else:m.tap(A,wait=30)
m.save(out/'starter.state')
snap('starter-earned')
walk_to(13,14);m.frames(DOWN,32);m.frames(0,120)
wait_command();move(0);finish_battle()
for _ in range(80):m.tap(B,wait=30)
check(flag(0x258),'Native first rival trainer battle completes during story progression')
toggle(3,2,15,0)
m.save(out/'world-base.state')
import re
map_ids={name:int(num)|(int(group)<<8) for name,num,group in re.findall(r'#define\s+(MAP_\w+)\s+\((\d+) \| \((\d+) << 8\)\)',(ROOT/'include/constants/map_groups.h').read_text())}
heals=json.loads((ROOT/'src/data/heal_locations.json').read_text())['heal_locations']
def teleport(id):
    open_menu();page(3);number(4,17,id);select(5);m.tap(A);m.tap(A,wait=400)
    m.frames(0,180)
for id,heal in enumerate(heals,1):
    teleport(id)
    expected=map_ids[heal['map']]
    check(location()==bytes([expected>>8,expected&255]) and struct.unpack('<hh',position())==(heal['x']+7,heal['y']+7),'Teleport arrives at '+heal['id'])
    if id==17:dismiss(100);m.frames(0,120) # Native Four Island rival greeting.
    open_menu();close_menu()
    before=position();m.frames(DOWN,20);m.frames(0,30)
    check(position()!=before,'Controls restored after teleport '+str(id))
    snap('teleport-'+str(id))
# Last heal uses the actual native destination, including indoor healer coordinates.
last_heal=m.bytes(m.read('gSaveBlock1Ptr')+0x1C,8)
teleport(0)
check(location()==last_heal[:2], 'Last-heal teleport uses the stored native map destination')
check(m.callback()=='CB2_Overworld','Last-heal teleport returns to the field')
open_menu();close_menu()
# Native story flag editing is temporary for this test and restored afterwards.
old_flag=flag(32);open_menu();page(3);number(8,18,32)
select(9);m.tap(A);m.tap(B)
check(flag(32)==old_flag,'Story flag confirmation cancellation preserves the flag')
m.tap(A);m.tap(A);check(flag(32),'World flag set updates native save flag')
select(10);m.tap(A);m.tap(A);check(not flag(32),'World flag clear updates native save flag')
if old_flag:select(9);m.tap(A);m.tap(A)
close_menu()
m.save(out/'world-tested.state')
# Earn the Pokedex via the native Parcel scene, then exercise seen/caught completion.
m.load(out/'world-base.state');teleport(2);toggle(3,2,15,1)
walk_to(43,27);toggle(3,2,15,0);m.frames(UP,32);m.frames(0,400)
for _ in range(140):
    if bag_count(349):break
    m.tap(A,wait=30)
for _ in range(60):m.tap(B,wait=30)
m.frames(0,120)

snap('parcel-clerk')
check(bag_count(349)==1,'Viridian clerk gives Oak parcel through the native story script')
teleport(1)

toggle(3,2,15,1)
walk_to(23,21,(1,0))

toggle(3,2,15,0);m.frames(UP,32);m.frames(0,400)
toggle(3,2,15,1);walk_to(13,11,(1,0));m.tap(UP);m.tap(A);dismiss(180)
for _ in range(40):m.tap(B,wait=30)
check(flag(0x829) and bag_count(349)==0,'Oak accepts parcel and grants the native Pokedex')
toggle(3,2,15,0)
open_menu();page(3);select(6);m.tap(A);m.tap(A)
sb2=m.read('gSaveBlock2Ptr');sb1=m.read('gSaveBlock1Ptr')
def dex_complete(address):
    flags=m.bytes(address,49)
    return all(flags[(id-1)//8] & (1<<((id-1)%8)) for id in range(1,387))
check(dex_complete(sb2+0x5C) and dex_complete(sb1+0x5F8) and dex_complete(sb1+0x3A18),'Seen-all completes all 386 entries and both native mirrors')
select(7);m.tap(A);m.tap(A)
check(dex_complete(sb2+0x28),'Caught-all completes all 386 native owned flags')
close_menu();snap('dex-complete');m.save(out/'dex-tested.state')
# Each battle branch starts from a checkpoint created above through real controls.
# Self-KO and recoil must protect only when enabled, and preserve native results when OFF.
for effect,attack in [('Self-Destruct',120),('Double-Edge recoil',38)]:
    for enabled in (1,0):
        m.load(out/'world-base.state')
        configure_party([attack,45,105,164]);toggle(2,0,10,enabled)
        initial=pokemon(m.symbols['gPlayerParty'])['hp']
        start_battle();move(0);finish_battle()
        final=pokemon(m.symbols['gPlayerParty'])['hp']
        check((final==initial if enabled else final<initial),effect+(' preserves HP with protection ON' if enabled else ' applies native HP cost with protection OFF'))
        check(m.read('gBattleOutcome',1)==1,'Normal victory completes after '+effect+' '+str(enabled))
# Substitute and Perish Song execute real native battle scripts, not injected damage.
m.load(out/'world-base.state');configure_party([164,195,45,105]);toggle(2,0,10,1)
start_battle();initial=m.read(m.symbols['gBattleMons']+0x28,2)
move(0);wait_command()
check(m.read(m.symbols['gBattleMons']+0x28,2)==initial,'Substitute HP cost respects HP protection')
# Substitute HP is the byte at offset 0x0A of the native DisableStruct.
check(m.read(m.symbols['gDisableStructs']+0xA,1)>0,'Substitute is created without hanging the battle')
move(1);wait_command()
for _ in range(4):
    move(2)
    for _ in range(300):
        if m.callback()=='CB2_Overworld':break
        if m.read('gBattlerControllerFuncs')&~1 in m.all_symbols['HandleInputChooseAction']:break
        m.tap(A,wait=20)
    if m.callback()=='CB2_Overworld':break
finish_battle()
check(pokemon(m.symbols['gPlayerParty'])['hp']==initial and m.read('gBattleOutcome',1)==1,'Perish Song defeats enemy while protected player survives')
# Pressure's separate Imprison/Perish Song loss paths and ordinary deduction.
for enabled in (1,0):
    m.load(out/'world-base.state');configure_party([286,195,43,105]);toggle(2,0,10,1);toggle(2,1,11,enabled)
    start_battle(356,5) # Dusclops: native Pressure ability, Leer shared for Imprison.
    before=m.bytes(m.symbols['gBattleMons']+0x24,4)
    move(0);wait_command()
    after=m.bytes(m.symbols['gBattleMons']+0x24,4)
    check(after[0]==before[0] if enabled else before[0]-after[0]>=2,'Pressure Imprison PP protection '+str(enabled))
    move(1);wait_command()
    after=m.bytes(m.symbols['gBattleMons']+0x24,4)
    check(after[1]==before[1] if enabled else before[1]-after[1]>=2,'Pressure Perish Song PP protection '+str(enabled))
# Spite and Grudge must preserve PP with the toggle ON and consume it with OFF.
for enabled in (1,0):
    m.load(out/'world-base.state');configure_party([45,247,105,164]);toggle(2,0,10,1);toggle(2,1,11,enabled)
    start_battle(92,12) # Gastly: Hypnosis, Lick, Spite; Lick cannot hit normal Fearow.
    exercised=False
    for _ in range(40):
        before=m.read(m.symbols['gBattleMons']+0x24,1)
        move(0);wait_command()
        if m.read(m.symbols['gLastMoves']+2,2)==180 and m.read('gLastMoves',2)==45:
            after=m.read(m.symbols['gBattleMons']+0x24,1)
            if enabled or before-after>1:
                exercised=True;break
    check(exercised and (after==before if enabled else before-after>1),'Enemy Spite PP protection '+str(enabled))
for enabled in (1,0):
    m.load(out/'world-base.state');configure_party([45,247,105,164]);toggle(2,0,10,1);toggle(2,1,11,enabled)
    start_battle(353,56)
    for _ in range(40):
        move(0);wait_command()
        if m.read(m.symbols['gStatuses3']+4)&(1<<14):break
    check(bool(m.read(m.symbols['gStatuses3']+4)&(1<<14)),'Enemy activates real Grudge '+str(enabled))
    before=m.read(m.symbols['gBattleMons']+0x25,1)
    m.save(out/'grudge-ready.state')
    for delay in range(12):
        if delay:
            m.load(out/'grudge-ready.state')
            move(0);wait_command()
            for _ in range(40):
                move(0);wait_command()
                if m.read(m.symbols['gStatuses3']+4)&(1<<14):break
            m.save(out/'grudge-ready.state')
        move(1)
        # Observe real Grudge still active at the instant enemy HP reaches zero.
        # Snatch can act first and clear it; that is not a Grudge test.
        for _ in range(3000):
            if m.read(m.symbols['gBattleMons']+0x58+0x28,2)==0:break
            m.frames(0,1)
        live_grudge=bool(m.read(m.symbols['gStatuses3']+4)&(1<<14))
        finish_battle()
        after=pokemon(m.symbols['gPlayerParty'])['pp'][1]
        if live_grudge and (after==before if enabled else after==0):break
    check(live_grudge and (after==before if enabled else after==0),'Enemy Grudge PP protection '+str(enabled))
# World integration: real grass encounters, ledges and post-battle healing.
m.load(out/'dex-tested.state');teleport(1);toggle(2,4,14,1);toggle(3,2,15,1)
walk_to(19,7);m.frames(UP,128);m.frames(0,120)
check(location()==bytes([map_ids['MAP_ROUTE1']>>8,map_ids['MAP_ROUTE1']&255]),'Map connection to Route 1 remains usable with walls enabled')
walk_to(19,43);toggle(3,2,15,0)
oid=m.read(m.symbols['gPlayerAvatar']+5,1)
check(m.read(m.symbols['gObjectEvents']+oid*36+30,1)==2,'Encounter test stands on real Route 1 tall grass')
grass_steps=stat(5)
for _ in range(50):
    m.frames(RIGHT,16);m.frames(0,20);m.frames(LEFT,16);m.frames(0,20)
check(m.callback()=='CB2_Overworld' and stat(5)-grass_steps>=100,'No-encounters suppresses 100 actual grass steps')
toggle(2,4,14,0)
for _ in range(150):
    m.frames(RIGHT if _%2==0 else LEFT,16);m.frames(0,20)
    if m.callback()!='CB2_Overworld' or 'Task_BattleStart' in m.tasks():break
wait_command()
check(pokemon(m.symbols['gEnemyParty'])['species'] in (16,19),'Disabling no-encounters restores original Route 1 species selection')
m.tap(DOWN);m.tap(RIGHT);m.tap(A,wait=500);finish_battle()
check(m.callback()=='CB2_Overworld','Ordinary grass encounter ends in playable field')
m.save(out/'route-field.state')
toggle(2,4,14,1);toggle(3,2,15,1);walk_to(19,37)
before=stat(43);m.frames(DOWN,20);m.frames(0,80)
check(stat(43)==before+1 and struct.unpack('<hh',position())==(19,39),'Walls preserve native two-tile ledge jumps and jump statistic')
m.load(out/'world-base.state');configure_party([105,45,247,164]);toggle(2,0,10,1)
start_battle(12,15) # Butterfree knows the three powders and Confusion.
for _ in range(30):
    move(0);wait_command()
    if m.read(m.symbols['gBattleMons']+0x4C):break
check(bool(m.read(m.symbols['gBattleMons']+0x4C)),'Enemy powder inflicts a real status despite HP protection')
m.tap(DOWN);m.tap(RIGHT);m.tap(A,wait=500);finish_battle()
check(bool(pokemon(m.symbols['gPlayerParty'])['status']),'Real battle status persists in the party after escape')
open_menu();page(3);select(0);m.tap(A);close_menu()
check(all(pokemon(m.symbols['gPlayerParty']+i*100)['status']==0 for i in range(m.read('gPlayerPartyCount',1))),'World heal clears actual battle status for the whole party')
# Destiny Bond must also honor the HP toggle without suppressing native KO when OFF.
for enabled in (1,0):
    m.load(out/'world-base.state');configure_party([105,247,45,164],235,100);toggle(2,0,10,enabled);toggle(2,1,11,1)
    start_battle(94,39)
    for _ in range(40):
        move(0);wait_command()
        if m.read(m.symbols['gBattleMons']+0x58+0x50)&(1<<25):break
    check(bool(m.read(m.symbols['gBattleMons']+0x58+0x50)&(1<<25)),'Enemy activates real Destiny Bond '+str(enabled))
    # Level 100 guarantees the selected hit can KO this level-39 opponent.
    # Observe Bond at the actual KO, not only at the preceding command menu.
    move(1)
    for _ in range(3000):
        if m.read(m.symbols['gBattleMons']+0x58+0x28,2)==0:break
        m.frames(0,1)
    check(m.read(m.symbols['gBattleMons']+0x58+0x28,2)==0 and bool(m.read(m.symbols['gBattleMons']+0x58+0x50)&(1<<25)), 'Destiny Bond remains live at the actual enemy KO '+str(enabled))
    finish_battle()
    hp=pokemon(m.symbols['gPlayerParty'])['hp']
    check(hp>0 if enabled else hp==0,'Destiny Bond HP protection '+str(enabled))
# With protection disabled, the same native Perish Song timer must cause a KO.
m.load(out/'world-base.state');configure_party([195,45,105,164]);toggle(2,0,10,0)
start_battle();move(0);wait_command()
for _ in range(4):
    move(1)
    for _ in range(300):
        if m.callback()=='CB2_Overworld':break
        if m.read('gBattlerControllerFuncs')&~1 in m.all_symbols['HandleInputChooseAction']:break
        m.tap(A,wait=20)
    if m.callback()=='CB2_Overworld':break
finish_battle()
check(pokemon(m.symbols['gPlayerParty'])['hp']==0,'Perish Song applies native player KO with protection OFF')
check(m.callback()=='CB2_Overworld' and m.read('gBattleOutcome',1)==1,'Perish Song simultaneous KO returns to normal victory with remaining party')
exec((ROOT/'tests/surf_scenarios.py').read_text())

exec((ROOT/'tests/browser_scenarios.py').read_text())
exec((ROOT/'tests/active_scenarios.py').read_text())
exec((ROOT/'tests/control_scenarios.py').read_text())

# Leave the final test branch with all modifiers disabled and responsive field controls.
open_menu();select(5);m.tap(A);m.tap(START);m.tap(A);close_menu()
check(not any(setting(i) for i in [0,3,8,9,10,11,12,14,15,16]),'Extended battle/world tests end with all runtime modifiers disabled')
open_menu();close_menu()
