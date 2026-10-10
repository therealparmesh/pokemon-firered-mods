#include "global.h"
#include "gflib.h"
#include "mods.h"
#include "pokemon.h"
#include "data.h"
#include "item.h"
#include "money.h"
#include "shop.h"
#include "menu.h"
#include "new_menu_helpers.h"
#include "event_object_movement.h"
#include "event_object_lock.h"
#include "field_player_avatar.h"
#include "overworld.h"
#include "field_fadetransition.h"
#include "script.h"
#include "link.h"
#include "link_rfu.h"
#include "menu_helpers.h"
#include "quest_log.h"
#include "event_data.h"
#include "pokedex.h"
#include "battle_setup.h"
#include "battle_main.h"
#include "characters.h"
#include "safari_zone.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/species.h"
#include "constants/pokemon.h"
#include "constants/heal_locations.h"
#include "constants/songs.h"

#if NATIVE_MODS
#define MOD_NEW(button) TEST_BUTTON(gMain.newKeysRaw, button)
// Seven rows plus title, status and controls fit in 240x160.
enum { P_MAIN, P_WILD, P_ITEMS, P_BATTLE, P_WORLD, P_PARTY, P_IV, P_EV, P_MOVES, P_ACTIVE };
enum { A_NONE = C_COUNT, A_BACK, A_ADD, A_STOCK, A_SHOP, A_HEAL, A_APPLY, A_TELEPORT, A_DEX_SEEN, A_DEX_CAUGHT, A_FLAG_SET, A_FLAG_CLEAR, A_RESET, A_GIVE, A_ENCOUNTER, A_MAX_IV, A_CLEAR_EV, A_PAGE = 128 };
struct ModRow { const u8 *label; u16 id; u16 min; u16 max; };
static EWRAM_DATA u8 sModPage = 0;
static EWRAM_DATA u16 sModCursor = 0;
static EWRAM_DATA u16 sOpeningKeys = 0;
static EWRAM_DATA u16 sPageCursors[10] = {0};
static EWRAM_DATA struct ModRow sActiveRows[MOD_RUNTIME_COUNT + 2] = {0};
static EWRAM_DATA u8 sActiveCount = 0;
static EWRAM_DATA u8 sWindow = 0;
static EWRAM_DATA u8 sBrowser = C_COUNT;
static EWRAM_DATA u16 sBrowseIndex = 0;
static EWRAM_DATA u16 sBrowseCount = 0;
static EWRAM_DATA u16 *sBrowseIds = NULL;
static EWRAM_DATA const u8 **sBrowseNames = NULL;
static EWRAM_DATA u8 *sBrowseKeys = NULL;
static EWRAM_DATA u8 sBrowseFilter = 0;
static EWRAM_DATA bool8 sBrowseAlphabetical = FALSE;
static EWRAM_DATA u16 sConfirm = A_NONE;
static EWRAM_DATA u16 sStock[9] = {ITEM_POTION, ITEM_POKE_BALL, ITEM_ANTIDOTE, ITEM_REPEL, ITEM_NONE};
static EWRAM_DATA u8 sStockCount = 4;
static EWRAM_DATA const u8 *sStatus = NULL;
static const u8 sSlash[] = _("/");
static const u8 sNone[] = _("None");
static const u8 sOn[] = _("ON");
static const u8 sOff[] = _("OFF");
static const u8 sRandom[] = _("Random");
static const u8 sDone[] = _("Done.");
static const u8 sFailed[] = _("Unavailable / invalid / bag full.");
static const u8 sWarn[] = _("Risk: save first! A confirms; B cancels.");
static const u8 sControls[] = _("A: choose  B: back  Left/Right: edit");
static const u8 sBrowseControls[] = _("A: select  B: cancel  L/R: +/-10");
static const u8 sFilterPrefix[] = _("SEL: ");
static const u8 sSortID[] = _("  START: ID");
static const u8 sSortAZ[] = _("  START: A-Z");
static const u8 sAll[] = _("All");
static const u8 sKanto[] = _("Kanto 1-151");
static const u8 sJohto[] = _("Johto 152-251");
static const u8 sHoenn[] = _("Hoenn 252-386");
static const u8 sPocketItems[] = _("Items");
static const u8 sPocketKeys[] = _("Key items");
static const u8 sPocketBalls[] = _("Balls");
static const u8 sPocketTM[] = _("TMs/HMs");
static const u8 sPocketBerries[] = _("Berries");
static const u8 sEmpty[] = _("No matching entries. SEL: next filter");
static const u8 *const sRegionFilters[] = {sAll, sKanto, sJohto, sHoenn};
static const u8 *const sPocketFilters[] = {sAll, sPocketItems, sPocketKeys, sPocketBalls, sPocketTM, sPocketBerries};
static const u8 sTypeFilters[] = {TYPE_NORMAL, TYPE_FIGHTING, TYPE_FLYING, TYPE_POISON, TYPE_GROUND, TYPE_ROCK, TYPE_BUG, TYPE_GHOST, TYPE_STEEL, TYPE_MYSTERY, TYPE_FIRE, TYPE_WATER, TYPE_GRASS, TYPE_ELECTRIC, TYPE_PSYCHIC, TYPE_ICE, TYPE_DRAGON, TYPE_DARK};
static const u8 sDraft[] = _("Draft: use Apply edits to save.");
static const u8 sApplied[] = _("Party edits applied.");
static const u8 sInvalidParty[] = _("Check EV total, ability, moves or item.");
static const u8 sNeedParty[] = _("A usable party Pokemon is required.");
static const u8 sNeedOverride[] = _("Enable Override; leave Safari first.");
static const u8 sNeedStory[] = _("Obtain your starter / Pokedex first.");
static const u8 sFullParty[] = _("Party full. Deposit a Pokemon first.");
static const u8 sDisabled[] = _("Modifiers off. Prior edits remain.");
static const u8 sChooseSpecies[] = _("Choose Pokemon");
static const u8 sChooseItem[] = _("Choose item");
static const u8 sChooseMove[] = _("Choose move");
static const u8 sMaxIV[] = _("Set all IVs to 31");
static const u8 sClearEV[] = _("Clear all EVs");
static const u8 sEVTotal[] = _("EV total: ");
static const u8 sEVLimit[] = _(" / 510 - Apply in Party");
static const u8 sActiveTitle[] = _("MODS / Active");
static const u8 sActivePrefix[] = _("Active: ");
static const u8 sActiveHint[] = _("  SELECT: review");
static const u8 sActiveSession[] = _("  Prior edits remain.");
static const u8 sActiveControls[] = _("A: disable  B: back  START: all");
static const u8 sDisableWarn[] = _("Disable session mods? A: yes B: no");
static const u8 sDisableAll[] = _("Disable all mods");
static const u8 sNoActive[] = _("No active session mods.");
static const u8 sWildOverride[] = _("Wild override");
static const u8 sActiveWalls[] = _("Walk through walls");
static const u8 sActiveBack[] = _("Back");
static const u8 sSession[] = _("Session settings - reset at power-off");
static const u8 sArrow[] = _(">");
static const struct WindowTemplate sWindowTemplate = {0, 1, 1, 28, 18, 15, 8};
static void Draw(void);
static bool8 SpeciesBrowser(void);
static bool8 MoveBrowser(void);
static void Task_ModMenu(u8 taskId);
static void Close(u8 taskId);
static const u8 sTitle0[] = _("MODS / Main");
static const u8 sLabel0_0[] = _("Wild Pokemon");
static const u8 sLabel0_1[] = _("Items and shop");
static const u8 sLabel0_2[] = _("Battle modifiers");
static const u8 sLabel0_3[] = _("Player and world");
static const u8 sLabel0_4[] = _("Party editor");
static const u8 sLabel0_5[] = _("Active mods");
static const u8 sLabel0_6[] = _("Return to game");
static const struct ModRow sRows0[] = {
    {sLabel0_0, A_PAGE+P_WILD, 0, 0},
    {sLabel0_1, A_PAGE+P_ITEMS, 0, 0},
    {sLabel0_2, A_PAGE+P_BATTLE, 0, 0},
    {sLabel0_3, A_PAGE+P_WORLD, 0, 0},
    {sLabel0_4, A_PAGE+P_PARTY, 0, 0},
    {sLabel0_5, A_PAGE+P_ACTIVE, 0, 0},
    {sLabel0_6, A_BACK, 0, 0},
};
static const u8 sTitle1[] = _("MODS / Wild");
static const u8 sLabel1_0[] = _("Override");
static const u8 sLabel1_1[] = _("Species");
static const u8 sLabel1_2[] = _("Level");
static const u8 sLabel1_3[] = _("Always shiny");
static const u8 sLabel1_4[] = _("Nature");
static const u8 sLabel1_5[] = _("All IVs");
static const u8 sLabel1_6[] = _("Back");
static const u8 sGive[] = _("Give selected Pokemon !");
static const u8 sEncounter[] = _("Start selected encounter");
static const struct ModRow sRows1[] = {
    {sLabel1_0, C_WILD, 0, 1},
    {sLabel1_1, C_SPECIES, 1, 386},
    {sLabel1_2, C_LEVEL, 1, 100},
    {sLabel1_3, C_SHINY, 0, 1},
    {sLabel1_4, C_NATURE, 0, 25},
    {sLabel1_5, C_IV, 0, 32},
    {sGive, A_GIVE, 0, 0},
    {sEncounter, A_ENCOUNTER, 0, 0},
    {sLabel1_6, A_BACK, 0, 0},
};
static const u8 sTitle2[] = _("MODS / Items");
static const u8 sLabel2_0[] = _("Item");
static const u8 sLabel2_1[] = _("Quantity");
static const u8 sLabel2_2[] = _("Add to bag");
static const u8 sLabel2_3[] = _("Add to shop stock");
static const u8 sLabel2_4[] = _("Open mod shop");
static const u8 sLabel2_5[] = _("Infinite money");
static const u8 sLabel2_6[] = _("Free purchases");
static const u8 sLabel2_7[] = _("Back");
static const struct ModRow sRows2[] = {
    {sLabel2_0, C_ITEM, 1, 374},
    {sLabel2_1, C_QUANTITY, 1, 999},
    {sLabel2_2, A_ADD, 0, 0},
    {sLabel2_3, A_STOCK, 0, 0},
    {sLabel2_4, A_SHOP, 0, 0},
    {sLabel2_5, C_MONEY, 0, 1},
    {sLabel2_6, C_FREE, 0, 1},
    {sLabel2_7, A_BACK, 0, 0},
};
static const u8 sTitle3[] = _("MODS / Battle");
static const u8 sLabel3_0[] = _("Infinite HP");
static const u8 sLabel3_1[] = _("Infinite PP");
static const u8 sLabel3_2[] = _("Guaranteed catch");
static const u8 sLabel3_3[] = _("EXP multiplier");
static const u8 sLabel3_4[] = _("No encounters");
static const u8 sLabel3_5[] = _("Always shiny");
static const u8 sLabel3_6[] = _("Back");
static const struct ModRow sRows3[] = {
    {sLabel3_0, C_HP, 0, 1},
    {sLabel3_1, C_PP, 0, 1},
    {sLabel3_2, C_CAPTURE, 0, 1},
    {sLabel3_3, C_EXP, 1, 10},
    {sLabel3_4, C_NO_ENCOUNTERS, 0, 1},
    {sLabel3_5, C_SHINY, 0, 1},
    {sLabel3_6, A_BACK, 0, 0},
};
static const u8 sTitle4[] = _("MODS / World");
static const u8 sLabel4_0[] = _("Heal party");
static const u8 sLabel4_1[] = _("Infinite money");
static const u8 sLabel4_2[] = _("Walk walls !");
static const u8 sLabel4_3[] = _("Fast walking");
static const u8 sLabel4_4[] = _("Destination");
static const u8 sLabel4_5[] = _("Teleport !");
static const u8 sLabel4_6[] = _("Dex: seen all !");
static const u8 sLabel4_7[] = _("Dex: caught all !");
static const u8 sLabel4_8[] = _("Story flag ID");
static const u8 sLabel4_9[] = _("Set flag !");
static const u8 sLabel4_10[] = _("Clear flag !");
static const u8 sLabel4_11[] = _("Back");
static const struct ModRow sRows4[] = {
    {sLabel4_0, A_HEAL, 0, 0},
    {sLabel4_1, C_MONEY, 0, 1},
    {sLabel4_2, C_WALLS, 0, 1},
    {sLabel4_3, C_SPEED, 0, 1},
    {sLabel4_4, C_DESTINATION, 0, 20},
    {sLabel4_5, A_TELEPORT, 0, 0},
    {sLabel4_6, A_DEX_SEEN, 0, 0},
    {sLabel4_7, A_DEX_CAUGHT, 0, 0},
    {sLabel4_8, C_FLAG, 32, 1279},
    {sLabel4_9, A_FLAG_SET, 0, 0},
    {sLabel4_10, A_FLAG_CLEAR, 0, 0},
    {sLabel4_11, A_BACK, 0, 0},
};
static const u8 sTitle5[] = _("MODS / Party");
static const u8 sLabel5_0[] = _("Party slot");
static const u8 sLabel5_1[] = _("Species");
static const u8 sLabel5_2[] = _("Level");
static const u8 sLabel5_3[] = _("Nature");
static const u8 sLabel5_4[] = _("Ability");
static const u8 sLabel5_5[] = _("Shiny");
static const u8 sLabel5_6[] = _("Friendship");
static const u8 sLabel5_7[] = _("Held item");
static const u8 sLabel5_8[] = _("IV editor");
static const u8 sLabel5_9[] = _("EV editor");
static const u8 sLabel5_10[] = _("Move editor");
static const u8 sLabel5_11[] = _("Apply edits !");
static const u8 sLabel5_12[] = _("Back");
static const struct ModRow sRows5[] = {
    {sLabel5_0, C_PARTY, 0, 5},
    {sLabel5_1, C_EDIT_SPECIES, 1, 386},
    {sLabel5_2, C_EDIT_LEVEL, 1, 100},
    {sLabel5_3, C_EDIT_NATURE, 0, 24},
    {sLabel5_4, C_ABILITY, 0, 1},
    {sLabel5_5, C_EDIT_SHINY, 0, 1},
    {sLabel5_6, C_FRIENDSHIP, 0, 255},
    {sLabel5_7, C_HELD_ITEM, 0, 374},
    {sLabel5_8, A_PAGE+P_IV, 0, 0},
    {sLabel5_9, A_PAGE+P_EV, 0, 0},
    {sLabel5_10, A_PAGE+P_MOVES, 0, 0},
    {sLabel5_11, A_APPLY, 0, 0},
    {sLabel5_12, A_BACK, 0, 0},
};
static const u8 sTitle6[] = _("MODS / IV");
static const u8 sLabel6_0[] = _("HP");
static const u8 sLabel6_1[] = _("Attack");
static const u8 sLabel6_2[] = _("Defense");
static const u8 sLabel6_3[] = _("Speed");
static const u8 sLabel6_4[] = _("Sp. Attack");
static const u8 sLabel6_5[] = _("Sp. Defense");
static const u8 sLabel6_6[] = _("Back");
static const struct ModRow sRows6[] = {
    {sLabel6_0, C_IV_HP, 0, 31},
    {sLabel6_1, C_IV_ATK, 0, 31},
    {sLabel6_2, C_IV_DEF, 0, 31},
    {sLabel6_3, C_IV_SPEED, 0, 31},
    {sLabel6_4, C_IV_SPATK, 0, 31},
    {sLabel6_5, C_IV_SPDEF, 0, 31},
    {sMaxIV, A_MAX_IV, 0, 0},
    {sLabel6_6, A_BACK, 0, 0},
};
static const u8 sTitle7[] = _("MODS / EV");
static const u8 sLabel7_0[] = _("HP");
static const u8 sLabel7_1[] = _("Attack");
static const u8 sLabel7_2[] = _("Defense");
static const u8 sLabel7_3[] = _("Speed");
static const u8 sLabel7_4[] = _("Sp. Attack");
static const u8 sLabel7_5[] = _("Sp. Defense");
static const u8 sLabel7_6[] = _("Back (total max 510)");
static const struct ModRow sRows7[] = {
    {sLabel7_0, C_EV_HP, 0, 252},
    {sLabel7_1, C_EV_ATK, 0, 252},
    {sLabel7_2, C_EV_DEF, 0, 252},
    {sLabel7_3, C_EV_SPEED, 0, 252},
    {sLabel7_4, C_EV_SPATK, 0, 252},
    {sLabel7_5, C_EV_SPDEF, 0, 252},
    {sClearEV, A_CLEAR_EV, 0, 0},
    {sLabel7_6, A_BACK, 0, 0},
};
static const u8 sTitle8[] = _("MODS / Moves");
static const u8 sLabel8_0[] = _("Move 1");
static const u8 sLabel8_1[] = _("Move 2");
static const u8 sLabel8_2[] = _("Move 3");
static const u8 sLabel8_3[] = _("Move 4");
static const u8 sLabel8_4[] = _("Back");
static const struct ModRow sRows8[] = {
    {sLabel8_0, C_MOVE1, 0, 354},
    {sLabel8_1, C_MOVE2, 0, 354},
    {sLabel8_2, C_MOVE3, 0, 354},
    {sLabel8_3, C_MOVE4, 0, 354},
    {sLabel8_4, A_BACK, 0, 0},
};
static const struct ModRow *const sModPages[] = {sRows0,sRows1,sRows2,sRows3,sRows4,sRows5,sRows6,sRows7,sRows8,NULL};
static const u8 sCounts[] = {ARRAY_COUNT(sRows0),ARRAY_COUNT(sRows1),ARRAY_COUNT(sRows2),ARRAY_COUNT(sRows3),ARRAY_COUNT(sRows4),ARRAY_COUNT(sRows5),ARRAY_COUNT(sRows6),ARRAY_COUNT(sRows7),ARRAY_COUNT(sRows8),0};
static const u8 *const sTitles[] = {sTitle0,sTitle1,sTitle2,sTitle3,sTitle4,sTitle5,sTitle6,sTitle7,sTitle8,sActiveTitle};
static void BuildActiveRows(void)
{
    static const u8 *const labels[MOD_RUNTIME_COUNT] = {
        sWildOverride, sLabel3_5, sLabel2_5, sLabel2_6, sLabel3_0,
        sLabel3_1, sLabel3_2, sLabel3_3, sLabel3_4, sActiveWalls, sLabel4_3
    };
    u8 i;
    sActiveCount = 0;
    for (i = 0; i < MOD_RUNTIME_COUNT; i++)
        if (ModIsEnabled(gRuntimeModSettings[i]))
        {
            sActiveRows[sActiveCount].label = labels[i];
            sActiveRows[sActiveCount++].id = gRuntimeModSettings[i];
        }
    sActiveRows[sActiveCount].label = sDisableAll;
    sActiveRows[sActiveCount].id = A_RESET;
    sActiveRows[sActiveCount + 1].label = sActiveBack;
    sActiveRows[sActiveCount + 1].id = A_BACK;
    if (sModCursor > sActiveCount + 1) sModCursor = sActiveCount + 1;
}
static const struct ModRow *Rows(void)
{
    return sModPage == P_ACTIVE ? sActiveRows : sModPages[sModPage];
}
static u16 RowCount(void)
{
    return sModPage == P_ACTIVE ? sActiveCount + 2 : sCounts[sModPage];
}
static const u8 sNature0[] = _("Hardy");
static const u8 sNature1[] = _("Lonely");
static const u8 sNature2[] = _("Brave");
static const u8 sNature3[] = _("Adamant");
static const u8 sNature4[] = _("Naughty");
static const u8 sNature5[] = _("Bold");
static const u8 sNature6[] = _("Docile");
static const u8 sNature7[] = _("Relaxed");
static const u8 sNature8[] = _("Impish");
static const u8 sNature9[] = _("Lax");
static const u8 sNature10[] = _("Timid");
static const u8 sNature11[] = _("Hasty");
static const u8 sNature12[] = _("Serious");
static const u8 sNature13[] = _("Jolly");
static const u8 sNature14[] = _("Naive");
static const u8 sNature15[] = _("Modest");
static const u8 sNature16[] = _("Mild");
static const u8 sNature17[] = _("Quiet");
static const u8 sNature18[] = _("Bashful");
static const u8 sNature19[] = _("Rash");
static const u8 sNature20[] = _("Calm");
static const u8 sNature21[] = _("Gentle");
static const u8 sNature22[] = _("Sassy");
static const u8 sNature23[] = _("Careful");
static const u8 sNature24[] = _("Quirky");
static const u8 *const sNatures[] = {sNature0,sNature1,sNature2,sNature3,sNature4,sNature5,sNature6,sNature7,sNature8,sNature9,sNature10,sNature11,sNature12,sNature13,sNature14,sNature15,sNature16,sNature17,sNature18,sNature19,sNature20,sNature21,sNature22,sNature23,sNature24};
static const u8 sCity0[] = _("Last heal");
static const u8 sCity1[] = _("Pallet Town");
static const u8 sCity2[] = _("Viridian City");
static const u8 sCity3[] = _("Pewter City");
static const u8 sCity4[] = _("Cerulean City");
static const u8 sCity5[] = _("Lavender Town");
static const u8 sCity6[] = _("Vermilion City");
static const u8 sCity7[] = _("Celadon City");
static const u8 sCity8[] = _("Fuchsia City");
static const u8 sCity9[] = _("Cinnabar Island");
static const u8 sCity10[] = _("Indigo Plateau");
static const u8 sCity11[] = _("Saffron City");
static const u8 sCity12[] = _("Route 4");
static const u8 sCity13[] = _("Route 10");
static const u8 sCity14[] = _("One Island");
static const u8 sCity15[] = _("Two Island");
static const u8 sCity16[] = _("Three Island");
static const u8 sCity17[] = _("Four Island");
static const u8 sCity18[] = _("Five Island");
static const u8 sCity19[] = _("Seven Island");
static const u8 sCity20[] = _("Six Island");
static const u8 *const sCities[] = {sCity0,sCity1,sCity2,sCity3,sCity4,sCity5,sCity6,sCity7,sCity8,sCity9,sCity10,sCity11,sCity12,sCity13,sCity14,sCity15,sCity16,sCity17,sCity18,sCity19,sCity20};

