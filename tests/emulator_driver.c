// Small deterministic mGBA RPC runner. No GUI or emulator mod codes.
#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
static void quietLog(struct mLogger *l, int category, enum mLogLevel level, const char *format, va_list args) {
    (void)l; (void)category;
    if (level == mLOG_FATAL) { vfprintf(stderr, format, args); fputc('\n', stderr); exit(1); }
}
static struct mLogger logger = { quietLog, NULL };
static color_t pixels[240*160];
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    mLogSetDefaultLogger(&logger);
    struct mCore *core = mCoreFind(argv[1]);
    if (!core || !core->init(core)) { fputs("mGBA initialization failed\n", stderr); return 1; }
    mCoreInitConfig(core, "native-mod-tests");
    core->opts.useBios = false;
    core->opts.skipBios = true;
    core->opts.audioSync = false;
    core->opts.videoSync = false;
    core->setVideoBuffer(core, pixels, 240);
    core->setAudioBufferSize(core, 1024);
    if (!mCoreLoadFile(core, argv[1])) return 1;
    // Fresh 128 KiB flash cartridge for every independent test process.
    unsigned char *blank = malloc(128 * 1024);
    memset(blank, 0xFF, 128 * 1024);
    struct VFile *save = VFileMemChunk(blank, 128 * 1024);
    free(blank);
    if (!save || !core->loadSave(core, save)) return 1;
    core->reset(core);
    setvbuf(stdout, NULL, _IOLBF, 0);
    puts("READY");
    char line[4096], path[2048];
    unsigned a,b;
    while (fgets(line, sizeof(line), stdin)) {
        if (sscanf(line, "F %u %u", &a, &b) == 2) {
            core->setKeys(core, a);
            for (unsigned i=0; i<b; i++) core->runFrame(core);
            printf("OK %u\n", core->frameCounter(core));
        } else if (sscanf(line, "R %x %u", &a, &b) == 2) {
            for (unsigned i=0; i<b; i++) printf("%02x",core->busRead8(core,a+i));
            puts("");
        } else if (line[0] == 'S' && line[1] == ' ' && sscanf(line,"S %2047s",path)==1) {
            FILE *f=fopen(path,"wb");
            if(!f) return 1;
            fprintf(f,"P6\n240 160\n255\n");
            for(unsigned i=0;i<240*160;i++) {
                unsigned char rgb[3]={pixels[i]&255,(pixels[i]>>8)&255,(pixels[i]>>16)&255};
                fwrite(rgb,1,3,f);
            }
            fclose(f); puts("OK");
        } else if (sscanf(line,"SAVE %2047s",path)==1) {
            size_t size=core->stateSize(core);void *data=malloc(size);
            if(!core->saveState(core,data)) return 1;
            FILE*f=fopen(path,"wb"); if(!f) return 1;fwrite(data,1,size,f);fclose(f);free(data);puts("OK");
        } else if (sscanf(line,"LOAD %2047s",path)==1) {
            size_t size=core->stateSize(core);void *data=malloc(size);FILE*f=fopen(path,"rb");
            if(!f || fread(data,1,size,f)!=size) return 1;fclose(f);
            if(!core->loadState(core,data))return 1;free(data);puts("OK");
        } else if (sscanf(line,"DUMP %2047s",path)==1) {
            void *data=NULL; size_t size=core->savedataClone(core,&data);
            FILE*f=fopen(path,"wb");if(!f || !data || !size)return 1;
            fwrite(data,1,size,f);fclose(f);free(data);puts("OK");
        } else if (strncmp(line,"RESET",5)==0) { core->reset(core); puts("OK"); }
        else if (line[0]=='Q') break;
        else { fputs("Invalid command\n",stderr);return 2; }
    }
    mCoreConfigDeinit(&core->config);
    core->deinit(core);
    return 0;
}
