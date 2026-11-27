from os.path import isdir, isfile, join
from os import makedirs
from pathlib import Path
import sys
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-picosdk")
assert isdir(FRAMEWORK_DIR)

mcu = "rp2350" if "rp2350" in board.get('build.mcu') else "rp2040"
is_rp2350 = mcu == "rp2350" # could be ARM or RISC-V
is_riscv = board.get('build.mcu') == "rp2350-riscv"
rp2_variant_dir = join(FRAMEWORK_DIR, "src", mcu)
# load known mappings
known_mappings: dict[str, str] = {
    # exact matches
    "0xcb_helios": "0xcb_helios.h",
    "adafruit_kb2040": "adafruit_kb2040.h",
    "arduino_nano_connect": "arduino_nano_rp2040_connect.h",
    "cytron_maker_pi_rp2040": "cytron_maker_pi_rp2040.h",
    "generic_rp2350": "pico2.h",
    "melopero_shake_rp2040": "melopero_shake_rp2040.h",
    "newsan_archi": "archi.h",
    "pimoroni_plasma2350w": "pimoroni_plasma2350_w.h",
    "vccgnd_yd_rp2040": "vcc-gnd_yd-rp2040_16m.h",
    "weact_rp2350b": "weact_studio_rp2350b_core.h",
    "nullbits_bit_c_pro": "nullbits_bit_c_pro.h",
    "pico": "pico.h",
    "pimoroni_pga2040": "pimoroni_pga2040.h",
    "pimoroni_pga2350": "pimoroni_pga2350.h",
    "pimoroni_plasma2040": "pimoroni_plasma2040.h",
    "pimoroni_plasma2350": "pimoroni_plasma2350.h",
    "pimoroni_servo2040": "pimoroni_servo2040.h",
    "pimoroni_tiny2040": "pimoroni_tiny2040_2mb.h",
    "pimoroni_tiny2350": "pimoroni_tiny2350.h",
    "rpipico": "pico.h",
    "rpipico2": "pico2.h",
    "seeed_xiao_rp2040": "seeed_xiao_rp2040.h",
    "seeed_xiao_rp2350": "seeed_xiao_rp2350.h",
    "solderparty_rp2040_stamp": "solderparty_rp2040_stamp.h",
    "solderparty_rp2350_stamp": "solderparty_rp2350_stamp.h",
    "solderparty_rp2350_stamp_xl": "solderparty_rp2350_stamp_xl.h",
    "sparkfun_iotredboard_rp2350": "sparkfun_iotredboard_rp2350.h",
    "sparkfun_xrp_controller": "sparkfun_xrp_controller.h",
    "sparkfun_xrp_controller_beta": "pico_w.h",
    "waveshare_rp2040_matrix": "waveshare_rp2040_matrix.h",
    "waveshare_rp2040_one": "waveshare_rp2040_one.h",
    "waveshare_rp2040_pizero": "waveshare_rp2040_pizero.h",
    "waveshare_rp2040_plus_16mb": "waveshare_rp2040_plus_16mb.h",
    "waveshare_rp2040_plus_4mb": "waveshare_rp2040_plus_4mb.h",
    "waveshare_rp2040_zero": "waveshare_rp2040_zero.h",
    "waveshare_rp2350_zero": "waveshare_rp2350_zero.h",
    # suggested matches and manually checked /modified
    "adafruit_feather": "adafruit_feather_rp2040.h",
    "adafruit_feather_adalogger": "adafruit_feather_rp2040_adalogger.h",
    "adafruit_feather_can": "adafruit_feather_rp2040.h",
    "adafruit_feather_dvi": "adafruit_feather_rp2040.h",
    "adafruit_feather_prop_maker": "adafruit_feather_rp2040",
    "adafruit_feather_rfm": "adafruit_feather_rp2040.h",
    "adafruit_feather_rp2350_adalogger": "adafruit_feather_rp2350.h",
    "adafruit_feather_rp2350_hstx": "adafruit_feather_rp2350.h",
    "adafruit_feather_scorpio": "adafruit_feather_rp2040.h",
    "adafruit_feather_thinkink": "adafruit_feather_rp2040.h",
    "adafruit_feather_usb_host": "adafruit_feather_rp2040_usb_host.h",
    "adafruit_fruitjam": "adafruit_fruit_jam.h",
    "adafruit_itsybitsy": "adafruit_itsybitsy_rp2040.h",
    "adafruit_macropad2040": "adafruit_macropad_rp2040.h",
    "adafruit_qtpy": "adafruit_qtpy_rp2040.h",
    "adafruit_trinkeyrp2040qt": "adafruit_trinkey_qt2040.h",
    "challenger_2350_bconnect": "ilabs_challenger_rp2350_bconnect.h",
    "challenger_2350_wifi6_ble5": "ilabs_challenger_rp2350_wifi_ble.h",
    "cytron_maker_nano_rp2040": "cytron_maker_pi_rp2040.h",
    "cytron_maker_uno_rp2040": "cytron_maker_pi_rp2040.h",
    "datanoisetv_picoadk" : "datanoisetv_rp2040_dsp.h",
    "datanoisetv_picoadk_v2": "datanoisetv_rp2350_dsp.h",
    "generic": "pico.h",
    "nanorp2040connect": "arduino_nano_rp2040_connect.h",
    "olimex_pico2xl": "olimex_rp2350_xl.h",
    "olimex_pico2xxl": "olimex_rp2350_xxl.h",
    "pimoroni_pico_plus_2": "pimoroni_pico_plus2_rp2350.h",
    "pimoroni_pico_plus_2w": "pimoroni_pico_plus2_w_rp2350.h",
    "rpipico2w": "pico2_w.h",
    "rpipicow": "pico_w.h",
    "sparkfun_iotnode_lorawanrp2350": "sparkfun_iotnode_lorawan_rp2350.h",
    "sparkfun_micromodrp2040": "sparkfun_micromod.h",
    "sparkfun_promicrorp2040": "sparkfun_promicro.h",
    "sparkfun_promicrorp2350": "sparkfun_promicro_rp2350.h",
    "sparkfun_thingplusrp2040": "sparkfun_thingplus.h",
    "sparkfun_thingplusrp2350": "sparkfun_thingplus_rp2350.h",
    "waveshare_rp2040_lcd_0_96": "waveshare_rp2040_lcd_0.96.h",
    "waveshare_rp2040_lcd_1_28": "waveshare_rp2040_lcd_1.28.h",
    "waveshare_rp2040_plus": "waveshare_rp2040_plus_4mb.h",
    "waveshare_rp2350_lcd_0_96": "waveshare_rp2350_lcd_0.96.h",
    "waveshare_rp2350_plus": "waveshare_rp2350_plus_4mb.h",
    "wiznet_5100s_evb_pico": "wiznet_w5100s_evb_pico.h",
    "wiznet_5100s_evb_pico2": "wiznet_w5100s_evb_pico2.h"
}

# check if the board JSON or the platformio.ini is dictating the use of a specific board header
if board.get("build.picosdk.board_header", "") != "":
    rp2_board_header = board.get("build.picosdk.board_header")
    print("Using specified Pico-SDK board header: %s" % rp2_board_header)
