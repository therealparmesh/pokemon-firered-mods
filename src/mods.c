#include "global.h"
#include "mods.h"
#include "pokemon.h"
#include "random.h"
#include "item.h"
#include "battle.h"
#include "battle_anim.h"
#include "constants/battle.h"
#include "constants/pokemon.h"
#include "constants/species.h"
#include "constants/moves.h"
#include "constants/items.h"

#if NATIVE_MODS
const char gNativeModBuild[] = "FRLG_NATIVE_MODS_V1";
EWRAM_DATA struct ModState gMods = {0};
EWRAM_DATA bool8 gModMenuOpen = FALSE;

u16 ModValue(u8 setting) { return gMods.values[setting]; }

// Only ongoing session effects belong here; selections and party drafts do not.
const u8 gRuntimeModSettings[MOD_RUNTIME_COUNT] = {
    C_WILD, C_SHINY, C_MONEY, C_FREE, C_HP, C_PP, C_CAPTURE,
    C_EXP, C_NO_ENCOUNTERS, C_WALLS, C_SPEED
};
bool8 ModIsEnabled(u8 setting)
{
    return ModValue(setting) != (setting == C_EXP ? 1 : 0);
}
u8 ModEnabledCount(void)
{
    u8 i, count = 0;
    for (i = 0; i < MOD_RUNTIME_COUNT; i++)
        if (ModIsEnabled(gRuntimeModSettings[i])) count++;
    return count;
}
void ModDisable(u8 setting)
{
    u8 i;
    for (i = 0; i < MOD_RUNTIME_COUNT; i++)
        if (setting == gRuntimeModSettings[i])
            gMods.values[setting] = setting == C_EXP ? 1 : 0;
}
void ModDisableAll(void)
{
    u8 i;
    for (i = 0; i < MOD_RUNTIME_COUNT; i++) ModDisable(gRuntimeModSettings[i]);
}

void ModReset(void)
{
    CpuFill16(0, &gMods, sizeof(gMods));
    gMods.values[C_SPECIES] = 1;
    gMods.values[C_LEVEL] = 5;
    gMods.values[C_ITEM] = ITEM_POTION;
    gMods.values[C_QUANTITY] = 1;
    gMods.values[C_EXP] = 1;
    gMods.values[C_FLAG] = 32;
    gModMenuOpen = FALSE;
}

// Changing an existing mon's personality must reorder and re-encrypt its data.
// Never use SetMonData(PERSONALITY) directly on an initialized Pokemon.
u32 ModPersonality(u32 otId, u8 nature, bool8 shiny, u32 previous)
{
    u32 personality;
    u16 lo, hi;
    do
    {
        lo = Random();
        if (shiny)
            hi = lo ^ (otId & 0xFFFF) ^ (otId >> 16) ^ (Random() & 7);
        else
            hi = Random();
        personality = lo | (hi << 16);
    } while (personality % NUM_NATURES != nature
          || (!shiny && GET_SHINY_VALUE(otId, personality) < SHINY_ODDS)
          || (personality & 255) != (previous & 255));
    return personality;
}

static void ModifyMon(struct Pokemon *mon, bool8 override)
{
    u32 personality, otId;
    u16 species;
    u8 nature, i, iv;
    if (!override && !ModValue(C_SHINY))
        return;
    if (override)
    {
        species = NationalPokedexNumToSpecies(ModValue(C_SPECIES));
        CreateMon(mon, species, ModValue(C_LEVEL), USE_RANDOM_IVS, FALSE, 0, OT_ID_PLAYER_ID, 0);
    }
    personality = GetMonData(mon, MON_DATA_PERSONALITY);
    otId = GetMonData(mon, MON_DATA_OT_ID);
    nature = ModValue(C_NATURE) && override ? ModValue(C_NATURE) - 1 : personality % NUM_NATURES;
    if (ModValue(C_SHINY) || (override && ModValue(C_NATURE)))
    {
        // New wild mons need not preserve gender; removes the editor's low-byte constraint.
        u16 lo, hi;
        do {
            lo = Random();
            hi = ModValue(C_SHINY) ? lo ^ (otId & 0xFFFF) ^ (otId >> 16) ^ (Random() & 7) : Random();
            personality = lo | (hi << 16);
        } while (personality % NUM_NATURES != nature);
        ModSetMonPersonality(mon, personality);
    }
    if (override && ModValue(C_IV))
    {
        iv = ModValue(C_IV) - 1;
        for (i = 0; i < 6; i++) SetMonData(mon, MON_DATA_HP_IV + i, &iv);
    }
    CalculateMonStats(mon);
}

