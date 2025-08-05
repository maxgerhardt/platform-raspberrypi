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

mcu = "rp2350" if board.get('build.mcu') == "rp2350" else "rp2040"
is_rp2350 = mcu == "rp2350"
rp2_variant_dir = join(FRAMEWORK_DIR, "src", mcu)
header = "%s.h" % board.get("build.variant")
# try to find the board header in the common directory
if isfile(join(FRAMEWORK_DIR, "src", "boards", "include", "boards", header)):
    rp2_board_header = board.get("build.picosdk.board_header", header)
else:
    rp2_board_header = board.get("build.picosdk.board_header", "pico.h")

# include basic settings
env.SConscript("_bare.py")

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
        # BUG: defining PICO_RP2040 in any way will force compilation for 2040 only.
        # FIX: add RP2350 only if board requested was 2350
        ("PICO_RP2350" if board.get('build.mcu') == "rp2350" else "PICO_RP2040", 1),
        ("PICO_RISCV", 0),
        ("PICO_ARM", 1),
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
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_divider", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_dma", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_exception", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_flash", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_gpio", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_i2c", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_interp", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_irq", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_pio", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_pll", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_pwm", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_resets", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "hardware_rcp", "include"),
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
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_rtt", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_rtt", "SEGGER", "RTT"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_semihosting", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_stdio_uart", "include"),
        join(FRAMEWORK_DIR, "src", "rp2_common", "pico_unique_id", "include"),
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

flags = []
# configure default but overridable defines
# todo figure this out from arduino-pico info? :))
if not "PICO_DEFAULT_BOOT_STAGE2_FILE" in cpp_defines:
    pass
if not "PICO_DEFAULT_BOOT_STAGE2" in cpp_defines:
    pass
if not "PIO_NO_STDIO_UART" in cpp_defines:
    flags.append(("PICO_STDIO_UART", 1))
    # SDK C code specifies it as LIB_... so do that too
    flags.append(("LIB_PICO_STDIO", 1))
    flags.append(("LIB_PICO_STDIO_UART", 1))
if not "PIO_NO_MULTICORE" in cpp_defines:
    flags.append(("PICO_MULTICORE_ENABLED", 1))
# check selected double implementation
double_impl = "auto"
if "PIO_DEFAULT_DOUBLE_IMPL" in cpp_defines:
    # should be auto, compiler, dcp, rp2040, none
    double_impl = cpp_defines["PIO_DEFAULT_DOUBLE_IMPL"]
float_impl = "auto"
if "PIO_DEFAULT_FLOAT_IMPL" in cpp_defines:
    # should be auto, compiler, dcp, rp2040, vfp, none
    float_impl = cpp_defines["PIO_DEFAULT_FLOAT_IMPL"]
divider_impl = "auto"
if "PIO_DEFAULT_DIVIDER_IMPL" in cpp_defines:
    # should be auto, hardware, compiler
    float_impl = cpp_defines["PIO_DEFAULT_FLOAT_IMPL"]
printf_impl = "pico"
if "PIO_DEFAULT_PRINTF_IMPL" in cpp_defines:
    # should be pico, compiler, none
    float_impl = cpp_defines["PIO_DEFAULT_FLOAT_IMPL"]
if not "PIO_NO_BINARY_INFO" in cpp_defines:
    flags.append(("PICO_BINARY_INFO_ENABLED", 1))

if not "PIO_USE_DEFAULT_PAGE_SIZE" in cpp_defines:
    env.Append(LINKFLAGS=["-Wl,-z,max-page-size=4096"])

timeout = 0
if "PIO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS" in cpp_defines:
    timeout = cpp_defines["PIO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS"]
flags.append(("PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS", timeout))

# default to USB stdio if nothing else defined (or explicitly disabled)
if not any(str(flag).startswith("PIO_STDIO") for flag in cpp_defines) and "PIO_STDIO_NONE" not in cpp_defines:
    cpp_defines.append("PIO_STDIO_USB")

def build_double_library():
    pass

def build_float_library():
    pass

def build_divider_library():
    pass

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