else:
    # is there a known mapping for this board?
    sdk_boards_dir = join(FRAMEWORK_DIR, "src", "boards", "include", "boards")
    # otherwise, the SDK may have a header with the same name as the board or its variant
    same_name_header = next((
        "%s.h" % name for name in (board.id, board.get("build.variant", ""))
        if name and isfile(join(sdk_boards_dir, "%s.h" % name))
    ), None)
    if board.id in known_mappings:
        rp2_board_header = known_mappings[board.id]
        print("Using known Pico-SDK board header for %s: %s" % (board.id, rp2_board_header))
    elif same_name_header:
        rp2_board_header = same_name_header
        print("Using Pico-SDK board header for %s: %s" % (board.id, rp2_board_header))
    else:
        # fallback to either pico.h or pico2.h depending on rp2040 or rp2350
        rp2_board_header = "pico2.h" if is_rp2350 else "pico.h"
        print("[WARN] No known Pico-SDK board header for %s, falling back to '%s'. Set one using 'board_build.picosdk.board_header = ..' in the platformio.ini" % (board.id, rp2_board_header))

# board header file must exist at this point.
if not isfile(join(FRAMEWORK_DIR, "src", "boards", "include", "boards", rp2_board_header)):
    sys.stderr.write("Could not find board header file %s in the Pico-SDK, aborting.\n" % rp2_board_header)
    env.Exit(-1)

# include basic settings
env.SConscript("_bare.py")

# process .pio files of user NOW
env.SConscript("_build_pioasm.py")

# for processing .pio files of the Pico-SDK. Build and depend only on C files within the module
def preprocess_pio_sources(src_dir):
    """Scan a folder recursively for .pio files and generate .pio.h in build_dir/generated."""
    from pathlib import Path
    pio_sources = list(Path(src_dir).rglob("*.pio"))
    headers = []

    # place all generated headers in $BUILD_DIR/generated
    genned_dir = Path(env.subst("$BUILD_DIR")) / "generated"
    genned_dir.mkdir(parents=True, exist_ok=True)

    for src in pio_sources:
        target = genned_dir / src.with_suffix(".pio.h").name
        headers.append(env.PioToPioH(str(target), str(src)))
    return headers

# generate version file
# .. actually unmutable, so pre-generatable
# generate config_autogen.h
# filled with the content of the board header file, and "rename_exceptions.h"
def gen_config_autogen(target_base_dir, board_hdr):
    try:
        makedirs(join(target_base_dir, "pico"), exist_ok=True)
    except Exception as exc:
        sys.stderr.write("Failed to create folder for automatic header file generation: %s\n" % repr(exc))
        env.Exit(-1)
    autogen_content_paths = [
        join(FRAMEWORK_DIR, "src", "boards", "include", "boards", board_hdr),
        join(FRAMEWORK_DIR, "src" , "rp2_common", "cmsis", "include", "cmsis", "rename_exceptions.h")
    ]
    # read content
    autogen_content = ""
    for file in autogen_content_paths:
        p = Path(file)
        if not p.exists():
            sys.stderr.write("Automatic header file generation failed: %s not found.\n" % file)
            env.Exit(-1)
        autogen_content += p.read_text()
    # write content back to disk
    Path(join(target_base_dir), "pico", "config_autogen.h").write_text(autogen_content)

genned_dir = join(env.subst("$PROJECT_BUILD_DIR"), env.subst("$PIOENV"), "generated")
gen_config_autogen(genned_dir, rp2_board_header)

env.Append(
    #ASFLAGS=[f for f in ccflags if isinstance(f, str) and f.startswith("-m")],
    #ASPPFLAGS=["-x", "assembler-with-cpp"],
    #CFLAGS=sorted(list(cflags - ccflags)),
    #CCFLAGS=sorted(list(ccflags)),
    CPPDEFINES=[
        ("PICO_RP2350" if is_rp2350 else "PICO_RP2040", 1),
        ("PICO_RISCV", int(is_riscv)),
        ("PICO_ARM", int(not is_riscv)),
        ("PICO_CMSIS_DEVICE", "\"%s\"" % mcu.upper()),
        ("PICO_DEFAULT_FLASH_SIZE_BYTES", 2 * 1024 * 1024),
        # default SDK defines for on-hardware build
        ("PICO_ON_DEVICE", "1"),
        ("PICO_NO_HARDWARE", "0"),
        ("PICO_BUILD", "1"),
        ("LIB_CMSIS_CORE", 1)
    ],
    CPPPATH=[
        # for version.h, one-time generated
        join(FRAMEWORK_DIR, "generated"),
        # this is 'genned_dir', but late-evaluated
        "$PROJECT_BUILD_DIR/$PIOENV/generated",
        
        # Boards Directory
        join(FRAMEWORK_DIR, "src", "boards", "include"),
        
        # Common for all (host, rp2040, rp2350)
        join(FRAMEWORK_DIR, "src", "common", "boot_picobin_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "boot_picoboot_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "boot_uf2_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_base_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_usb_reset_interface_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_bit_ops_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_binary_info", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_divider_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_sync", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_time", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_util", "include"),
        join(FRAMEWORK_DIR, "src", "common", "pico_stdlib_headers", "include"),
        join(FRAMEWORK_DIR, "src", "common", "hardware_claim", "include"),

        # variant specific
        join(rp2_variant_dir, "pico_platform", "include"),
        join(rp2_variant_dir, "hardware_regs", "include"),
        join(rp2_variant_dir, "hardware_structs", "include"),
        join(rp2_variant_dir, "boot_stage2", "include"),

        # common for rp2040, rp2350
        join(FRAMEWORK_DIR, "src", "rp2_common", "boot_bootrom_headers", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_adc", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_base", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_boot_lock", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_clocks", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_dcp", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_divider", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_dma", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_exception", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_flash", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_gpio", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_hazard3", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_i2c", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_interp", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_irq", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_pio", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_pll", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_pwm", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_resets", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_rcp", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_riscv", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_riscv_platform_timer", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_rtc", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_spi", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_sync_spin_lock", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_sync", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_ticks", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_timer", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_uart", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_vreg", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_watchdog", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_xosc", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_xip_cache", "include"),

        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_aon_timer", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_atomic", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_bit_ops", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_bootrom", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_bootsel_via_double_reset", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_divider", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_double", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_flash", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_float", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_int64_ops", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_malloc", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_mem_ops", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_multicore", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_common", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_compiler", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_panic", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_sections", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_printf", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_rand", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_status_led", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_rtt", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_rtt", "SEGGER", "RTT"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_semihosting", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_uart", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_thread_local", "include"), # SDK >= 2.3.0
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_unique_id", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_usb_reset", "include"), # SDK >= 2.3.0
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_rosc", "include"), # SDK >= 2.3.0
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_psram", "include"), # SDK >= 2.3.0, RP2350 only
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_low_power", "include"), # SDK >= 2.3.0
        # CMSIS only for ARM
        join(FRAMEWORK_DIR, "src", "rp2_common", "cmsis", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "cmsis", "stub", "CMSIS", "Core", "Include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "cmsis", "stub", "CMSIS", "Device", mcu.upper(), "Include"),

        join(FRAMEWORK_DIR, "src", "rp2_common", "tinyusb", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_usb", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_i2c_slave", "include"),
        # Network
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_async_context", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_btstack", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cyw43_driver", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_lwip", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cyw43_arch", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_mbedtls", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_time_adapter", "include"),

        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_crt0", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_clib_interface", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cxx_options", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_standard_binary_info", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_standard_link", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_fix", "rp2040_usb_device_enumeration", "include"),

        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_runtime_init", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_runtime", "include"),
        
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdlib", "include"),

        join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "asminclude"),
        join(FRAMEWORK_DIR, "src", mcu, "pico_platform", "include"),
    ],
    #CXXFLAGS=sorted(list(cxxflags - ccflags)),
    LIBPATH=[
        # will be needed for linker script
        genned_dir
    #    os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant")),
    #    os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "libs")
    ],

    LINKFLAGS=[
        "$BUILD_DIR/boot2.S"
    ],
    #LIBSOURCE_DIRS=[os.path.join(FRAMEWORK_DIR, "libraries")],
    #LIBS=["mbed"]
)