void ModModifyWildMon(struct Pokemon *mon)
{
    ModifyMon(mon, ModValue(C_WILD));
}

void ModCreateSelectedMon(struct Pokemon *mon)
{
    ModifyMon(mon, TRUE);
}

bool8 ModBattleAllowed(void)
{
    return !(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_POKEDUDE | BATTLE_TYPE_OLD_MAN_TUTORIAL | BATTLE_TYPE_BATTLE_TOWER | BATTLE_TYPE_TRAINER_TOWER | BATTLE_TYPE_EREADER_TRAINER));
}

bool8 ModPreservePP(u8 battler)
{
    return ModBattleAllowed() && ModValue(C_PP) && GetBattlerSide(battler) == B_SIDE_PLAYER;
}

bool8 ModProtectBattler(u8 battler)
{
    return ModBattleAllowed() && ModValue(C_HP) && GetBattlerSide(battler) == B_SIDE_PLAYER;
}

void ModHealParty(void)
{
    u8 i, j, pp;
    u16 hp, move;
    u32 status = 0;
    for (i = 0; i < gPlayerPartyCount; i++)
    {
        if (GetMonData(&gPlayerParty[i], MON_DATA_IS_EGG)) continue;
        hp = GetMonData(&gPlayerParty[i], MON_DATA_MAX_HP);
        SetMonData(&gPlayerParty[i], MON_DATA_HP, &hp);
        SetMonData(&gPlayerParty[i], MON_DATA_STATUS, &status);
        for (j = 0; j < MAX_MON_MOVES; j++)
        {
            move = GetMonData(&gPlayerParty[i], MON_DATA_MOVE1 + j);
            pp = CalculatePPWithBonus(move, GetMonData(&gPlayerParty[i], MON_DATA_PP_BONUSES), j);
            SetMonData(&gPlayerParty[i], MON_DATA_PP1 + j, &pp);
        }
    }
}

void ModLoadPartyEditor(void)
{
    struct Pokemon *mon = &gPlayerParty[ModValue(C_PARTY)];
    u32 personality = GetMonData(mon, MON_DATA_PERSONALITY);
    u8 i;
    gMods.values[C_EDIT_SPECIES] = SpeciesToNationalPokedexNum(GetMonData(mon, MON_DATA_SPECIES));
    gMods.values[C_EDIT_LEVEL] = GetMonData(mon, MON_DATA_LEVEL);
    gMods.values[C_EDIT_NATURE] = personality % NUM_NATURES;
    gMods.values[C_ABILITY] = GetMonData(mon, MON_DATA_ABILITY_NUM);
    gMods.values[C_EDIT_SHINY] = GET_SHINY_VALUE(GetMonData(mon, MON_DATA_OT_ID), personality) < SHINY_ODDS;
    gMods.values[C_FRIENDSHIP] = GetMonData(mon, MON_DATA_FRIENDSHIP);
    gMods.values[C_HELD_ITEM] = GetMonData(mon, MON_DATA_HELD_ITEM);
    for (i = 0; i < 6; i++)
    {
        gMods.values[C_IV_HP+i] = GetMonData(mon, MON_DATA_HP_IV+i);
        gMods.values[C_EV_HP+i] = GetMonData(mon, MON_DATA_HP_EV+i);
    }
    for (i = 0; i < 4; i++) gMods.values[C_MOVE1+i] = GetMonData(mon, MON_DATA_MOVE1+i);
}

