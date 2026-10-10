#!/usr/bin/env python3
"""Boot and in-game regression tests driven solely by emulated GBA buttons.
Memory is read only for assertions; no saves, callbacks, flags or mods injected.
"""
import hashlib, json, pathlib, signal, struct, sys, zlib
signal.alarm(300)
from emulator import Emulator, ROOT
A,B,SELECT,START,RIGHT,LEFT,UP,DOWN,R,L=1,2,4,8,16,32,64,128,256,512
rom,elf,variant=sys.argv[1:]
out=ROOT/'tests/output'/variant
out.mkdir(parents=True,exist_ok=True)
(out/'results.json').unlink(missing_ok=True)
m=Emulator(rom,elf)
passed=[]
def check(ok,name):
    if not ok:
        snap('failure');m.save(out/'failure.state')
    assert ok,name
    passed.append(name);print('PASS:',name,flush=True)
def snap(name):
    ppm=out/(name+'.ppm');m.screenshot(ppm)
    b=ppm.read_bytes().split(b'\n',3)[3]
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))
    scan=b''.join(b'\0'+b[y*720:(y+1)*720] for y in range(160))
    (out/(name+'.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',240,160,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b''))
def position():
    oid=m.read(m.symbols['gPlayerAvatar']+5,1)
    return m.bytes(m.symbols['gObjectEvents']+oid*0x24+0x10,4)
def setting(index):return m.read(m.symbols['gMods']+index*2,2)
def select(row):
    for _ in range(32):
        cursor=m.read('sModCursor',2)
        if cursor==row:return
        m.tap(DOWN)
    raise AssertionError('Menu cursor cannot reach row '+str(row))
def start_action(action, wait=40):
    m.tap(START,wait=60)
    assert 'Task_StartMenuHandleInput' in m.tasks(), 'Native Start menu did not open'
    for _ in range(12):
        cursor=m.read('sStartMenuCursorPos',1)
        if m.read(m.symbols['sStartMenuOrder']+cursor,1)==action:break
        m.tap(DOWN)
    else:raise AssertionError('Native Start menu is missing action '+str(action))
    m.tap(A,wait=wait)
def open_menu():
    start_action(9)
    assert m.read('gModMenuOpen',1)==1,'Start > Mods did not open menu'
def page(row):
    select(row);m.tap(A)
def close_menu():
    for _ in range(6):
        if not m.read('gModMenuOpen',1):return
        m.tap(B)
    raise AssertionError('Menu did not close')
def bag_count(item):
    sb=m.read('gSaveBlock1Ptr'); key=m.read(m.read('gSaveBlock2Ptr')+0xF20)&65535
    total=0
    for offset,count in [(0x310,42),(0x3B8,30),(0x430,13),(0x464,58),(0x54C,43)]:
        for i in range(count):
            slot=m.read(sb+offset+i*4)
            if slot&65535==item:total+=((slot>>16)^key)
    return total
ORDERS=[(0,1,2,3),(0,1,3,2),(0,2,1,3),(0,3,1,2),(0,2,3,1),(0,3,2,1),(1,0,2,3),(1,0,3,2),(2,0,1,3),(3,0,1,2),(2,0,3,1),(3,0,2,1),(1,2,0,3),(1,3,0,2),(2,1,0,3),(3,1,0,2),(2,3,0,1),(3,2,0,1),(1,2,3,0),(1,3,2,0),(2,1,3,0),(3,1,2,0),(2,3,1,0),(3,2,1,0)]
def pokemon(address):
    b=m.bytes(address,100);pid,ot=struct.unpack_from('<II',b)
    data=b''.join(struct.pack('<I',word^pid^ot) for word in struct.unpack_from('<12I',b,32))
    assert sum(struct.unpack('<24H',data))&65535==struct.unpack_from('<H',b,28)[0],'Pokemon checksum failed'
    assert not b[19]&1,'Bad egg flag set'
    blocks=[data[i*12:(i+1)*12] for i in ORDERS[pid%24]]
    ivword=struct.unpack_from('<I',blocks[3],4)[0]
    return {'pid':pid,'ot':ot,'species':struct.unpack_from('<H',blocks[0])[0],'exp':struct.unpack_from('<I',blocks[0],4)[0],'level':b[84], 'hp':struct.unpack_from('<H',b,86)[0], 'ivs':[(ivword>>(i*5))&31 for i in range(6)],'evs':list(blocks[2][:6]),'moves':list(struct.unpack_from('<4H',blocks[1])),'pp':list(blocks[1][8:12]),'pp_bonuses':blocks[0][8],'held_item':struct.unpack_from('<H',blocks[0],2)[0],'ability':ivword>>31,'status':struct.unpack_from('<I',b,80)[0],'max_hp':struct.unpack_from('<H',b,88)[0],'shiny':((ot>>16)^(ot&65535)^(pid>>16)^(pid&65535))<8}