cpp_defines = env.Flatten(env.get("CPPDEFINES", []))

def get_define_value(name, default=None):
    # value of a -D macro from CPPDEFINES (build_flags, board), or default if not defined
    for d in env.get("CPPDEFINES", []):
        if isinstance(d, (tuple, list)) and len(d) >= 2 and d[0] == name:
            return str(d[1])
        if d == name:
            return "1"
    return default

flags = []
# configure default but overridable defines
# todo figure this out from arduino-pico info? :))
if not "PICO_DEFAULT_BOOT_STAGE2_FILE" in cpp_defines:
    pass
if not "PICO_DEFAULT_BOOT_STAGE2" in cpp_defines:
    pass
use_multicore = "PIO_NO_MULTICORE" not in cpp_defines
if use_multicore:
    # PICO_MULTICORE_ENABLED is the name of the SDK's Bazel config option. No SDK source reads it,
    # but it's kept for compatibility with user code that may check it. What the SDK actually reads
    # is LIB_PICO_MULTICORE (e.g. pico/flash.h, pico/malloc.h, async_context_threadsafe_background.h),
    # which is emitted below together with the other LIB_<library> defines.
    flags.append(("PICO_MULTICORE_ENABLED", 1))
# pico_malloc wraps malloc/calloc/realloc/free and makes them multicore-safe (mutex), like in a CMake build.
use_pico_malloc = "PIO_NO_PICO_MALLOC" not in cpp_defines
# float / double / divider / int64_ops / bit_ops / mem_ops implementations: see "runtime support libraries" below
# printf implementation: pico or compiler
printf_impl = get_define_value("PIO_DEFAULT_PRINTF_IMPL", "pico")
if not "PIO_NO_BINARY_INFO" in cpp_defines:
    flags.append(("PICO_BINARY_INFO_ENABLED", 1))

if not "PIO_USE_DEFAULT_PAGE_SIZE" in cpp_defines:
    env.Append(LINKFLAGS=["-Wl,-z,max-page-size=4096"])

timeout = get_define_value("PIO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS", 0)
flags.append(("PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS", timeout))

# default to USB stdio if nothing else defined (or explicitly disabled)
# (only the stdio selection flags count, not options like PIO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS)
stdio_select_flags = ("PIO_STDIO_USB", "PIO_STDIO_UART", "PIO_STDIO_SEMIHOSTING", "PIO_STDIO_RTT", "PIO_STDIO_NONE")
if not any(flag in cpp_defines for flag in stdio_select_flags):
    print("No stdio implementation defined, defaulting to USB.")
    cpp_defines.append("PIO_STDIO_USB")

is_cyw43_board = any(str(flag).startswith("PICO_CYW43_SUPPORTED") for flag in cpp_defines)

# ToDo: this may also be triggered by other functions or configs.
def build_tinyusb():
    # setup build to include TinyUSB component
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "lib", "tinyusb", "src"),
        ],
        CPPDEFINES=[
            ("CFG_TUSB_DEBUG", 0),
            ("CFG_TUSB_MCU", "OPT_MCU_RP2040"),
            ("CFG_TUSB_OS", "OPT_OS_PICO"),
            ("PICO_RP2040_USB_DEVICE_UFRAME_FIX", 1),
            ("PICO_RP2040_USB_DEVICE_ENUMERATION_FIX", 1),
        ]
    )
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKTinyUSB"),
        join(FRAMEWORK_DIR, join(FRAMEWORK_DIR, "lib", "tinyusb", "src")),
        "+<*> -<portable> +<portable/raspberrypi>"
    )
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKPicoFix"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_fix")
    )

def configure_printf_impl():
    # remap PIO macros to macros used in the SDK
    remap_dict = {
        "PIO_STDIO_USB": "LIB_PICO_STDIO_USB",
        "PIO_STDIO_UART": "LIB_PICO_STDIO_UART",
        "PIO_STDIO_SEMIHOSTING": "LIB_PICO_STDIO_SEMIHOSTING",
        "PIO_STDIO_RTT": "LIB_PICO_STDIO_RTT"
    }
    for key in remap_dict:
        if key in cpp_defines:
            flags.append(remap_dict[key])
            if "LIB_PICO_STDIO" not in flags:
                flags.append("LIB_PICO_STDIO")
    # we definitely need tinyusb for this
    if "LIB_PICO_STDIO_USB" in flags:
        build_tinyusb()
    # in any case, when stdio_usb_descriptors.c is compiled, 
    # it will complain if USBD_MAX_POWER_MA is already defined.
    # so, let's remove it if it exists.
    if "USBD_MAX_POWER_MA" in cpp_defines:
        new_defines = env["CPPDEFINES"].copy()
        # remove USBD_MAX_POWER_MA tuple
        new_defines = [d for d in new_defines if not (isinstance(d, tuple) and d[0] == "USBD_MAX_POWER_MA")]
        env.Replace(CPPDEFINES=new_defines)

def compile_gatt_files():
    """Compile the project's .gatt files to $BUILD_DIR/generated/<name>.h (like pico_btstack_make_gatt_header)."""
    compile_gatt = join(FRAMEWORK_DIR, "lib", "btstack", "tool", "compile_gatt.py")
    for gatt_file in Path(env.subst("$PROJECT_SRC_DIR")).rglob("*.gatt"):
        header_file = Path(genned_dir) / gatt_file.with_suffix(".h").name
        if header_file.exists() and header_file.stat().st_mtime >= gatt_file.stat().st_mtime:
            continue
        action = env.VerboseAction(
            '"$PYTHONEXE" "%s" "%s" "%s"' % (compile_gatt, str(gatt_file), str(header_file)),
            "Generating %s" % str(header_file))
        if env.Execute(action) != 0:
            sys.stderr.write("Failed to compile GATT file %s\n" % str(gatt_file))
            env.Exit(1)