bool8 ModApplyPartyEditor(void)
{
    struct Pokemon *mon = &gPlayerParty[ModValue(C_PARTY)];
    u16 species, value, total = 0;
    u32 experience, personality;
    u8 i, byte, bonuses;
    bool8 hasMove = FALSE;
    if (ModValue(C_PARTY) >= gPlayerPartyCount || GetMonData(mon, MON_DATA_IS_EGG) || GetMonData(mon, MON_DATA_SANITY_IS_BAD_EGG)) return FALSE;
    for (i = 0; i < 6; i++)
    {
        if (ModValue(C_IV_HP+i) > 31 || ModValue(C_EV_HP+i) > 252) return FALSE;
        total += ModValue(C_EV_HP+i);
    }
    for (i = 0; i < 4; i++)
    {
        if (ModValue(C_MOVE1+i) >= MOVES_COUNT) return FALSE;
        if (ModValue(C_MOVE1+i)) hasMove = TRUE;
    }
    if (!hasMove || ModValue(C_EDIT_NATURE) >= NUM_NATURES || ModValue(C_EDIT_SPECIES) > 386) return FALSE;
    if (total > 510) return FALSE;
    species = NationalPokedexNumToSpecies(ModValue(C_EDIT_SPECIES));
    if (!species || ModValue(C_EDIT_LEVEL) < 1 || ModValue(C_EDIT_LEVEL) > 100) return FALSE;
    if (ModValue(C_ABILITY) && !gSpeciesInfo[species].abilities[1]) return FALSE;
    value = ModValue(C_HELD_ITEM);
    // Mail requires a separate initialized mail record; keep that engine-owned.
    if ((value >= ITEM_ORANGE_MAIL && value <= ITEM_RETRO_MAIL) || (value && (ItemId_GetId(value) != value || ItemId_GetPocket(value) == POCKET_KEY_ITEMS))) return FALSE;
    if (GetMonData(mon, MON_DATA_HELD_ITEM) >= ITEM_ORANGE_MAIL && GetMonData(mon, MON_DATA_HELD_ITEM) <= ITEM_RETRO_MAIL) return FALSE;
    // Keep progress toward the next level when changing only unrelated fields.
    if (species != GetMonData(mon, MON_DATA_SPECIES) || ModValue(C_EDIT_LEVEL) != GetMonData(mon, MON_DATA_LEVEL))
    {
        experience = gExperienceTables[gSpeciesInfo[species].growthRate][ModValue(C_EDIT_LEVEL)];
        SetMonData(mon, MON_DATA_EXP, &experience);
    }
    SetMonData(mon, MON_DATA_SPECIES, &species);
    personality = GetMonData(mon, MON_DATA_PERSONALITY);
    if (personality % NUM_NATURES != ModValue(C_EDIT_NATURE)
        || (GET_SHINY_VALUE(GetMonData(mon, MON_DATA_OT_ID), personality) < SHINY_ODDS) != ModValue(C_EDIT_SHINY))
    {
        personality = ModPersonality(GetMonData(mon, MON_DATA_OT_ID), ModValue(C_EDIT_NATURE), ModValue(C_EDIT_SHINY), personality);
        ModSetMonPersonality(mon, personality);
    }
    byte = ModValue(C_ABILITY); SetMonData(mon, MON_DATA_ABILITY_NUM, &byte);
    byte = ModValue(C_FRIENDSHIP); SetMonData(mon, MON_DATA_FRIENDSHIP, &byte);
    value = ModValue(C_HELD_ITEM); SetMonData(mon, MON_DATA_HELD_ITEM, &value);
    for (i = 0; i < 6; i++)
    {
        byte = ModValue(C_IV_HP+i); SetMonData(mon, MON_DATA_HP_IV+i, &byte);
        byte = ModValue(C_EV_HP+i); SetMonData(mon, MON_DATA_HP_EV+i, &byte);
    }
    bonuses = GetMonData(mon, MON_DATA_PP_BONUSES);
    for (i = 0; i < 4; i++)
    {
        value = ModValue(C_MOVE1+i);
        if (value != GetMonData(mon, MON_DATA_MOVE1+i))
        {
            bonuses &= ~(3 << (i * 2));
            SetMonData(mon, MON_DATA_MOVE1+i, &value);
            byte = gBattleMoves[value].pp;
            SetMonData(mon, MON_DATA_PP1+i, &byte);
        }
    }
    SetMonData(mon, MON_DATA_PP_BONUSES, &bonuses);
    CalculateMonStats(mon);
    return !GetMonData(mon, MON_DATA_SANITY_IS_BAD_EGG);
}
#endif