try:
    for _ in range(35):
        m.frames(0,60)
        if m.callback()=='CB2_TitleScreenRun':break
    check(m.callback()=='CB2_TitleScreenRun','Boot reaches title screen')
    m.frames(0,720);snap('title')
    m.tap(START,wait=180)
    for _ in range(240):
        if m.callback()=='CB2_Overworld':break
        if m.callback()=='CB2_NamingScreen':m.tap(START,wait=30);m.tap(A,wait=80)
        else:m.tap(A,count=20,wait=30)
    m.frames(0,120)
    check(m.callback()=='CB2_Overworld','New game reaches normal overworld')
    snap('gameplay')
    before=position();m.frames(LEFT,32);m.frames(0,30)
    check(position()!=before,'Normal field movement works')
    m.frames(RIGHT,32);m.frames(0,30)
    open_menu();check(m.read('gModMenuOpen',1)==1,'Start > Mods opens native menu with sequential buttons');check(m.read('sModPage',1)==0,'Start-menu selection lands on Main without reusing A');snap('menu')
    close_menu();check(m.read('gModMenuOpen',1)==0,'B closes native menu')
    old=bag_count(13)
    open_menu();page(1);select(2);m.tap(A)
    check(bag_count(13)==old+1,'Item mod adds one Potion through bag API')
    snap('item-added');close_menu()
    open_menu();page(2);select(4);m.tap(A)
    check(setting(14)==1,'No encounters toggle enables')
    m.tap(A);check(setting(14)==0,'No encounters toggle disables')
    close_menu()
    before=position();m.frames(LEFT,32);m.frames(0,30)
    check(position()!=before and m.callback()=='CB2_Overworld','Gameplay remains responsive after disabling mod')
    m.frames(RIGHT,32);m.frames(0,30)
    # Validate wild settings via a native, explicit "Give selected Pokemon" action.
    open_menu();page(0);select(0);m.tap(A)
    select(1);m.tap(A);m.tap(RIGHT);m.tap(RIGHT);m.tap(DOWN);m.tap(A)
    check(setting(1)==22,'Named species browser and page navigation select Fearow')
    select(2);m.tap(RIGHT) # level 6
    select(3);m.tap(A) # shiny
    select(4);m.tap(RIGHT) # Hardy
    select(5);m.tap(R,wait=20);m.tap(R,wait=20);m.tap(R,wait=20);m.tap(R,wait=20) # IV 31
    select(6);m.tap(A);m.tap(A,wait=80)
    check(m.read('gPlayerPartyCount',1)==1,'Native give action creates a party Pokemon')
    mon=pokemon(m.symbols['gPlayerParty'])
    check(mon['species']==22 and mon['level']==6 and mon['shiny'] and mon['ivs']==[31]*6 and mon['pid']%25==0,'Species, level, shiny, nature and IV controls produce valid Pokemon')
    snap('wild-settings');close_menu()
    # Edit nature, level, EVs and a move; assert encrypted data independently.
    open_menu();page(4);select(2);m.tap(RIGHT);select(3);m.tap(RIGHT)
    select(9);m.tap(A);select(0);m.tap(R);m.tap(B)
    select(10);m.tap(A);select(0);m.tap(A);m.tap(DOWN);m.tap(A);m.tap(B)
    select(11);m.tap(A);m.tap(A,wait=180)
    mon=pokemon(m.symbols['gPlayerParty'])
    check(mon['level']==7 and mon['pid']%25==1 and mon['evs'][0]==10,'Party edits recalculate level/nature/EVs with valid checksum')
    check(mon['shiny'] and mon['ivs']==[31]*6 and all(0<=v<355 for v in mon['moves']),'Party edits preserve shiny state and valid IVs/moves')
    snap('party-edited');close_menu()
    # Native shop transaction, with explicit field-lock lifecycle.
    stored_money=m.read(m.read('gSaveBlock1Ptr')+0x290)
    old=bag_count(13)
    open_menu();page(1);select(6);m.tap(A);select(4);m.tap(A,wait=50)
    m.tap(A,wait=200)
    for _ in range(40):
        if bag_count(13)==old+1:break
        m.tap(A,count=10,wait=60)
    check(bag_count(13)==old+1 and m.read(m.read('gSaveBlock1Ptr')+0x290)==stored_money,'Native free shop purchase adds item without charging money')
    snap('shop-purchase')
    for _ in range(40):
        if 'Task_BuyMenu' in m.tasks():break
        m.tap(A,wait=30)
    m.tap(B,wait=250)
    for _ in range(40):
        if 'Task_ShopMenu' in m.tasks():break
        m.tap(A,wait=30)
    m.tap(B,wait=80)
    before=position();m.frames(LEFT,32);m.frames(0,30)
    check(position()!=before and m.callback()=='CB2_Overworld','Exiting native shop restores field controls')
    m.frames(RIGHT,32);m.frames(0,30)
    # A real generated wild battle, an actual damage move, and capture.
    open_menu();page(1);select(0);m.tap(A)
    for _ in range(9):m.tap(UP)
    m.tap(A);select(2);m.tap(A);close_menu()
    check(bag_count(4)==1,'Named item browser adds Poké Ball to correct pocket')
    open_menu();page(2)
    for row in range(3):select(row);m.tap(A)
    close_menu()
    open_menu();page(0);select(1);m.tap(A)
    for _ in range(21):m.tap(UP)
    m.tap(A);select(2);m.tap(LEFT);select(7);m.tap(A,wait=500)
    def wait_action():
        for _ in range(300):
            if m.read('gBattlerControllerFuncs')&~1 in m.all_symbols['HandleInputChooseAction']:return
            m.tap(A,wait=20)
        snap('battle-timeout');m.save(out/'battle-timeout.state')
        print('Battle diagnostic',m.callback(),hex(m.read('gBattlerControllerFuncs')&~1),hex(m.symbols['HandleInputChooseAction']),m.read('gBattleOutcome',1),setting(0),setting(1),m.tasks(),flush=True)
        raise AssertionError('Battle did not reach command selection')
    wait_action()
    battle_callback=m.callback();m.tap(START|SELECT,wait=40)
    check(not m.read('gModMenuOpen',1) and m.callback()==battle_callback, 'Start+Select cannot open Mods during a real battle')
    enemy=pokemon(m.symbols['gEnemyParty'])
    check(enemy['species']==1 and enemy['level']==5 and enemy['shiny'] and enemy['ivs']==[31]*6 and enemy['pid']%25==0,'Selected wild battle uses shiny/nature/IV/species/level settings')
    original_hp=m.read(m.symbols['gBattleMons']+0x28,2)
    original_pp=m.bytes(m.symbols['gBattleMons']+0x24,4)
    damage_turn=False
    for _ in range(12):
        m.tap(A);m.tap(RIGHT);m.tap(A);wait_action() # Growl, not a damaging move
        if m.read(m.symbols['gLastMoves']+2,2)==33:damage_turn=True;break # Enemy Tackle
    check(damage_turn and m.read(m.symbols['gBattleMons']+0x28,2)==original_hp,'Infinite HP prevents damage from an enemy Tackle')
    check(m.bytes(m.symbols['gBattleMons']+0x24,4)==original_pp,'Infinite PP preserves PP after executed moves')
    snap('battle')
    m.tap(RIGHT);m.tap(A,wait=200);m.tap(RIGHT,wait=80);m.tap(RIGHT,wait=80)
    snap('ball-pocket');m.tap(A,wait=80);m.tap(A,wait=600)
    for _ in range(150):
        if m.callback()=='CB2_Overworld':break
        if m.callback()=='CB2_NamingScreen':m.tap(START,wait=30);m.tap(A,wait=60)
        else:m.tap(B,wait=30);m.tap(A,wait=30)
    m.frames(0,120)
    check(m.callback()=='CB2_Overworld' and m.read('gBattleOutcome',1)==7 and m.read('gPlayerPartyCount',1)==2,'Guaranteed capture completes and returns to gameplay')
    caught=pokemon(m.symbols['gPlayerParty']+100)
    check(caught['species']==1 and caught['shiny'] and caught['level']==5,'Captured modified Pokemon retains valid checksum and properties')
    # Experience multiplier exercises the original victory/EXP flow.
    before_exp=pokemon(m.symbols['gPlayerParty'])['exp']
    open_menu();page(2);select(3);m.tap(RIGHT);m.tap(RIGHT);close_menu()
    open_menu();page(0);select(2)
    for _ in range(4):m.tap(LEFT)
    select(7);m.tap(A,wait=500);wait_action()
    m.tap(A);m.tap(LEFT);m.tap(A) # Drill Peck, first move
    for _ in range(240):
        if m.callback()=='CB2_Overworld':break
        m.tap(A,count=20,wait=30)
    m.frames(0,120)
    check(m.callback()=='CB2_Overworld' and m.read('gBattleOutcome',1)==1 and pokemon(m.symbols['gPlayerParty'])['exp']-before_exp==27,'EXP multiplier gives 3x the native level-1 Bulbasaur EXP')
    # Disable session mods and verify ordinary field input again.
    open_menu();select(5);m.tap(A);m.tap(START);m.tap(A);close_menu()
    check(not any(setting(i) for i in [0,3,8,9,10,11,12,14,15,16]),'Disable all clears every mod toggle')
    before=position();m.frames(LEFT,32);m.frames(0,30)
    check(position()!=before,'Normal gameplay continues after all mods are disabled')
    snap('after-disable')
    # Save through the native menu, power-cycle, and continue from flash.
    party_before=[pokemon(m.symbols['gPlayerParty']+i*100) for i in range(2)]
    items_before=bag_count(13)
    open_menu();page(2);select(4);m.tap(A);close_menu()
    start_action(4,wait=120)
    for _ in range(20):m.tap(A,count=20,wait=60)
    m.command('DUMP '+str(out/'generated.sav'))
    flash=(out/'generated.sav').read_bytes()
    footers=sum(struct.unpack_from('<I',flash,i*4096+4088)[0]==0x08012025 for i in range(len(flash)//4096))
    check(m.read('gSaveAttemptStatus',2)==1 and footers>=14,'Native saving writes a complete valid flash save slot')
    m.command('RESET')
    for _ in range(40):
        m.frames(0,60)
        if m.callback()=='CB2_TitleScreenRun':break
    m.frames(0,720);m.tap(START,wait=180)
    check(m.callback()=='CB2_MainMenu','Saved game exposes Continue after power-cycle')
    m.tap(A,wait=300)
    for _ in range(60):
        if m.callback()=='CB2_Overworld' and m.read('gQuestLogState',1) not in (2,3):break
        m.tap(B,wait=30)
    m.frames(0,120)
    check(m.callback()=='CB2_Overworld' and m.read('gPlayerPartyCount',1)==2 and [pokemon(m.symbols['gPlayerParty']+i*100) for i in range(2)]==party_before and bag_count(13)==items_before,'Save/reload preserves edited and captured Pokemon and bag items')
    check(setting(14)==0,'Mod settings reset on power-cycle and do not enter save data')
    snap('reloaded');m.save(out/'gameplay.state')
    open_menu()
    check(m.read('gModMenuOpen',1)==1,'Mods remains accessible from native Start after save/reload')
    close_menu()
    # Change the actual in-game option rather than writing its RAM field.
    start_action(5,wait=150)
    for _ in range(4):m.tap(DOWN)
    m.tap(RIGHT);m.tap(RIGHT);m.tap(B,wait=200);m.tap(B,wait=60)
    check(m.read(m.read('gSaveBlock2Ptr')+0x13,1)==2,'Native Options menu enables L=A button mode')
    open_menu();page(0);select(1);m.tap(A);m.tap(R);m.tap(L)
    check(m.read('sBrowser',1)==1 and m.read('sBrowseIndex',2)==0,'Mod browser L/R navigation works under L=A without confirming')
    close_menu();check(not m.read('gModMenuOpen',1),'Native menu closes correctly under L=A')
    # Audit regressions: party drafts must not mutate actual Pokemon until Apply.
    open_menu();page(4);select(0);m.tap(R)
    check(setting(19)==1,'Ten-step party jump stops at the last occupied slot')
    m.tap(LEFT);select(4);m.tap(A)
    check(setting(23)==0,'Single-ability species cannot select an invalid ability')
    select(9);m.tap(A)
    select(0)
    for _ in range(26):m.tap(R)
    select(1)
    for _ in range(26):m.tap(R)
    select(2);m.tap(R)
    snap('ev-over-limit');m.tap(B)
    before_mon=m.bytes(m.symbols['gPlayerParty'],100)
    select(11);m.tap(A);m.tap(A,wait=80)
    check(m.bytes(m.symbols['gPlayerParty'],100)==before_mon,'Over-budget EV edits are rejected without partial mutation')
    snap('invalid-party');select(9);m.tap(A);select(6);m.tap(A);m.tap(B)
    select(8);m.tap(A);select(6);m.tap(A);m.tap(B)
    select(11);m.tap(A);m.tap(A,wait=80)
    mon=pokemon(m.symbols['gPlayerParty'])
    check(mon['evs']==[0]*6 and mon['ivs']==[31]*6,'Clear EV and max IV presets apply valid stats')
    check(mon['exp']==party_before[0]['exp'] and mon['pid']==party_before[0]['pid'] and mon['pp']==party_before[0]['pp'] and mon['pp_bonuses']==party_before[0]['pp_bonuses'],'Unrelated party edits preserve earned EXP, personality and existing move PP')
    select(2);m.tap(RIGHT);close_menu()
    check(pokemon(m.symbols['gPlayerParty'])==mon,'Closing party editor discards unapplied drafts')
    # Selected gifts use creation settings even when encounter override is OFF.
    open_menu();page(0);select(4);m.tap(RIGHT);m.tap(RIGHT)
    select(5)
    for _ in range(4):m.tap(R)
    select(6);m.tap(A);m.tap(B)
    check(m.read('gPlayerPartyCount',1)==2,'B cancels a permanent-action confirmation')
    m.tap(A);m.tap(A,wait=80)
    gift=pokemon(m.symbols['gPlayerParty']+200)
    check(setting(0)==0 and gift['pid']%25==1 and gift['ivs']==[31]*6,'Give selected Pokemon honors nature and IVs with override OFF')
    close_menu()
    # Native paid shop purchase and sale with infinite money preserve real balance.
    def money():return m.read(m.read('gSaveBlock1Ptr')+0x290)^m.read(m.read('gSaveBlock2Ptr')+0xF20)
    saved_money=money();old=bag_count(13)
    open_menu();page(1);select(5);m.tap(A);select(4);m.tap(A,wait=60);m.tap(A,wait=200)
    for _ in range(40):
        if bag_count(13)==old+1:break
        m.tap(A,count=10,wait=60)
    check(bag_count(13)==old+1 and money()==saved_money,'Infinite money pays for a normal-price purchase without changing stored balance')
    for _ in range(40):
        if 'Task_BuyMenu' in m.tasks():break
        m.tap(A,wait=30)
    m.tap(B,wait=250)
    for _ in range(40):
        if 'Task_ShopMenu' in m.tasks():break
        m.tap(A,wait=30)
    m.tap(DOWN);m.tap(A,wait=250)
    # The native bag retains the Balls pocket from the capture; select Items.
    for _ in range(2):m.tap(LEFT,wait=80)
    snap('sell-menu')
    for _ in range(40):
        if bag_count(13)==old:break
        m.tap(A,wait=60)
    check(bag_count(13)==old and money()==saved_money+150,'Selling with infinite money adds only the actual sale price to stored balance')
    for _ in range(40):
        if 'Task_ShopMenu' in m.tasks():break
        m.tap(B,wait=60)
    snap('sell-exit')
    m.tap(B,wait=120)
    open_menu();page(1);select(5);m.tap(A);close_menu()
    check(setting(8)==0 and money()==saved_money+150,'Disabling infinite money restores the earned balance')
    # Disabling battle mods must restore actual damage and PP consumption.
    open_menu();page(1);select(0);m.tap(A)
    for _ in range(9):m.tap(UP)
    m.tap(A);select(2);m.tap(A);close_menu()
    open_menu();page(2);select(2);m.tap(A);close_menu()
    open_menu();page(0);select(0);m.tap(A);select(7);m.tap(A,wait=500);wait_action()
    original_hp=m.read(m.symbols['gBattleMons']+0x28,2)
    original_pp=m.read(m.symbols['gBattleMons']+0x25,1)
    for _ in range(12):
        m.tap(A);m.tap(RIGHT);m.tap(A);wait_action()
        if m.read(m.symbols['gBattleMons']+0x28,2)<original_hp:break
    check(m.read(m.symbols['gBattleMons']+0x28,2)<original_hp,'Disabling infinite HP restores real enemy damage')
    check(m.read(m.symbols['gBattleMons']+0x25,1)<original_pp,'Disabling infinite PP restores real PP consumption')
    m.tap(RIGHT);m.tap(A,wait=200)
    for _ in range(2):m.tap(RIGHT,wait=80)
    m.tap(A,wait=80);m.tap(A,wait=600)
    for _ in range(150):
        if m.callback()=='CB2_Overworld':break
        if m.callback()=='CB2_NamingScreen':m.tap(START,wait=30);m.tap(A,wait=60)
        else:m.tap(B,wait=30);m.tap(A,wait=30)
    m.frames(0,120)
    check(m.callback()=='CB2_Overworld' and m.read('gPlayerPartyCount',1)==4,'Capture after disabling HP and PP returns to playable field')
    damaged=pokemon(m.symbols['gPlayerParty'])
    open_menu();page(4);select(6);m.tap(RIGHT);select(11);m.tap(A);m.tap(A,wait=80);close_menu()
    edited=pokemon(m.symbols['gPlayerParty'])
    check(edited['pp']==damaged['pp'] and edited['hp']==damaged['hp'],'Friendship-only edit preserves depleted HP and PP')
    open_menu();page(3);select(0);m.tap(A);close_menu()
    healed=pokemon(m.symbols['gPlayerParty'])
    check(healed['hp']==healed['max_hp'] and healed['pp'][1]>damaged['pp'][1] and healed['status']==0,'Heal party restores real battle damage and spent PP')
    # Wall traversal is bounded; move back to the original walkable tile before disabling.
    start=struct.unpack('<hh',position())
    open_menu();page(3);select(2);m.tap(A);m.tap(B)
    check(setting(15)==0,'Cancel leaves walk-through-walls disabled')
    m.tap(A);m.tap(A);close_menu()
    m.frames(UP,240);m.frames(0,30);m.frames(LEFT,240);m.frames(0,30)
    corner=struct.unpack('<hh',position())
    check(corner==(7,7),'Wall traversal reaches but cannot cross the map boundary')
    m.frames(UP,60);m.frames(LEFT,60);m.frames(0,30)
    check(struct.unpack('<hh',position())==corner,'Repeated wall movement remains inside map bounds')
    for direction,axis in [(RIGHT,0),(DOWN,1)]:
        for _ in range(120):
            if struct.unpack('<hh',position())[axis]>=start[axis]:break
            m.frames(direction,1)
        m.frames(0,30)
    check(struct.unpack('<hh',position())==start,'Wall traversal can return to the original walkable tile')
    open_menu();page(3);select(2);m.tap(A);select(3);m.tap(A);close_menu()
    before=position();m.frames(RIGHT,16);m.frames(0,30)
    check(position()!=before and setting(16)==1,'Fast walking moves the player and returns to idle')
    open_menu();select(5);m.tap(A);m.tap(START);m.tap(A);close_menu()
    check(not setting(15) and not setting(16),'Disable all clears traversal and speed modifiers')
    # Full party and bag failures must leave existing data intact.
    open_menu();page(0);select(6)
    for _ in range(2):m.tap(A);m.tap(A,wait=80)
    check(m.read('gPlayerPartyCount',1)==6,'Give Pokemon fills available party slots')
    before_party=m.bytes(m.symbols['gPlayerParty'],600)
    m.tap(A);m.tap(A,wait=80)
    check(m.read('gPlayerPartyCount',1)==6 and m.bytes(m.symbols['gPlayerParty'],600)==before_party,'Full-party give refuses safely without overwriting Pokemon')
    snap('party-full');close_menu()
    # A supported second ability and useful held item, including exact EV cap.
    open_menu();page(4);select(0);m.tap(R)
    select(1);m.tap(R)
    for _ in range(8):m.tap(RIGHT)
    select(4);m.tap(A)
    select(7);m.tap(A)
    for _ in range(386):
        idx=m.read('sBrowseIndex',2);ptr=m.read('sBrowseIds')
        if m.read(ptr+idx*2,2)==200:break
        m.tap(DOWN)
    m.tap(A)
    select(9);m.tap(A)
    for row in (0,1):
        select(row)
        for _ in range(26):m.tap(R)
    select(2)
    for _ in range(6):m.tap(RIGHT)
    snap('ev-valid-cap');m.tap(B);select(11);m.tap(A);m.tap(A,wait=80)
    rat=pokemon(m.symbols['gPlayerParty']+500)
    check(rat['species']==19 and rat['ability']==1 and rat['held_item']==200,'Party editor applies supported second ability and Leftovers')
    check(rat['evs']==[252,252,6,0,0,0],'Exactly 510 EVs are accepted with valid encrypted data')
    select(10);m.tap(A)
    for row in range(4):
        select(row);m.tap(A)
        # Select move zero directly with single steps, wrapping if needed.
        for _ in range(355):
            if m.read('sBrowseIndex',2)==0:break
            m.tap(UP)
        m.tap(A)
    m.tap(B);select(11)
    before=m.bytes(m.symbols['gPlayerParty']+500,100)
    m.tap(A);m.tap(A,wait=80)
    check(m.bytes(m.symbols['gPlayerParty']+500,100)==before,'An all-empty moveset is rejected without corrupting party data')
    close_menu()
    # Capture every category and its second page for layout review.
    for row,name in enumerate(['wild','items','battle','world','party']):
        open_menu();page(row);snap('ui-'+name)
        m.tap(B)
        check(m.read('sModCursor',2)==row,'Back restores parent selection: '+name)
        close_menu()
    open_menu();page(4);select(8);m.tap(A);snap('ui-iv');m.tap(B)
    select(9);m.tap(A);snap('ui-ev');m.tap(B)
    select(10);m.tap(A);snap('ui-moves');close_menu()
    m.save(out/'audit.state')
    # Use a real PP Up through the native Bag, then test preservation/reset by slot.
    open_menu();page(1);select(0);m.tap(A)
    for _ in range(386):
        idx=m.read('sBrowseIndex',2);ptr=m.read('sBrowseIds')
        if m.read(ptr+idx*2,2)==69:break
        m.tap(DOWN)
    m.tap(A);select(2);m.tap(A);close_menu()
    check(bag_count(69)==1,'PP Up is granted through the native item browser')
    m.tap(START,wait=60)
    for _ in range(10):
        cursor=m.read('sStartMenuCursorPos',1)
        if m.read(m.symbols['sStartMenuOrder']+cursor,1)==2:break
        m.tap(DOWN)
    m.tap(A,wait=200)
    for _ in range(2):m.tap(LEFT,wait=80)
    m.tap(DOWN);snap('pp-up-bag')
    for _ in range(60):
        if bag_count(69)==0:break
        m.tap(A,wait=60)
    check(bag_count(69)==0 and pokemon(m.symbols['gPlayerParty'])['pp_bonuses']==1,'Native PP Up raises the first move PP bonus')
    for _ in range(40):
        if m.callback()=='CB2_Overworld':break
        m.tap(B,wait=60)
    m.frames(0,80);m.tap(B,wait=30)
    boosted=pokemon(m.symbols['gPlayerParty'])
    open_menu();page(4);select(6);m.tap(RIGHT);select(11);m.tap(A);m.tap(A,wait=80)
    kept=pokemon(m.symbols['gPlayerParty'])
    check(kept['pp_bonuses']==boosted['pp_bonuses'] and kept['pp']==boosted['pp'],'Applying unrelated edits preserves an actual PP Up bonus and PP')
    select(10);m.tap(A);select(0);m.tap(A);m.tap(DOWN);m.tap(A);m.tap(B)
    select(11);m.tap(A);m.tap(A,wait=80);close_menu()
    changed=pokemon(m.symbols['gPlayerParty'])
    check(changed['pp_bonuses']==0 and changed['moves'][0]==boosted['moves'][0]+1 and changed['pp'][1:]==boosted['pp'][1:],'Replacing a move resets only that slot PP and PP Up bonus')
    m.save(out/'coverage.state')
    (out/'results.json').write_text(json.dumps({'variant':variant,'rom_sha256':hashlib.sha256(pathlib.Path(rom).read_bytes()).hexdigest(),'passed':passed,'input_only':True},indent=2)+'\n')
finally:
    m.close()