def build_btstack():
    # opt-in BLE support: pico_btstack_ble + pico_btstack_cyw43 in a CMake build.
    # The project has to provide a btstack_config.h, e.g. in its include/ folder.
    btstack_dir = join(FRAMEWORK_DIR, "lib", "btstack")
    env.Append(CPPPATH=[
        btstack_dir,
        join(btstack_dir, "3rd-party", "md5"),
        join(btstack_dir, "3rd-party", "yxml"),
        join(btstack_dir, "3rd-party", "rijndael"),
        join(btstack_dir, "3rd-party", "micro-ecc"),
        join(btstack_dir, "3rd-party", "segger-rtt"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_btstack", "include"),
    ], CPPDEFINES=[
        ("ENABLE_BLE", 1),
        ("CYW43_ENABLE_BLUETOOTH", 1),
        ("LIB_PICO_BTSTACK_BLE", 1),
        ("LIB_PICO_BTSTACK_CYW43", 1),
        ("LIB_PICO_BTSTACK_FLASH_BANK", 1),
    ])
    # pico_btstack_base
    base_src = [
        "3rd-party/micro-ecc/uECC.c",
        "3rd-party/rijndael/rijndael.c",
        "3rd-party/segger-rtt/SEGGER_RTT_printf.c",
        "platform/embedded/btstack_tlv_flash_bank.c",
        "platform/embedded/hci_dump_embedded_stdout.c",
        "platform/embedded/hci_dump_segger_rtt_stdout.c",
        "src/ad_parser.c", "src/btstack_audio.c", "src/btstack_base64_decoder.c", "src/btstack_crypto.c",
        "src/btstack_hid.c", "src/btstack_hid_parser.c", "src/btstack_linked_list.c", "src/btstack_memory.c",
        "src/btstack_memory_pool.c", "src/btstack_resample.c", "src/btstack_ring_buffer.c", "src/btstack_run_loop.c",
        "src/btstack_run_loop_base.c", "src/btstack_slip.c", "src/btstack_tlv.c", "src/btstack_tlv_none.c",
        "src/btstack_util.c", "src/hci.c", "src/hci_cmd.c", "src/hci_dump.c", "src/hci_event.c", "src/l2cap.c",
        "src/l2cap_signaling.c", "3rd-party/md5/md5.c", "3rd-party/yxml/yxml.c",
    ]
    # SEGGER_RTT.c is already part of pico_stdio_rtt
    if "LIB_PICO_STDIO_RTT" not in flags:
        base_src.append("3rd-party/segger-rtt/SEGGER_RTT.c")
    # pico_btstack_ble
    ble_src = [
        "src/ble/att_db.c", "src/ble/att_db_util.c", "src/ble/att_dispatch.c", "src/ble/att_server.c",
        "src/ble/gatt-service/battery_service_server.c", "src/ble/gatt-service/battery_service_client.c",
        "src/ble/gatt-service/cycling_power_service_server.c",
        "src/ble/gatt-service/cycling_speed_and_cadence_service_server.c",
        "src/ble/gatt-service/device_information_service_server.c",
        "src/ble/gatt-service/device_information_service_client.c",
        "src/ble/gatt-service/heart_rate_service_server.c", "src/ble/gatt-service/hids_device.c",
        "src/ble/gatt-service/nordic_spp_service_server.c", "src/ble/gatt-service/ublox_spp_service_server.c",
        "src/ble/gatt-service/ancs_client.c", "src/ble/gatt_client.c", "src/ble/le_device_db_memory.c",
        "src/ble/le_device_db_tlv.c", "src/ble/sm.c",
    ]
    if isfile(join(btstack_dir, "src", "hci_event_builder.c")):
        ble_src.append("src/hci_event_builder.c")
    if isfile(join(btstack_dir, "src", "ble", "gatt-service", "hids_host.c")):
        ble_src += ["src/ble/gatt-service/hids_host.c", "src/ble/gatt_service_client.c"]
    else:
        ble_src.append("src/ble/gatt-service/hids_client.c")
    env.BuildSources(
        join("$BUILD_DIR", "BTstack"),
        btstack_dir,
        "-<*> " + " ".join("+<%s>" % f for f in base_src + ble_src)
    )
    # pico_btstack_flash_bank, pico_btstack_run_loop_async_context and btstack_stdin_pico.c (pico_btstack_base)
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKBTstack"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_btstack"),
        "-<*> +<btstack_flash_bank.c> +<btstack_run_loop_async_context.c> +<btstack_stdin_pico.c>"
    )
    compile_gatt_files()

def build_cyw43_arch():
    # not needed for non-CYW43 boards
    if not is_cyw43_board:
        return
    # -D CYW43_LWIP=0 is what pico_cyw43_arch_none does: WiFi driver without lwIP (e.g. for BLE only)
    use_lwip = get_define_value("CYW43_LWIP", "1") != "0"
    use_btstack = "PIO_USE_BTSTACK_BLE" in cpp_defines
    env.Append(CPPPATH=[
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cyw43_arch", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cyw43_driver", "include"),
        join(FRAMEWORK_DIR, "lib", "btstack", "src"),
        join(FRAMEWORK_DIR, "lib", "btstack", "platform", "embedded"),
        join(FRAMEWORK_DIR, "lib", "cyw43-driver", "src"),
        join(FRAMEWORK_DIR, "lib", "cyw43-driver", "firmware"),
        join(FRAMEWORK_DIR, "lib", "lwip", "src", "include"),
        # The project's include/ folder comes first, so that an lwipopts.h (and mbedtls_config.h) from the
        # project is used for the SDK / lwIP sources too, not only for the project's own sources.
        # PlatformIO itself only adds it to the environment that builds the project sources.
        "$PROJECT_INCLUDE_DIR",
        # fallback lwipopts.h if the project doesn't provide one
        join(FRAMEWORK_DIR, "lib", "btstack", "platform", "lwip", "port")
    ], CPPDEFINES=[
        ("PICO_CYW43_ARCH_THREADSAFE_BACKGROUND", "1"),
    ])
    # build pico_cyw43_arch
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKCyw43Arch"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cyw43_arch"),
        "-<*> +<cyw43_arch.c> +<cyw43_arch_threadsafe_background.c>"
    )
    # build rp2_common/pico_async_context
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKAsyncContext"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_async_context"),
        "-<*> +<async_context_base.c> +<async_context_threadsafe_background.c>"
    )
    # build pico_cyw43_driver, has .pio file
    comp_build_dir = join("$BUILD_DIR", "PicoSDKPicoCYW43Driver")
    comp_src_dir = join(FRAMEWORK_DIR, "src", "rp2_common", "pico_cyw43_driver")
    src_filter = "+<*.c> -<*.S> -<*.s>"
    if use_btstack:
        # cybt_shared_bus: the Bluetooth part of the WiFi chip's bus driver
        src_filter += " +<cybt_shared_bus/*.c>"
    else:
        # pico_btstack_cyw43 / pico_btstack_hci_transport_cyw43, only needed if btstack is on
        src_filter += " -<btstack_cyw43.c> -<btstack_hci_transport_cyw43.c> -<btstack_chipset_cyw43.c>"
    pio_headers = preprocess_pio_sources(comp_src_dir)
    c_nodes = env.BuildSources(comp_build_dir, comp_src_dir, src_filter)
    env.Depends(c_nodes, pio_headers)
    if use_btstack:
        build_btstack()

    # build lib/cyw43-driver, regularly.
    env.BuildSources(
        join("$BUILD_DIR", "Cyw43Driver"),
        join(FRAMEWORK_DIR, "lib", "cyw43-driver", "src"),
        "+<*> -<*.S> -<*.s> -<cyw43_spi.c>" # already provided by more specialized cyw43_bus_pio_spi.c
    )

    if not use_lwip:
        return

    # build rp2_common / pico_lwip
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKLwip"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_lwip"),
        "-<*> +<lwip_nosys.c>"
    )

    # build lib/lwip.
    lwip_src_filter = "-<*> +<api> +<core> +<port> +<netif/ethernet.c>"
    env.BuildSources(
        join("$BUILD_DIR", "Lwip"),
        join(FRAMEWORK_DIR, "lib", "lwip", "src"),
        lwip_src_filter
    )


