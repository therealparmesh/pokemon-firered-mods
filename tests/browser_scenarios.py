# Input-only browser tests in the shared native emulator harness.
def ids():
    count=m.read('sBrowseCount',2);ptr=m.read('sBrowseIds')
    return [m.read(ptr+i*2,2) for i in range(count)]
def highlighted():return ids()[m.read('sBrowseIndex',2)]
def filter_next():m.tap(SELECT,wait=40)
def alphabetical():m.tap(START,wait=20)
def normalized(b):
    b=b.split(b'\xff')[0]
    return bytes(c-0xD5+0xBB if 0xD5<=c<=0xEE else 0xBF if c in (6,0x1B) else c for c in b)
# Dex range filters include exact endpoints and don't alter selection on cancel.
open_menu();page(0);select(1);m.tap(A);original=setting(1)
check(ids()==list(range(1,387)),'Pokemon browser defaults to complete National Dex order')
for expected,name in [(range(1,152),'Kanto'),(range(152,252),'Johto'),(range(252,387),'Hoenn')]:
    filter_next();check(ids()==list(expected),'Pokemon filter includes exact '+name+' boundaries')
snap('browser-hoenn');filter_next();selected=highlighted();alphabetical()
check(highlighted()==selected,'A-Z sorting preserves the highlighted Pokemon ID')
# Independently map National IDs through the native ROM's reverse table.
national_to_species={}
for species,national in enumerate(struct.unpack('<411H',m.bytes(m.symbols['sSpeciesToNationalPokedexNum'],822)),1):
    if national:national_to_species.setdefault(national,species)
keys=[(normalized(m.bytes(m.symbols['gSpeciesNames']+national_to_species[id]*11,11)),id) for id in ids()]
check(keys==sorted(keys),'All 386 Pokemon sort by their actual names including Hoenn mappings')
# First-generation species IDs and names are directly indexed in the native ROM.
filter_next()
keys=[(normalized(m.bytes(m.symbols['gSpeciesNames']+id*11,11)),id) for id in ids()]
check(keys==sorted(keys),'Kanto Pokemon names sort alphabetically with deterministic IDs')
snap('browser-pokemon-az');m.tap(B);check(setting(1)==original,'Cancel filtered/sorted Pokemon browser leaves setting unchanged')
select(1);m.tap(A);check(not m.read('sBrowseFilter',1) and not m.read('sBrowseAlphabetical',1),'Reopening browser resets to All/ID at the committed selection')
check(highlighted()==original,'Reopening restores the committed Pokemon ID');close_menu()
# Pocket membership is checked against the actual native item table (44-byte entries).
open_menu();page(1);select(0);m.tap(A);all_items=ids();original=setting(6)
for pocket in range(1,6):
    filter_next();chosen=ids()
    check(bool(chosen) and all(m.read(m.symbols['gItems']+id*44+26,1)==pocket for id in chosen),'Item pocket filter '+str(pocket)+' contains only matching native items')
snap('browser-berries');filter_next();alphabetical()
keys=[(normalized(m.bytes(m.symbols['gItems']+id*44,14)),id) for id in ids()]
check(keys==sorted(keys),'All item names sort alphabetically')
check(set(ids())==set(all_items),'Sorting neither drops nor duplicates valid items')
m.tap(B);check(setting(6)==original,'Cancel item filters leaves selected item unchanged');close_menu()
# Type filters keep the explicit empty-move choice and only the selected type.
open_menu();page(4);select(10);m.tap(A);select(0);m.tap(A);original=setting(39)
check(ids()==list(range(355)),'Move browser defaults to all 354 moves plus None')
for type_id in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]:
    filter_next();chosen=ids()
    check(chosen[0]==0 and all(m.read(m.symbols['gBattleMoves']+id*12+2,1)==type_id for id in chosen[1:]),'Move type filter '+str(type_id)+' contains only matching moves and None')
    if type_id==9:
        m.tap(R);check(highlighted()==chosen[-1], 'R jumps to the end of a short filtered list')
        m.tap(L);check(highlighted()==0, 'L jumps to the start of a short filtered list')
snap('browser-dark-moves');alphabetical()
chosen=ids();keys=[(normalized(m.bytes(m.symbols['gMoveNames']+id*13,13)),id) for id in chosen[1:]]
check(chosen[0]==0 and keys==sorted(keys),'Filtered move sorting retains None first and alphabetizes real moves')
select_id=chosen[-1]
for _ in range(355):
    if highlighted()==select_id:break
    m.tap(DOWN)
m.tap(A)
check(setting(39)==select_id,'Selecting a filtered sorted move stores its true move ID')
close_menu()
# Held-item filtering never reintroduces keys or mail, including when sorted.
open_menu();page(4);select(7);m.tap(A)
for _ in range(5):
    chosen=ids();check(chosen[0]==0 and all(m.read(m.symbols['gItems']+id*44+26,1)!=2 and not 121<=id<=132 for id in chosen[1:]),'Held-item browser retains safety exclusions in filter '+str(_))
    alphabetical();check(ids()[0]==0,'Held-item alphabetical order keeps None first '+str(_));filter_next()
check(m.read('sBrowseFilter',1)==0,'Held-item filter cycle skips the unusable key-item pocket')
m.tap(B);close_menu()
# Restore the draft; no browser test changes an actual Pokemon or inventory.
open_menu();page(4);select(10);m.tap(A);select(0);m.tap(A);browser_original=original
for _ in range(355):
    if highlighted()==browser_original:break
    m.tap(DOWN)
m.tap(A);close_menu()
m.save(out/'browser-restore.state');m.load(out/'coverage.state')
open_menu();page(0);select(1);m.tap(A);alphabetical();filter_next();m.tap(R);m.tap(L)
check(m.read(m.read('gSaveBlock2Ptr')+0x13,1)==2 and m.read('sBrowser',1)==1,'Filtered alphabetical L/R paging works under native L=A button mode')
close_menu();m.load(out/'browser-restore.state')
