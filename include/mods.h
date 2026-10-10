#ifndef GUARD_MODS_H
#define GUARD_MODS_H
#include "global.h"
enum ModSetting {
    C_WILD, C_SPECIES, C_LEVEL, C_SHINY, C_NATURE, C_IV,
    C_ITEM, C_QUANTITY, C_MONEY, C_FREE,
    C_HP, C_PP, C_CAPTURE, C_EXP, C_NO_ENCOUNTERS,
    C_WALLS, C_SPEED, C_DESTINATION, C_FLAG,
    C_PARTY, C_EDIT_SPECIES, C_EDIT_LEVEL, C_EDIT_NATURE, C_ABILITY,
    C_EDIT_SHINY, C_FRIENDSHIP, C_HELD_ITEM,
    C_IV_HP, C_IV_ATK, C_IV_DEF, C_IV_SPEED, C_IV_SPATK, C_IV_SPDEF,
    C_EV_HP, C_EV_ATK, C_EV_DEF, C_EV_SPEED, C_EV_SPATK, C_EV_SPDEF,
    C_MOVE1, C_MOVE2, C_MOVE3, C_MOVE4, C_COUNT
};
struct ModState { u16 values[C_COUNT]; };
extern struct ModState gMods;
extern bool8 gModMenuOpen;
u16 ModValue(u8 setting);
bool8 ModOpenMenu(void);
void ModReset(void);
#define MOD_RUNTIME_COUNT 11
extern const u8 gRuntimeModSettings[MOD_RUNTIME_COUNT];
bool8 ModIsEnabled(u8 setting);
u8 ModEnabledCount(void);
void ModDisable(u8 setting);
void ModDisableAll(void);
void ModCreateSelectedMon(struct Pokemon *mon);
void ModModifyWildMon(struct Pokemon *mon);
bool8 ModBattleAllowed(void);
bool8 ModPreservePP(u8 battler);
bool8 ModProtectBattler(u8 battler);
void ModSetMonPersonality(struct Pokemon *mon, u32 personality);
u32 ModPersonality(u32 otId, u8 nature, bool8 shiny, u32 previous);
void ModHealParty(void);
void ModLoadPartyEditor(void);
bool8 ModApplyPartyEditor(void);
#endif