def build_mbedtls():
    # opt-in, like linking pico_mbedtls (and pico_lwip_mbedtls) in a CMake build.
    # The project has to provide a mbedtls_config.h, e.g. in its include/ folder.
    if "PIO_USE_MBEDTLS" not in cpp_defines:
        return
    mbedtls_dir = join(FRAMEWORK_DIR, "lib", "mbedtls")
    if isfile(join(FRAMEWORK_DIR, "src", "rp2_common", "pico_mbedtls", "include", "pico_mbedtls_config.h")):
        # SDK >= 2.0 with mbedtls 3.x: wrapper that includes the project's mbedtls_config.h
        mbedtls_config_file = "pico_mbedtls_config.h"
    else:
        mbedtls_config_file = "mbedtls_config.h"
    env.AppendUnique(CPPPATH=[
        "$PROJECT_INCLUDE_DIR",
        join(mbedtls_dir, "include"),
        join(mbedtls_dir, "library"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_mbedtls", "include"),
    ])
    env.Append(CPPDEFINES=[("MBEDTLS_CONFIG_FILE", "\\\"%s\\\"" % mbedtls_config_file)])
    # pico_mbedtls_crypto + pico_mbedtls_x509 + pico_mbedtls_tls: that's all of library/*.c
    env.BuildSources(
        join("$BUILD_DIR", "MbedTLS"),
        join(mbedtls_dir, "library"),
        "-<*> +<*.c>"
    )
    # pico_mbedtls: hardware entropy, time and (RP2350) SHA-256 acceleration glue
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKMbedTLS"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_mbedtls"),
        "-<*> +<pico_mbedtls.c>"
    )
    if not is_cyw43_board or get_define_value("CYW43_LWIP", "1") == "0":
        return
    # pico_lwip_mbedtls: TLS for lwIP's altcp API
    env.Append(CPPPATH=[join(FRAMEWORK_DIR, "lib", "lwip", "src", "apps", "altcp_tls")])
    env.BuildSources(
        join("$BUILD_DIR", "LwipAltcpTls"),
        join(FRAMEWORK_DIR, "lib", "lwip", "src", "apps", "altcp_tls"),
        "-<*> +<altcp_tls_mbedtls_mem.c>"
    )
    # lwIP's own altcp_tls_mbedtls.c doesn't support mbedtls 3.x, the SDK ships a patched one
    if isfile(join(FRAMEWORK_DIR, "src", "rp2_common", "pico_lwip", "altcp_tls_mbedtls.c")) \
            and isfile(join(mbedtls_dir, "library", "ssl_client.c")):
        env.BuildSources(
            join("$BUILD_DIR", "PicoSDKLwipMbedTLS"),
            join(FRAMEWORK_DIR, "src", "rp2_common", "pico_lwip"),
            "-<*> +<altcp_tls_mbedtls.c>"
        )
    else:
        env.BuildSources(
            join("$BUILD_DIR", "LwipAltcpTlsMbedTLS"),
            join(FRAMEWORK_DIR, "lib", "lwip", "src", "apps", "altcp_tls"),
            "-<*> +<altcp_tls_mbedtls.c>"
        )

configure_printf_impl()
build_cyw43_arch()
build_mbedtls()

# default false, only mentioned here:
# PICO_CXX_ENABLE_EXCEPTIONS
# PICO_CXX_ENABLE_RTTI
# PICO_CXX_ENABLE_CXA_ATEXIT
env.Append(CPPDEFINES=flags)


# configure linker script (memmap_default)
# this will want a file called pico_flash_region.ld:
flash_region = "FLASH(rx) : ORIGIN = 0x10000000, LENGTH = %s\n" % str(board.get("upload.maximum_size"))
Path(join(genned_dir, "pico_flash_region.ld")).write_text(flash_region)

# SDK >= 2.3.0 moved the linker scripts to src/<mcu>/pico_platform and split them into
# INCLUDE'd fragments, found via the linker search path. Older SDKs have a monolithic script in pico_crt0.
new_memmap = join(FRAMEWORK_DIR, "src", mcu, "pico_platform", "memmap_default.ld")
if isfile(new_memmap):
    # pico_standard_link generates this one too; like there, no PSRAM region by default (PICO_PSRAM_SIZE_BYTES unset).
    Path(join(genned_dir, "pico_psram_region.ld")).write_text("PSRAM(rwx) : ORIGIN = 0x11000000, LENGTH = 0\n")
    # Same search order as pico_standard_link: platform fragments first (they override the common ones),
    # then the common fragments, then the generated region files (already in LIBPATH).
    env.Prepend(LIBPATH=[
        join(FRAMEWORK_DIR, "src", mcu, "pico_platform", "script_include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_standard_link", "script_include"),
    ])
    # CMake passes default_locations.ld as an extra --script before the memmap. PlatformIO always puts
    # -T <LDSCRIPT_PATH> first, so use a wrapper script that includes both in the right order.
    Path(join(genned_dir, "memmap_default_pio.ld")).write_text(
        "/* Generated by PlatformIO */\nINCLUDE \"default_locations.ld\"\nINCLUDE \"memmap_default.ld\"\n"
    )
    env.Prepend(LIBPATH=[join(FRAMEWORK_DIR, "src", mcu, "pico_platform")])
    env.Replace(LDSCRIPT_PATH=join(genned_dir, "memmap_default_pio.ld"))
else:
    env.Replace(LDSCRIPT_PATH=join(FRAMEWORK_DIR, "src", "rp2_common", "pico_crt0", mcu, "memmap_default.ld"))

# build base files
# system_RP2040.c
# env.BuildSources(
#     join("$BUILD_DIR", "PicoSDK"),
#     join(FRAMEWORK_DIR, "src", "rp2_common", "cmsis", "stub", "CMSIS", "Device", "RP2040", "Source")
# )
pad_script = join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "pad_checksum")
pad_args = ["-s 0xffffffff"]
if is_rp2350:
    if isfile(join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "pad")):
        # SDK >= 2.3.0: RP2350 boot2 is only padded, not checksummed; no seed or arch arguments.
        pad_script = join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "pad")
        pad_args = []
    else:
        pad_args.append("-a riscv" if is_riscv else "-a arm")
# the RP2040 version of pad_checksum doesn't take an "-a" argument at all.

current_defines = []
for x in env["CPPDEFINES"]:
    # can be a tuple (key, value) or just a key
    if isinstance(x, tuple):
        current_defines.append(f"-D{x[0]}={str(x[1])}")
    else:
        current_defines.append(f"-D{x}")