build_double_library()
build_float_library()
build_divider_library()
configure_printf_impl()

# default false, only mentioned here:
# PICO_CXX_ENABLE_EXCEPTIONS
# PICO_CXX_ENABLE_RTTI
# PICO_CXX_ENABLE_CXA_ATEXIT
env.Append(CPPDEFINES=flags)


# configure linker script (memmap_default)
# this will want a file called pico_flash_region.ld:
flash_region = "FLASH(rx) : ORIGIN = 0x10000000, LENGTH = %s\n" % str(board.get("upload.maximum_size"))
Path(join(genned_dir, "pico_flash_region.ld")).write_text(flash_region)

env.Replace(LDSCRIPT_PATH=join(FRAMEWORK_DIR, "src", "rp2_common", "pico_crt0", mcu, "memmap_default.ld"))

# build base files
# system_RP2040.c
# env.BuildSources(
#     join("$BUILD_DIR", "PicoSDK"),
#     join(FRAMEWORK_DIR, "src", "rp2_common", "cmsis", "stub", "CMSIS", "Device", "RP2040", "Source")
# )

gen_boot2_cmd = env.Command(
    join("$BUILD_DIR", "boot2.S"),  # $TARGET
    join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "compile_time_choice.S"),  # $SOURCE
    env.VerboseAction(" ".join([
        "$CC",
        "$ASPPFLAGS",
        #"$ASFLAGS",
        #"$CCFLAGS",
    ] 
    + ["-D%s=%s" % (flag[0], str(flag[1])) for flag in env["CPPDEFINES"]] 
    + [
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "asminclude"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "common", "pico_base_headers", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "generated"),
        "-I", "$PROJECT_BUILD_DIR/$PIOENV/generated",
        "-I\"%s\"" % join(rp2_variant_dir, "pico_platform", "include"),
        "-I\"%s\"" % join(FRAMEWORK_DIR, "src", "rp2_common", "pico_platform_compiler", "include"),
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
        join(FRAMEWORK_DIR, "src", mcu, "boot_stage2", "pad_checksum"),
        "-s 0xffffffff",
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
    ("pico_clib_interface", "-<*> +<newlib_interface.c>"),
    ("pico_flash", "+<*>"),
    ("pico_i2c_slave", "+<*>"),
    #("pico_malloc", "+<*>"),  # needs additional linker wrapper flags for malloc, calloc, realloc and free
    ("pico_multicore", "+<*>"),
    ("pico_platform_panic", "+<*>"),
    ("pico_rand", "+<*>"),
    ("pico_runtime_init", "+<*>"),
    ("pico_runtime", "+<*>"),
    ("pico_stdio_rtt", "+<*>"),
    ("pico_stdio_semihosting", "+<*>"),
    ("pico_stdio_uart", "+<*>"),
    ("pico_stdio_usb", "+<*>"),
    ("pico_stdio", "+<*>"),
    ("pico_stdlib", "+<*>"),
    ("pico_standard_binary_info", "+<*>"),
    ("pico_unique_id", "+<*>"),
]

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

env.BuildSources(
    join("$BUILD_DIR", "PicoSDKPlatform"),
    join(FRAMEWORK_DIR, "src", mcu, "pico_platform"),
    "-<*> +<*.c>"
)

for component, src_filter in default_common_rp2_components:
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDK%s" % component),
        join(FRAMEWORK_DIR, "src", "rp2_common", component),
        src_filter
    )

# Will be crt0_riscv.S for RISC-V builds..
env.BuildSources(
    join("$BUILD_DIR", "PicoSDKCRT0"),
    join(FRAMEWORK_DIR, "src", "rp2_common", "pico_crt0"),
    "-<*> +<crt0.S>"
)

default_common_components = [
    ("pico_time", "+<*>"),
    ("pico_util", "+<*>"),
    ("pico_sync", "+<*>"),
    ("hardware_claim", "+<*>"),
]
for component, src_filter in default_common_components:
    env.BuildSources(
        join("$BUILD_DIR", "PicoSDKCommon%s" % component),
        join(FRAMEWORK_DIR, "src", "common", component),
        src_filter
    )
