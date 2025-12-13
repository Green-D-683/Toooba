###  -*-Makefile-*-

# ================================================================
# Path to RISCY-OOO sources

RISCY_HOME ?= ../../src_Core/RISCY_OOO
# RISCY_HOME ?= $(HOME)/Projects/RISCV/MIT-riscy/riscy-OOO

RISCY_DIRS = $(RISCY_HOME)/procs/RV64G_OOO:$(RISCY_HOME)/procs/lib:$(RISCY_HOME)/coherence/src:$(RISCY_HOME)/fpgautils/lib

CONNECTAL_DIRS = $(RISCY_HOME)/connectal/bsv:$(RISCY_HOME)/connectal/tests/spi:$(RISCY_HOME)/connectal/lib/bsv

# ALL_RISCY_DIRS = $(RISCY_DIRS)
ALL_RISCY_DIRS = $(RISCY_DIRS):$(CONNECTAL_DIRS)

# ================================================================

REPO ?= ../..
ARCH ?= RV64ACDFIMSU

# ================================================================
# RISC-V config macros passed into Bluespec 'bsc' compiler

BSC_COMPILATION_FLAGS += \
	-D RV64 \
	-D ISA_PRIV_M  -D ISA_PRIV_U  -D ISA_PRIV_S  \
	-D SV39  \
	-D ISA_I  -D ISA_M  -D ISA_A  -D ISA_F  -D ISA_D  -D ISA_FD_DIV  -D ISA_C  \
	-D SHIFT_BARREL    \
	-D MULT_SYNTH    \
	-D Near_Mem_Caches    \
	-D FABRIC64    \


QUARTUS_DIR = .

# Default ISA test

TEST ?= rv64ui-p-add

#================================================================
# Parameter settings for MIT RISCY

BSC_COMPILATION_FLAGS += -D BSIM

override BENCHMARK_ARGS += --no_write_logs


-include ./Include_Generated_Params.mk

include $(REPO)/builds/Resources/Include_RISCY_Config.mk

#================================================================
# Common boilerplate rules

include $(REPO)/builds/Resources/Include_Common.mk

#================================================================
# Makefile rules for building for specific simulator: verilator

include $(REPO)/builds/Resources/Include_verilator.mk

full_clean::
	rm -f Include_Generated_Params.mk

ifdef BLUESPEC_VERILOG_LIB
QUARTUS_BLUESPEC_INCLUDE = $(subst /,\/,$(BLUESPEC_VERILOG_LIB))
else # SymLink Predefined Bluespec Library for Quartus in expected place
QUARTUS_BLUESPEC_INCLUDE = ..\/..\/BlueSpec-Verilog
endif

setup_quartus:: $(REPO)/Quartus/Toooba.qpf $(REPO)/Quartus/mkCoreW.qsf
	cp -f $(REPO)/Quartus/Toooba.qpf $(QUARTUS_DIR)/Toooba.qpf
	sed "s/..\/builds\/RV64ACDFIMSU_Toooba_verilator/./g" $(REPO)/Quartus/mkCoreW.qsf | sed "s/..\/BlueSpec-Verilog/$(QUARTUS_BLUESPEC_INCLUDE)/" > $(QUARTUS_DIR)/mkCoreW.qsf

$(QUARTUS_DIR)/mkCoreW.qsf: setup_quartus
$(QUARTUS_DIR)/Toooba.qpf: setup_quartus