gen_boot2_cmd = env.Command(
    join("$BUILD_DIR", "boot2.S"),  # $TARGET
    join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "compile_time_choice.S"),  # $SOURCE
    env.VerboseAction(" ".join([
        "$CC",
        "$ASPPFLAGS",
        #"$ASFLAGS",
        #"$CCFLAGS",
    ] 
    + current_defines
    + [
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "asminclude"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "common", "pico_base_headers", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "generated"),
        "-I", "$PROJECT_BUILD_DIR/$PIOENV/generated",
        "-I\"%s\"" % join(rp2_variant_dir, "pico_platform", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_compiler", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_hazard3", "include"),
        "-I\"%s\"" % join(rp2_variant_dir, "hardware_regs", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_common", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_sections", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_panic", "include"),
        "-o",
        join("$BUILD_DIR", "boot2.elf"),
        "-nostdlib",
        "--specs=nosys.specs",
        "-nostartfiles",
        "-Wl,-T,\"%s\"" % join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "boot_stage2.ld"),
        "$SOURCE"
    ] + [ " && "] + [
        "$OBJCOPY",
        "-Obinary",
        join("$BUILD_DIR", "boot2.elf"),
        join("$BUILD_DIR", "boot2.bin")
    ] + [ " && "] + [
        "$PYTHONEXE",
        "\"%s\"" % pad_script,
    ] + pad_args + [
        join("$BUILD_DIR", "boot2.bin"),
        join("$BUILD_DIR", "boot2.S"),
    ]), "Generating boot2 $BUILD_DIR/boot2.S")
)
env.Depends("$BUILD_DIR/${PROGNAME}.elf", gen_boot2_cmd)

# default compontents
default_common_rp2_components = [
    ("hardware_adc", "+<*>"),
    ("hardware_boot_lock", "+<*>"),
    ("hardware_clocks", "+<*>"),
    ("hardware_dma", "+<*>"),
    ("hardware_flash", "+<*>"),
    ("hardware_gpio", "+<*>"),
    ("hardware_i2c", "+<*>"),
    ("hardware_interp", "+<*>"),
    ("hardware_irq", "+<*>"),
    ("hardware_pio", "+<*>"),
    ("hardware_pll", "+<*>"),
    ("hardware_pwm", "+<*>"),
    ("hardware_rcp", "+<*>"),
    ("hardware_resets", "+<*>"),
    ("hardware_spi", "+<*>"),
    ("hardware_sync_spin_lock", "+<*>"),
    ("hardware_sync", "+<*>"),
    ("hardware_ticks", "+<*>"),
    ("hardware_timer", "+<*>"),
    ("hardware_uart", "+<*>"),
    ("hardware_vreg", "+<*>"),
    ("hardware_watchdog", "+<*>"),
    ("hardware_xip_cache", "+<*>"),
    ("hardware_xosc", "+<*>"),
    ("pico_aon_timer", "+<*>"),
    ("pico_atomic", "+<*>"),
    ("pico_bootrom", "+<*>"),
    ("pico_bootsel_via_double_reset", "+<*>"),
    # cxa_guard.c (thread-safe C++ static init) only exists in SDK >= 2.3.0; the filter ignores it otherwise
    ("pico_clib_interface", "-<*> +<newlib_interface.c> +<cxa_guard.c>"),
    ("pico_flash", "+<*>"),
    ("pico_i2c_slave", "+<*>"),
    ("pico_multicore", "+<*>"),
    ("pico_platform_panic", "+<*>"),
    ("pico_rand", "+<*>"),
    ("pico_runtime_init", "+<*>"),
    ("pico_runtime", "+<*>"),
    ("pico_status_led", "+<*>"),
    ("pico_stdio", "+<*>"),
    ("pico_stdlib", "+<*>"),
    ("pico_standard_binary_info", "+<*>"),
    ("pico_unique_id", "+<*>"),
]

if use_pico_malloc:
    default_common_rp2_components.append(("pico_malloc", "+<*>"))
    env.Append(LINKFLAGS=[
        "-Wl,--wrap=malloc",
        "-Wl,--wrap=calloc",
        "-Wl,--wrap=realloc",
        "-Wl,--wrap=free",
    ])

# ---- runtime support libraries, linked by pico_runtime in a CMake build ----
# Each has an implementation that can be chosen with -D PIO_DEFAULT_<LIB>_IMPL=<impl>, like PICO_DEFAULT_<LIB>_IMPL.
# "pico" (default) uses the SDK's optimized versions (RP2040 bootrom routines, RP2350 VFP / double coprocessor (DCP),
# Hazard3 assembly), "compiler" uses the compiler's libgcc / C library versions.
is_rp2040 = not is_rp2350

def wrap_functions(names):
    env.Append(LINKFLAGS=["-Wl,--wrap=%s" % n for n in names])

def select_impl(lib, allowed):
    impl = get_define_value("PIO_DEFAULT_%s_IMPL" % lib.upper(), "pico")
    if impl == "auto":
        impl = "pico"
    if impl not in allowed:
        sys.stderr.write("Unsupported PIO_DEFAULT_%s_IMPL '%s' for %s (supported: %s)\n" % (
            lib.upper(), impl, board.get("build.mcu"), ", ".join(allowed)))
        env.Exit(-1)
    return impl

def add_runtime_lib(name, src_filter, impl_define=None):
    default_common_rp2_components.append((name, src_filter))
    if impl_define:
        env.Append(CPPDEFINES=[(impl_define, 1)])

float_aeabi_arith = ["__aeabi_fadd", "__aeabi_fdiv", "__aeabi_fmul", "__aeabi_frsub", "__aeabi_fsub"]
float_aeabi_cmp = ["__aeabi_cfcmpeq", "__aeabi_cfrcmple", "__aeabi_cfcmple", "__aeabi_fcmpeq", "__aeabi_fcmplt",
                   "__aeabi_fcmple", "__aeabi_fcmpge", "__aeabi_fcmpgt", "__aeabi_fcmpun"]
float_aeabi_conv32 = ["__aeabi_i2f", "__aeabi_ui2f", "__aeabi_f2iz", "__aeabi_f2uiz"]
float_aeabi_conv64 = ["__aeabi_l2f", "__aeabi_ul2f", "__aeabi_f2lz", "__aeabi_f2ulz"]
float_aeabi_conv_double = ["__aeabi_f2d"]
float_sci = ["cosf", "sinf", "tanf", "atan2f", "expf", "logf", "sincosf"]
float_sci_extra = ["ldexpf", "copysignf", "truncf", "floorf", "ceilf", "roundf", "asinf", "acosf", "atanf", "sinhf",
                   "coshf", "tanhf", "asinhf", "acoshf", "atanhf", "exp2f", "log2f", "exp10f", "log10f", "powf",
                   "powintf", "hypotf", "cbrtf", "fmodf", "dremf", "remainderf", "remquof", "expm1f", "log1pf"]
float_all = (float_aeabi_arith + float_aeabi_cmp + float_aeabi_conv32 + float_aeabi_conv64 + float_aeabi_conv_double
             + ["sqrtf"] + float_sci + float_sci_extra + ["fmaf"])