static void Print(const u8 *text, u8 x, u8 y)
{
    AddTextPrinterParameterized(sWindow, FONT_SMALL, text, x, y, TEXT_SKIP_DRAW, NULL);
}
static void FormatValue(u8 setting, u16 value, u8 *text)
{
    if (setting == C_SPECIES || setting == C_EDIT_SPECIES)
        StringCopy(text, gSpeciesNames[NationalPokedexNumToSpecies(value)]);
    else if (setting == C_ABILITY) StringCopy(text, gAbilityNames[gSpeciesInfo[NationalPokedexNumToSpecies(ModValue(C_EDIT_SPECIES))].abilities[value]]);
    else if (setting == C_HELD_ITEM && !value) StringCopy(text, sNone);
    else if (setting == C_ITEM || setting == C_HELD_ITEM) CopyItemName(value, text);
    else if (setting >= C_MOVE1 && setting <= C_MOVE4) StringCopy(text, gMoveNames[value]);
    else if (setting == C_NATURE) StringCopy(text, value ? sNatures[value-1] : sRandom);
    else if (setting == C_EDIT_NATURE) StringCopy(text, sNatures[value]);
    else if (setting == C_DESTINATION) StringCopy(text, sCities[value]);
    else if (setting == C_IV && !value) StringCopy(text, sRandom);
    else if (setting == C_WILD || setting == C_SHINY || setting == C_MONEY || setting == C_FREE || setting == C_HP || setting == C_PP || setting == C_CAPTURE || setting == C_NO_ENCOUNTERS || setting == C_WALLS || setting == C_SPEED || setting == C_EDIT_SHINY)
        StringCopy(text, value ? sOn : sOff);
    else ConvertIntToDecimalStringN(text, value + (setting == C_PARTY) - (setting == C_IV && value), STR_CONV_MODE_LEFT_ALIGN, 4);
}
static void Draw(void)
{
    u16 first, index, total;
    u8 row;
    u8 value[64];
    FillWindowPixelBuffer(sWindow, PIXEL_FILL(1));
    Print(sBrowser == C_COUNT ? sTitles[sModPage] : (sBrowser == C_SPECIES || sBrowser == C_EDIT_SPECIES) ? sChooseSpecies : (sBrowser >= C_MOVE1 && sBrowser <= C_MOVE4) ? sChooseMove : sChooseItem, 2, 0);
    total = sBrowser < C_COUNT ? sBrowseCount : RowCount();
    index = sBrowser < C_COUNT ? sBrowseIndex : sModCursor;
    first = index / 7 * 7;
    ConvertIntToDecimalStringN(value, total ? index + 1 : 0, STR_CONV_MODE_LEFT_ALIGN, 3);
    StringAppend(value, sSlash);
    ConvertIntToDecimalStringN(value + StringLength(value), total, STR_CONV_MODE_LEFT_ALIGN, 3);
    Print(value, 222 - GetStringWidth(FONT_SMALL, value, 0), 0);
    for (row = 0; row < 7 && first+row < total; row++)
    {
        u16 id;
        if (first+row == index) Print(sArrow, 0, 18+row*14);
        if (sBrowser < C_COUNT)
        {
            FormatValue(sBrowser, sBrowseIds[first+row], value);
            Print(value, 12, 18+row*14);
        }
        else
        {
            const struct ModRow *entry = &Rows()[first+row];
            id = entry->id;
            Print(entry->label, 12, 18+row*14);
            if (sModPage == P_MAIN && id == A_PAGE+P_ACTIVE)
            {
                ConvertIntToDecimalStringN(value, ModEnabledCount(), STR_CONV_MODE_LEFT_ALIGN, 2);
                Print(value, 126, 18+row*14);
            }
            else if (id < C_COUNT)
            {
                FormatValue(id, ModValue(id), value);
                Print(value, 126, 18+row*14);
            }
        }
    }
    if (sBrowser < C_COUNT)
    {
        const u8 *filter = SpeciesBrowser() ? sRegionFilters[sBrowseFilter] : MoveBrowser() ? (sBrowseFilter ? gTypeNames[sTypeFilters[sBrowseFilter-1]] : sAll) : sPocketFilters[sBrowseFilter];
        StringCopy(value, sFilterPrefix);
        StringAppend(value, filter);
        StringAppend(value, sBrowseAlphabetical ? sSortAZ : sSortID);
        Print(value, 0, 119);
        if (!total) Print(sEmpty, 0, 48);
    }
    else if (sModPage == P_EV && sConfirm == A_NONE && !sStatus)
    {
        u16 sum = 0;
        for (row = 0; row < 6; row++) sum += ModValue(C_EV_HP + row);
        StringCopy(value, sEVTotal);
        ConvertIntToDecimalStringN(value + StringLength(value), sum, STR_CONV_MODE_LEFT_ALIGN, 4);
        StringAppend(value, sEVLimit);
        Print(value, 0, 119);
    }
    else if (sModPage == P_MAIN && !sStatus)
    {
        StringCopy(value, sActivePrefix);
        ConvertIntToDecimalStringN(value + StringLength(value), ModEnabledCount(), STR_CONV_MODE_LEFT_ALIGN, 2);
        StringAppend(value, sActiveHint);
        Print(value, 0, 119);
    }
    else if (sModPage == P_ACTIVE && sConfirm == A_NONE && !sStatus)
    {
        StringCopy(value, sActivePrefix);
        ConvertIntToDecimalStringN(value + StringLength(value), sActiveCount, STR_CONV_MODE_LEFT_ALIGN, 2);
        StringAppend(value, sActiveSession);
        Print(value, 0, 119);
    }
    else Print(sConfirm == A_RESET ? sDisableWarn : sConfirm != A_NONE ? sWarn : sStatus ? sStatus : sModPage >= P_PARTY ? sDraft : sSession, 0, 119);
    if (sModPage == P_ACTIVE && !sActiveCount) Print(sNoActive, 12, 60);
    Print(sBrowser < C_COUNT ? sBrowseControls : sModPage == P_ACTIVE ? sActiveControls : sControls, 0, 132);
    CopyWindowToVram(sWindow, COPYWIN_FULL);
}
static void NormalizeAbility(void)
{
    if (!gSpeciesInfo[NationalPokedexNumToSpecies(ModValue(C_EDIT_SPECIES))].abilities[1])
        gMods.values[C_ABILITY] = 0;
}
static bool8 ValidHeldItem(u16 id)
{
    return id == ITEM_NONE || (ItemId_GetPocket(id) != POCKET_KEY_ITEMS && !(id >= ITEM_ORANGE_MAIL && id <= ITEM_RETRO_MAIL));
}
static bool8 ValidItem(u16 id)
{
    return id == ITEM_NONE || (id < ITEMS_COUNT && ItemId_GetId(id) == id && ItemId_GetPocket(id) != 0);
}
static bool8 SpeciesBrowser(void)
{
    return sBrowser == C_SPECIES || sBrowser == C_EDIT_SPECIES;
}
static bool8 MoveBrowser(void)
{
    return sBrowser >= C_MOVE1 && sBrowser <= C_MOVE4;
}
static u8 BrowserFilterCount(void)
{
    return SpeciesBrowser() ? ARRAY_COUNT(sRegionFilters) : MoveBrowser() ? ARRAY_COUNT(sTypeFilters)+1 : ARRAY_COUNT(sPocketFilters);
}
static const u8 *BrowserName(u16 id)
{
    return sBrowseNames[id];
}
static u8 SortCharacter(u8 c)
{
    if (c >= CHAR_a && c <= CHAR_z) return c - CHAR_a + CHAR_A;
    if (c == CHAR_E_ACUTE || c == CHAR_e_ACUTE) return CHAR_E;
    return c;
}
static s16 CompareBrowserIds(u16 a, u16 b)
{
    const u8 *left, *right;
    if (!a || !b) return a - b; // None remains first in every order.
    left = sBrowseKeys + a * 16; right = sBrowseKeys + b * 16;
    while (*left && *left == *right) { left++; right++; }
    if (*left != *right) return *left - *right;
    return a - b; // Stable deterministic tie-break for identical names.
}
static bool8 MatchesBrowserFilter(u16 id)
{
    if (!sBrowseFilter || !id) return TRUE;
    if (SpeciesBrowser())
        return sBrowseFilter == 1 ? id <= 151 : sBrowseFilter == 2 ? id >= 152 && id <= 251 : id >= 252;
    if (MoveBrowser()) return gBattleMoves[id].type == sTypeFilters[sBrowseFilter-1];
    return ItemId_GetPocket(id) == sBrowseFilter;
}
static void RebuildBrowser(u16 preferred)
{
    u16 i, limit, gap, entry;
    s16 j;
    sBrowseCount = 0; sBrowseIndex = 0;
    limit = SpeciesBrowser() ? 387 : MoveBrowser() ? MOVES_COUNT : ITEMS_COUNT;
    for (i = (SpeciesBrowser() || sBrowser == C_ITEM) ? 1 : 0; i < limit; i++)
    {
        if (limit == ITEMS_COUNT && !ValidItem(i)) continue;
        if (sBrowser == C_HELD_ITEM && !ValidHeldItem(i)) continue;
        if (!MatchesBrowserFilter(i)) continue;
        sBrowseIds[sBrowseCount++] = i;
    }
    // Shell sort avoids a quadratic pause while drawing a large native list.
    if (sBrowseAlphabetical)
        for (gap = sBrowseCount / 2; gap; gap /= 2)
            for (i = gap; i < sBrowseCount; i++)
            {
                entry = sBrowseIds[i]; j = i;
                while (j >= gap && CompareBrowserIds(sBrowseIds[j-gap], entry) > 0)
                {
                    sBrowseIds[j] = sBrowseIds[j-gap]; j -= gap;
                }
                sBrowseIds[j] = entry;
            }
    for (i = 0; i < sBrowseCount; i++)
        if (sBrowseIds[i] == preferred) { sBrowseIndex = i; break; }
}
static void Browser(u8 setting)
{
    u16 i, national, limit;
    u8 j, text[32];
    sBrowseIds = Alloc(386 * sizeof(u16));
    sBrowseNames = AllocZeroed(387 * sizeof(const u8 *));
    sBrowseKeys = AllocZeroed(387 * 16);
    if (!sBrowseIds || !sBrowseNames || !sBrowseKeys)
    {
        if (sBrowseIds) Free(sBrowseIds);
        if (sBrowseNames) Free(sBrowseNames);
        if (sBrowseKeys) Free(sBrowseKeys);
        sBrowseIds = NULL; sBrowseNames = NULL; sBrowseKeys = NULL; sStatus = sFailed;
        return;
    }
    sBrowser = setting; sBrowseFilter = 0; sBrowseAlphabetical = FALSE;
    sBrowseNames[0] = sNone;
    if (SpeciesBrowser())
    {
        // Build the reverse mapping once, rather than scanning it per comparison.
        for (i = 1; i < NUM_SPECIES; i++)
        {
            national = SpeciesToNationalPokedexNum(i);
            if (national && national <= 386 && !sBrowseNames[national])
                sBrowseNames[national] = gSpeciesNames[i];
        }
    }
    else if (MoveBrowser())
        for (i = 1; i < MOVES_COUNT; i++) sBrowseNames[i] = gMoveNames[i];
    else
        for (i = 1; i < ITEMS_COUNT; i++) sBrowseNames[i] = gItems[i].name;
    limit = SpeciesBrowser() ? 387 : MoveBrowser() ? MOVES_COUNT : ITEMS_COUNT;
    for (i = 1; i < limit; i++)
    {
        if (!SpeciesBrowser() && !MoveBrowser()) CopyItemName(i, text);
        else StringCopy(text, BrowserName(i));
        for (j = 0; j < 15 && text[j] != EOS; j++) sBrowseKeys[i*16+j] = SortCharacter(text[j]) + 1; // Native space is 0; reserve key 0 for the terminator.
    }
    RebuildBrowser(ModValue(setting));
}
static void Close(u8 taskId)
{
    if (sBrowseIds) { Free(sBrowseIds); sBrowseIds = NULL; }
    if (sBrowseNames) { Free(sBrowseNames); sBrowseNames = NULL; }
    if (sBrowseKeys) { Free(sBrowseKeys); sBrowseKeys = NULL; }
    ClearStdWindowAndFrame(sWindow, TRUE);
    RemoveWindow(sWindow);
    DestroyTask(taskId);
    gModMenuOpen = FALSE;
    ClearPlayerHeldMovementAndUnfreezeObjectEvents();
    UnlockPlayerFieldControls();
}
static void Action(u16 action, u8 taskId)
{
    u16 i, item;
    bool8 ok = TRUE;
    sStatus = sDone;
    if (action == A_ADD)
    {
        item = ModValue(C_ITEM);
        ok = ValidItem(item) && AddBagItem(item, ItemId_GetPocket(item) == POCKET_KEY_ITEMS ? 1 : ModValue(C_QUANTITY));
    }
    else if (action == A_GIVE)
    {
        struct Pokemon *mon;
        ok = gPlayerPartyCount < PARTY_SIZE;
        mon = ok ? AllocZeroed(sizeof(struct Pokemon)) : NULL;
        if (!mon) ok = FALSE;
        else
        {
            ModCreateSelectedMon(mon);
            ok = GiveMonToPlayer(mon) == MON_GIVEN_TO_PARTY;
            Free(mon);
        }
    }
    else if (action == A_ENCOUNTER)
    {
        ok = FALSE;
        for (i = 0; i < gPlayerPartyCount; i++)
            if (!GetMonData(&gPlayerParty[i], MON_DATA_IS_EGG) && GetMonData(&gPlayerParty[i], MON_DATA_HP)) ok = TRUE;
        if (!ok) { sStatus = sNeedParty; return; }
        ok = ModValue(C_WILD) && !GetSafariZoneFlag();
        if (ok)
        {
            ZeroEnemyPartyMons();
            CreateMon(&gEnemyParty[0], NationalPokedexNumToSpecies(ModValue(C_SPECIES)), ModValue(C_LEVEL), USE_RANDOM_IVS, FALSE, 0, OT_ID_PLAYER_ID, 0);
            Close(taskId);
            StartWildBattle();
            return;
        }
    }
    else if (action == A_STOCK)
    {
        item = ModValue(C_ITEM);
        // Native shop quantity arithmetic assumes nonzero prices and ordinary pockets.
        ok = ValidItem(item) && ItemId_GetPrice(item) && ItemId_GetPocket(item) != POCKET_KEY_ITEMS;
        if (ok)
        {
            for (i = 0; i < sStockCount && sStock[i] != item; i++);
            if (i == sStockCount)
            {
                if (sStockCount == 8)
                {
                    for (i = 0; i < 7; i++) sStock[i] = sStock[i+1];
                    sStockCount = 7;
                }
                sStock[sStockCount++] = item;
                sStock[sStockCount] = ITEM_NONE;
            }
        }
    }
    else if (action == A_SHOP)
    {
        Close(taskId);
        CreateModPokemartMenu(sStock);
        return;
    }
    else if (action == A_HEAL) ModHealParty();
    else if (action == A_APPLY) { ok = ModApplyPartyEditor(); sStatus = sApplied; }
    else if (action == A_MAX_IV || action == A_CLEAR_EV)
    {
        for (i = 0; i < 6; i++) gMods.values[(action == A_MAX_IV ? C_IV_HP : C_EV_HP) + i] = action == A_MAX_IV ? 31 : 0;
        sStatus = sDraft;
    }
    else if (action == A_TELEPORT)
    {
        ok = FlagGet(FLAG_SYS_POKEMON_GET);
        if (ok)
        {
            i = ModValue(C_DESTINATION);
            Close(taskId);
            if (!i) SetWarpDestinationToLastHealLocation();
            else SetWarpDestinationToHealLocation(i);
            DoTeleportWarp();
            return;
        }
    }
    else if (action == A_DEX_SEEN || action == A_DEX_CAUGHT)
    {
        ok = FlagGet(FLAG_SYS_POKEDEX_GET);
        if (ok) for (i = 1; i <= 386; i++)
        {
            GetSetPokedexFlag(i, FLAG_SET_SEEN);
            if (action == A_DEX_CAUGHT) GetSetPokedexFlag(i, FLAG_SET_CAUGHT);
        }
    }
    else if (action == A_FLAG_SET) FlagSet(ModValue(C_FLAG));
    else if (action == A_FLAG_CLEAR) FlagClear(ModValue(C_FLAG));
    else if (action == C_WALLS) gMods.values[C_WALLS] = TRUE;
    else if (action == A_RESET) { ModDisableAll(); BuildActiveRows(); sModCursor = 0; sStatus = sDisabled; }
    if (!ok) sStatus = action == A_APPLY ? sInvalidParty : action == A_ENCOUNTER ? sNeedOverride : action == A_GIVE ? sFullParty : (action == A_TELEPORT || action == A_DEX_SEEN || action == A_DEX_CAUGHT) ? sNeedStory : sFailed;
}
static void Task_ModMenu(u8 taskId)
{
    s16 delta = 0;
    const struct ModRow *entry = &Rows()[sModCursor];
    // Opening buttons must be released before they can operate this menu.
    if (sOpeningKeys)
    {
        sOpeningKeys &= gMain.heldKeysRaw;
        return;
    }
    if (MOD_NEW(A_BUTTON | B_BUTTON | L_BUTTON | R_BUTTON | SELECT_BUTTON | START_BUTTON) || JOY_REPT(DPAD_UP | DPAD_DOWN | DPAD_LEFT | DPAD_RIGHT)) PlaySE(SE_SELECT);
    if (sConfirm != A_NONE)
    {
        if (MOD_NEW(B_BUTTON)) { sConfirm = A_NONE; Draw(); }
        else if (MOD_NEW(A_BUTTON))
        {
            u16 action = sConfirm;
            sConfirm = A_NONE;
            Action(action, taskId);
            if (gModMenuOpen) Draw();
        }
        return;
    }
    if (sBrowser < C_COUNT)
    {
        if (MOD_NEW(B_BUTTON)) { sBrowser = C_COUNT; Free(sBrowseIds); sBrowseIds = NULL; Free(sBrowseNames); sBrowseNames = NULL; Free(sBrowseKeys); sBrowseKeys = NULL; }
        else if (MOD_NEW(A_BUTTON) && sBrowseCount) { gMods.values[sBrowser] = sBrowseIds[sBrowseIndex]; if (sBrowser == C_EDIT_SPECIES) NormalizeAbility(); sBrowser = C_COUNT; Free(sBrowseIds); sBrowseIds = NULL; Free(sBrowseNames); sBrowseNames = NULL; Free(sBrowseKeys); sBrowseKeys = NULL; }
        else if (MOD_NEW(SELECT_BUTTON) || MOD_NEW(START_BUTTON))
        {
            u16 preferred = sBrowseCount ? sBrowseIds[sBrowseIndex] : ModValue(sBrowser);
            if (MOD_NEW(SELECT_BUTTON))
            {
                do { sBrowseFilter = (sBrowseFilter + 1) % BrowserFilterCount(); }
                while (sBrowser == C_HELD_ITEM && sBrowseFilter == POCKET_KEY_ITEMS);
            }
            else sBrowseAlphabetical = !sBrowseAlphabetical;
            RebuildBrowser(preferred);
        }
        else
        {
            if (!sBrowseCount) return;
            if (JOY_REPT(DPAD_UP)) delta = -1;
            if (JOY_REPT(DPAD_DOWN)) delta = 1;
            if (JOY_REPT(DPAD_LEFT) || MOD_NEW(L_BUTTON)) delta = -10;
            if (JOY_REPT(DPAD_RIGHT) || MOD_NEW(R_BUTTON)) delta = 10;
            if (!delta) return;
            if ((delta == 10 || delta == -10) && sBrowseCount <= 10)
                sBrowseIndex = delta > 0 ? sBrowseCount - 1 : 0;
            else sBrowseIndex = (sBrowseIndex + sBrowseCount + delta) % sBrowseCount;
        }
        Draw(); return;
    }
    if (MOD_NEW(B_BUTTON) || (MOD_NEW(A_BUTTON) && entry->id == A_BACK))
    {
        if (sModPage == P_MAIN) { Close(taskId); return; }
        sModPage = sModPage >= P_IV && sModPage <= P_MOVES ? P_PARTY : P_MAIN;
        sModCursor = sPageCursors[sModPage]; sStatus = NULL; Draw(); return;
    }
    if (sModPage == P_MAIN && MOD_NEW(SELECT_BUTTON) && !(gMain.heldKeysRaw & (L_BUTTON | R_BUTTON)))
    {
        sPageCursors[P_MAIN] = sModCursor;
        sModPage = P_ACTIVE; sModCursor = 0; sStatus = NULL;
        BuildActiveRows(); Draw(); return;
    }
    if (sModPage == P_ACTIVE)
    {
        if (MOD_NEW(START_BUTTON) || (MOD_NEW(A_BUTTON) && entry->id == A_RESET))
        {
            if (sActiveCount) sConfirm = A_RESET;
            else sStatus = sNoActive;
            Draw(); return;
        }
        if (MOD_NEW(A_BUTTON) && entry->id < C_COUNT)
        {
            ModDisable(entry->id);
            BuildActiveRows(); sStatus = NULL; Draw(); return;
        }
        // Reviewing active effects cannot accidentally re-enable or edit them.
        if (JOY_REPT(DPAD_LEFT | DPAD_RIGHT) || MOD_NEW(L_BUTTON | R_BUTTON)) return;
    }
    if (JOY_REPT(DPAD_UP)) delta = -1;
    if (JOY_REPT(DPAD_DOWN)) delta = 1;
    if (delta) { sModCursor = (sModCursor + RowCount() + delta) % RowCount(); sStatus = NULL; Draw(); return; }
    if (JOY_REPT(DPAD_LEFT)) delta = -1;
    if (JOY_REPT(DPAD_RIGHT)) delta = 1;
    if (MOD_NEW(L_BUTTON)) delta = -10;
    if (MOD_NEW(R_BUTTON)) delta = 10;
    if (entry->id < C_COUNT && (delta || MOD_NEW(A_BUTTON)))
    {
        u16 id = entry->id;
        u16 previous = ModValue(id);
        s32 value;
        u16 maximum = entry->max;
        sStatus = NULL;
        if (MOD_NEW(A_BUTTON) && (id == C_SPECIES || id == C_EDIT_SPECIES || id == C_ITEM || id == C_HELD_ITEM || (id >= C_MOVE1 && id <= C_MOVE4))) { Browser(id); Draw(); return; }
        if (id == C_WALLS && !ModValue(id)) { sConfirm = id; Draw(); return; }
        value = ModValue(id) + (delta ? delta : 1);
        if (entry->max == 1) value = !ModValue(id);
        else
        {
            if (id == C_PARTY) maximum = gPlayerPartyCount - 1;
            if (value < entry->min) value = delta == -1 ? maximum : entry->min;
            else if (value > maximum) value = delta == 1 || !delta ? entry->min : maximum;
        }
        if (((id == C_ITEM || id == C_HELD_ITEM) && !ValidItem(value)) || (id == C_HELD_ITEM && !ValidHeldItem(value))) { Browser(id); Draw(); return; }
        if (id == C_ABILITY && !gSpeciesInfo[NationalPokedexNumToSpecies(ModValue(C_EDIT_SPECIES))].abilities[1]) value = 0;
        gMods.values[id] = value;
        if (id == C_EDIT_SPECIES) NormalizeAbility();
        if (id == C_PARTY && value != previous && value < gPlayerPartyCount) ModLoadPartyEditor();
        Draw(); return;
    }
    if (MOD_NEW(A_BUTTON))
    {
        if (entry->id >= A_PAGE)
        {
            if (entry->id == A_PAGE+P_PARTY)
            {
                if (!gPlayerPartyCount) { sStatus = sFailed; Draw(); return; }
                gMods.values[C_PARTY] = 0;
                ModLoadPartyEditor();
            }
            sPageCursors[sModPage] = sModCursor;
            sModPage = entry->id-A_PAGE; sModCursor = 0; sStatus = NULL;
            if (sModPage == P_ACTIVE) BuildActiveRows();
        }
        else if (entry->id == A_GIVE || entry->id == A_APPLY || entry->id == A_TELEPORT || entry->id == A_DEX_SEEN || entry->id == A_DEX_CAUGHT || entry->id == A_FLAG_SET || entry->id == A_FLAG_CLEAR) sConfirm = entry->id;
        else Action(entry->id, taskId);
        if (gModMenuOpen) Draw();
    }
}
bool8 ModOpenMenu(void)
{
    u8 task;
    if (gModMenuOpen || gPaletteFade.active || MenuHelpers_IsLinkActive() || InUnionRoom() || QL_IS_PLAYBACK_STATE || !walkrun_is_standing_still()) return FALSE;
    if (FindTaskIdByFunc(Task_ModMenu) != TASK_NONE) return FALSE;
    task = CreateTask(Task_ModMenu, 80);
    if (task == TASK_NONE) return FALSE;
    sWindow = AddWindow(&sWindowTemplate);
    if (sWindow == WINDOW_NONE) { DestroyTask(task); return FALSE; }
    FreezeObjectEvents();
    HandleEnforcedLookDirectionOnPlayerStopMoving();
    StopPlayerAvatar();
    LockPlayerFieldControls();
    LoadStdWindowFrameGfx();
    DrawStdWindowFrame(sWindow, FALSE);
    PutWindowTilemap(sWindow);
    if (!sStockCount) {
        sStock[0] = ITEM_POTION; sStock[1] = ITEM_POKE_BALL;
        sStock[2] = ITEM_ANTIDOTE; sStock[3] = ITEM_REPEL;
        sStock[4] = ITEM_NONE; sStockCount = 4;
    }
    CpuFill16(0, sPageCursors, sizeof(sPageCursors));
    sModPage = P_MAIN; sModCursor = 0; sBrowser = C_COUNT; sConfirm = A_NONE; sStatus = NULL;
    gModMenuOpen = TRUE;
    sOpeningKeys = gMain.heldKeysRaw;
    PlaySE(SE_WIN_OPEN);
    Draw();
    return TRUE;
}
#endif