double_all = [
    "__aeabi_dadd", "__aeabi_ddiv", "__aeabi_dmul", "__aeabi_drsub", "__aeabi_dsub",
    "__aeabi_cdcmpeq", "__aeabi_cdrcmple", "__aeabi_cdcmple", "__aeabi_dcmpeq", "__aeabi_dcmplt", "__aeabi_dcmple",
    "__aeabi_dcmpge", "__aeabi_dcmpgt", "__aeabi_dcmpun",
    "__aeabi_i2d", "__aeabi_ui2d", "__aeabi_d2iz", "__aeabi_d2uiz",
    "__aeabi_l2d", "__aeabi_ul2d", "__aeabi_d2lz", "__aeabi_d2ulz", "__aeabi_d2f",
    "sqrt", "cos", "sin", "tan", "atan2", "exp", "log", "sincos",
    "ldexp", "copysign", "trunc", "floor", "ceil", "round", "asin", "acos", "atan", "sinh", "cosh", "tanh", "asinh",
    "acosh", "atanh", "exp2", "log2", "exp10", "log10", "pow", "powint", "hypot", "cbrt", "fmod", "drem",
    "remainder", "remquo", "expm1", "log1p", "fma",
]

# pico_float
if is_riscv:
    float_impl = select_impl("float", ["pico", "compiler", "none"])
else:
    # no "none" on RP2350 Arm: the hard float ABI uses the FPU directly
    float_impl = select_impl("float", ["pico", "compiler"] + (["none"] if is_rp2040 else []))
if float_impl == "pico":
    if is_rp2040:
        add_runtime_lib("pico_float", "-<*> +<float_aeabi_rp2040.S> +<float_init_rom_rp2040.c> +<float_math.c> "
                        "+<float_v1_rom_shim_rp2040.S>", "LIB_PICO_FLOAT_PICO")
        wrap_functions(float_all)
    elif not is_riscv:
        # pico_float_pico_vfp: arithmetic, compares, 32-bit conversions, sqrtf and fmaf are VFP instructions
        add_runtime_lib("pico_float", "-<*> +<float_math.c> +<float_conv32_vfp.S> +<float_common_m33.S> "
                        "+<float_sci_m33_vfp.S>", "LIB_PICO_FLOAT_PICO")
        env.Append(CPPDEFINES=[("LIB_PICO_FLOAT_PICO_VFP", 1)], CCFLAGS=["-fno-math-errno"])
        wrap_functions(float_aeabi_conv64 + float_sci + float_sci_extra)
    else:
        # Hazard3: provides the libgcc soft float functions directly, no wrapping
        add_runtime_lib("pico_float", "-<*> +<float_single_hazard3.S>", "LIB_PICO_FLOAT_PICO")
elif float_impl == "none":
    add_runtime_lib("pico_float", "-<*> +<float_none.S>", "LIB_PICO_FLOAT_NONE")
    wrap_functions(float_all)
else:
    env.Append(CPPDEFINES=[("LIB_PICO_FLOAT", 1), ("LIB_PICO_FLOAT_COMPILER", 1)])

# pico_double (the SDK has no optimized double implementation for RISC-V, so "pico" means "compiler" there)
double_impl = select_impl("double", ["pico", "compiler", "none"])
if double_impl == "pico" and is_riscv:
    double_impl = "compiler"
if double_impl == "pico":
    if is_rp2040:
        add_runtime_lib("pico_double", "-<*> +<double_aeabi_rp2040.S> +<double_init_rom_rp2040.c> +<double_math.c> "
                        "+<double_v1_rom_shim_rp2040.S>", "LIB_PICO_DOUBLE_PICO")
    else:
        add_runtime_lib("pico_double", "-<*> +<double_math.c> +<double_aeabi_dcp.S> +<double_fma_dcp.S> "
                        "+<double_sci_m33.S> +<double_conv_m33.S>", "LIB_PICO_DOUBLE_PICO")
        env.Append(CPPDEFINES=[("LIB_PICO_DOUBLE_PICO_DCP", 1)])
    wrap_functions(double_all)
elif double_impl == "none":
    add_runtime_lib("pico_double", "-<*> +<double_none.S>", "LIB_PICO_DOUBLE_NONE")
    # printing floats/doubles won't work, so save the space
    env.Append(CPPDEFINES=[("PICO_PRINTF_SUPPORT_FLOAT", 0)])
    wrap_functions(double_all)
else:
    env.Append(CPPDEFINES=[("LIB_PICO_DOUBLE", 1), ("LIB_PICO_DOUBLE_COMPILER", 1)])

# pico_divider (+ hardware_divider): RP2040 has a memory-mapped hardware divider, RP2350 has divide instructions
divider_impl = select_impl("divider", ["pico", "hardware", "compiler"] if is_rp2040 else ["pico", "compiler"])
if is_rp2040:
    add_runtime_lib("hardware_divider", "-<*> +<divider.c>")
    default_common_rp2_components.append(("hardware_divider", "-<*> +<divider.S>", "_asm"))
if is_rp2040 and divider_impl in ("pico", "hardware"):
    add_runtime_lib("pico_divider", "-<*> +<divider_hardware.S>", "LIB_PICO_DIVIDER_HARDWARE")
    wrap_functions(["__aeabi_idiv", "__aeabi_idivmod", "__aeabi_ldivmod",
                    "__aeabi_uidiv", "__aeabi_uidivmod", "__aeabi_uldivmod"])
else:
    add_runtime_lib("pico_divider", "-<*> +<divider_compiler.c>", "LIB_PICO_DIVIDER_COMPILER")

# pico_int64_ops: RP2040 only
int64_ops_impl = select_impl("int64_ops", ["pico", "compiler"])
if is_rp2040 and int64_ops_impl == "pico":
    add_runtime_lib("pico_int64_ops", "-<*> +<pico_int64_ops_aeabi.S>", "LIB_PICO_INT64_OPS_PICO")
    wrap_functions(["__aeabi_lmul"])
else:
    env.Append(CPPDEFINES=[("LIB_PICO_INT64_OPS", 1), ("LIB_PICO_INT64_OPS_COMPILER", 1)])

# pico_bit_ops
bit_ops_impl = select_impl("bit_ops", ["pico", "compiler"])
if bit_ops_impl == "pico":
    add_runtime_lib("pico_bit_ops", "-<*> +<bit_ops_aeabi.S>", "LIB_PICO_BIT_OPS_PICO")
    if is_rp2040:
        wrap_functions(["__clzdi2", "__ctzsi2", "__popcountsi2", "__popcountdi2", "__clz", "__clzl", "__clzsi2",
                        "__clzll"])
    wrap_functions(["__ctzdi2"])
else:
    env.Append(CPPDEFINES=[("LIB_PICO_BIT_OPS", 1), ("LIB_PICO_BIT_OPS_COMPILER", 1)])

# pico_mem_ops: RP2040 only (bootrom memcpy/memset)
mem_ops_impl = select_impl("mem_ops", ["pico", "compiler"])
if is_rp2040 and mem_ops_impl == "pico":
    add_runtime_lib("pico_mem_ops", "-<*> +<mem_ops_aeabi.S>", "LIB_PICO_MEM_OPS_PICO")
    wrap_functions(["memcpy", "memset", "__aeabi_memcpy", "__aeabi_memset", "__aeabi_memcpy4", "__aeabi_memset4",
                    "__aeabi_memcpy8", "__aeabi_memset8"])
else:
    env.Append(CPPDEFINES=[("LIB_PICO_MEM_OPS", 1), ("LIB_PICO_MEM_OPS_COMPILER", 1)])

# pico_cxx_options: plain malloc/free based operator new/delete (the builder already compiles C++ with
# -fno-exceptions -fno-rtti), and pico_platform_common (linked by pico_platform)
default_common_rp2_components.extend([
    ("pico_cxx_options", "-<*> +<new_delete.cpp>"),
    ("pico_platform_common", "+<*>"),
])

# Libraries that are not linked by default in CMake but were impossible to use here (sources never compiled).
# Compiling them is harmless: unused functions are removed by --gc-sections.
default_common_rp2_components.extend([
    ("hardware_rosc", "+<*>"),
    ("pico_low_power", "-<*> +<low_power.c>"),
])
if is_riscv:
    # hardware_exception replaces crt0's machine exception handler with its own table on RISC-V.
    # Only included when requested, as that's a global change.
    if "PIO_USE_HARDWARE_EXCEPTION" in cpp_defines:
        default_common_rp2_components.append(("hardware_exception", "+<*>"))
        env.Append(CPPDEFINES=[("PICO_CRT0_NO_ISR_RISCV_MACHINE_EXCEPTION", 1)])
else:
    default_common_rp2_components.append(("hardware_exception", "-<*> +<exception.c>"))
if is_rp2350:
    default_common_rp2_components.append(("hardware_psram", "+<*>"))

# printf implementation, like pico_printf / pico_stdio in a CMake build. Default "pico" (pico_printf_pico): the SDK's
# own printf with float support, output through pico_stdio. "compiler" keeps the C library's printf (newlib-nano, no %f).
if printf_impl == "pico":
    default_common_rp2_components.append(("pico_printf", "-<*> +<printf.c>"))
    env.Append(
        CPPDEFINES=[("LIB_PICO_PRINTF_PICO", 1)],
        LINKFLAGS=["-Wl,--wrap=%s" % f for f in (
            "sprintf", "snprintf", "vsnprintf",                   # pico_printf
            "printf", "vprintf", "puts", "putchar", "getchar",    # pico_stdio
        )]
    )
elif printf_impl == "compiler":
    env.Append(CPPDEFINES=[("LIB_PICO_PRINTF_COMPILER", 1)])
else:
    sys.stderr.write("Unsupported PIO_DEFAULT_PRINTF_IMPL '%s' (supported: pico, compiler)\n" % printf_impl)
    env.Exit(-1)

# SDK >= 2.3.0: pico_runtime links pico_thread_local (default implementation: per_thread)
if isdir(join(FRAMEWORK_DIR, "src", "rp2_common", "pico_thread_local")):
    default_common_rp2_components.append(("pico_thread_local", "+<*>"))
    if not any(str(d).startswith("PICO_THREAD_LOCAL_MODE_") for d in cpp_defines):
        env.Append(CPPDEFINES=[("PICO_THREAD_LOCAL_MODE_PER_THREAD", 1)])

# multiple stdio implementations can be on at the same time!
if "LIB_PICO_STDIO_USB" in flags:
    default_common_rp2_components.append(("pico_stdio_usb", "+<*>"))
    # SDK >= 2.3.0 moved the USB reset interface out of pico_stdio_usb
    if isdir(join(FRAMEWORK_DIR, "src", "rp2_common", "pico_usb_reset")):
        default_common_rp2_components.append(("pico_usb_reset", "+<*>"))
if "LIB_PICO_STDIO_UART" in flags:
    default_common_rp2_components.append(("pico_stdio_uart", "+<*>"))
if "LIB_PICO_STDIO_SEMIHOSTING" in flags:
    default_common_rp2_components.append(("pico_stdio_semihosting", "+<*>"))
if "LIB_PICO_STDIO_RTT" in flags:
    default_common_rp2_components.append(("pico_stdio_rtt", "+<*>"))

if is_rp2350:
    default_common_rp2_components.extend(
        [
            ("hardware_powman", "+<*>"),
            ("hardware_sha256", "+<*>"),
            ("pico_sha256", "+<*>"),
        ]
    )
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_powman", "include"),
            join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_sha256", "include"),
            join(FRAMEWORK_DIR, "src", "rp2_common", "pico_sha256", "include"),
        
    ])
else:
    default_common_rp2_components.extend(
        [
            ("hardware_rtc", "+<*>"),
        ]
    )
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_rtc", "include"),        
    ])

default_common_components = [
    ("pico_time", "+<*>"),
    ("pico_util", "+<*>"),
    ("pico_sync", "+<*>"),
    ("hardware_claim", "+<*>"),
]

# Like pico_add_library() in a CMake build, every SDK library that is part of the build gets a global
# LIB_<LIBRARY>=1 define. The SDK uses these to detect which other libraries are present, e.g.
# LIB_PICO_MULTICORE makes flash_safe_execute() pause the other core and pico_malloc take a mutex.
# Libraries created with NOFLAG in CMake don't get one.
# Note: LIB_TINYUSB_DEVICE / LIB_TINYUSB_HOST are deliberately not set; they'd compile pico_stdio_usb out.
lib_defines_noflag = {"pico_thread_local"}
# components that don't exist in the installed SDK version (e.g. added in 2.3.0) are skipped
default_common_rp2_components = [
    e for e in default_common_rp2_components if isdir(join(FRAMEWORK_DIR, "src", "rp2_common", e[0]))
]
lib_defines = []
for e in default_common_rp2_components + default_common_components:
    if e[0] not in lib_defines_noflag and e[0] not in lib_defines:
        lib_defines.append(e[0])
if not use_multicore:
    # pico_multicore is still compiled (for API compatibility), but the SDK treats the build as single-core.
    lib_defines.remove("pico_multicore")
lib_flags = []
for lib in lib_defines:
    name = "LIB_" + lib.upper()
    # don't duplicate or override what's already defined (e.g. LIB_PICO_STDIO_USB, or user build_flags)
    if name not in cpp_defines and name not in flags:
        lib_flags.append((name, 1))
env.Append(CPPDEFINES=lib_flags)

env.BuildSources(
    join("$BUILD_DIR", "PicoSDKPlatform"),
    join(FRAMEWORK_DIR, "src", mcu, "pico_platform"),
    "-<*> +<*.c>"
)

# entries are (component, src_filter) or (component, src_filter, build_dir_suffix), the latter for components
# whose sources must go to separate build folders (e.g. divider.S and divider.c would both become divider.o)
for entry in default_common_rp2_components:
    component, src_filter = entry[0], entry[1]
    comp_src_dir = join(FRAMEWORK_DIR, "src", "rp2_common", component)
    comp_build_dir = join("$BUILD_DIR", "PicoSDK%s%s" % (component, entry[2] if len(entry) > 2 else ""))

    pio_headers = preprocess_pio_sources(comp_src_dir)
    c_nodes = env.BuildSources(comp_build_dir, comp_src_dir, src_filter)

    if pio_headers:
        env.Depends(c_nodes, pio_headers)

pico_crt0 = "crt0_riscv.S" if is_riscv else "crt0.S"
env.BuildSources(
    join("$BUILD_DIR", "PicoSDKCRT0"),
    join(FRAMEWORK_DIR, "src", "rp2_common", "pico_crt0"),
    "-<*> +<%s>" % pico_crt0
)

for component, src_filter in default_common_components:
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKCommon%s" % component),
        join(FRAMEWORK_DIR, "src", "common", component),
        src_filter
    )
