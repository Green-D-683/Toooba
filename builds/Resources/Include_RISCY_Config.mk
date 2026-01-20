###  -*-Makefile-*-

# Copyright (c) 2018-2019 Bluespec, Inc. All Rights Reserved

# ================================================================
# Macros from RISCY_HOME/procs/RV64G_OOO/Makefile

PROC := RV64G_OOO

# core size
CORE_SIZE ?= SMALL
# cache size
CACHE_SIZE ?= LARGE
# always include perf counter
PERF_COUNT := true
# dram type in simulation: VC707 or AWSF1
SIM_DRAM_TYPE := AWSF1
# use Xilinx FPU IP cores
USE_XILINX_FPU ?= false

# default 1 core
CORE_NUM ?= 1
# TSO or WEAK
TSO_MM ?= false
# Lr upgrades line to E (no forward progress guarantee)
LR_UP_TO_E ?= false
# Forbid LLC from respoding a load (toS) request with E state
NO_LOAD_RESP_E ?= false
# Use self inv cache? (only for WEAK mm), value is the max hits in D$
SELF_INV_CACHE ?=
# self inv D$ in case of system inst or trap
SYSTEM_SELF_INV_L1D ?= false
# security
SECURITY ?= false
SECURE_LLC ?= false
SECURE_FLUSH ?= false
SECURE_NONE ?= false
SECURE_MSHR ?= false
SECURE_ARBITER ?= false
DISABLE_SECURE_BW ?= false
SIM_LOG_LLC_PARTITION_NUM ?=
SIM_LOG_LLC_MSHR_BANK_NUM ?=
SIM_LLC_ARBITER_NUM ?=
SIM_LLC_ARBITER_LAT ?=
# default check cache deadlock and rename error
CHECK_DEADLOCK ?= true
RENAME_DEBUG ?= false
INSTR_PREFETCHER_LOCATION ?= NONE
INSTR_PREFETCHER_TYPE ?= SINGLE_WINDOW_TARGET
DATA_PREFETCHER_LOCATION ?= L1
DATA_PREFETCHER_TYPE ?= STRIDE

# clk frequency depends on core size
ifneq (,$(filter $(CORE_SIZE),TINY SMALL BOOM MEDIUM))
USER_CLK_PERIOD ?= 24
else ifneq (,$(filter $(CORE_SIZE),SMALL_WIDE LARGE))
USER_CLK_PERIOD ?= 32
else ifneq (,$(filter $(CORE_SIZE),LARGE_WIDE))
USER_CLK_PERIOD ?= 40
else ifeq (,$(filter $(CORE_SIZE),MANUAL))
$(error unsupported CORE_SIZE)
endif

ifeq (,$(filter $(CACHE_SIZE),SMALL LARGE MC_1MB MC_2MB MANUAL))
$(error unsupported CACHE_SIZE)
endif


ifeq (,$(filter $(INSTR_PREFETCHER_LOCATION),NONE L1 L1LL LL))
	$(error unsupported INSTR_PREFETCHER_LOCATION)
endif
ifeq (,$(filter $(INSTR_PREFETCHER_TYPE),NEXT_LINE_ON_MISS NEXT_LINE_ON_ALL SINGLE_WINDOW MULTI_WINDOW SINGLE_WINDOW_TARGET MULTI_WINDOW_TARGET))
	$(error unsupported INSTR_PREFETCHER_TYPE)
endif


ifeq (,$(filter $(DATA_PREFETCHER_LOCATION),NONE L1 L1LL LL))
	$(error unsupported DATA_PREFETCHER_LOCATION)
endif
ifeq (,$(filter $(DATA_PREFETCHER_TYPE),MARKOV MARKOV_ON_HIT MARKOV_ON_HIT_2 BLOCK STRIDE STRIDE_ADAPTIVE))
	$(error unsupported DATA_PREFETCHER_TYPE)
endif

# ================================================================
# These are taken from: RISCY_HOME/procs/scripts/Makefile.common

XILINX_FP_FMA_LATENCY = 3
XILINX_INT_MUL_LATENCY = 2

# If not using manual tuning
ifeq (,$(filter $(CORE_SIZE),MANUAL)) 
BSC_COMPILATION_FLAGS += \
	-D CORE_$(CORE_SIZE)
else
include $(REPO)/builds/Resources/Include_RISCY_Parameters.mk
# Add parameters needed in ProcConfig.bsv otherwise declared by CORE_SIZE and CACHE_SIZE here
core_parameters = \
	USER_CLK_PERIOD \
	sizeSup \
	ROB_SIZE \
	NUM_EPOCHS \
	NUM_SPEC_TAGS \
	TLB_SIZE \
	LDQ_SIZE \
	STQ_SIZE \
	SB_SIZE \
	RS_ALU_SIZE \
	RS_MEM_SIZE \
	RS_FPUMULDIV_SIZE \
	TOUR_PRED_SIZE \
	BTB_SIZE \
	BTB_WAYS
BSC_COMPILATION_FLAGS += $(foreach parameter,$(core_parameters),-D $(parameter)=$($(parameter)))
endif

ifeq (,$(filter $(CACHE_SIZE),MANUAL))
BSC_COMPILATION_FLAGS += \
	-D CACHE_$(CACHE_SIZE)
else
include $(REPO)/builds/Resources/Include_RISCY_Parameters.mk
# Add parameters needed in ProcConfig.bsv otherwise declared by CORE_SIZE and CACHE_SIZE here
cache_parameters = \
	LOG_L1_LINES \
	LOG_L1_WAYS \
	LOG_LLC_LINES \
	LOG_LLC_WAYS
BSC_COMPILATION_FLAGS += $(foreach parameter,$(cache_parameters),-D $(parameter)=$($(parameter)))
endif

BSC_COMPILATION_FLAGS += \
	-D NUM_CORES=$(CORE_NUM) \
        -D XILINX_FP_FMA_LATENCY=$(XILINX_FP_FMA_LATENCY) \
        -D XILINX_INT_MUL_LATENCY=$(XILINX_INT_MUL_LATENCY) \
	-D USE_BSV_BRAM_SYNC_FIFO \
	-D INSTR_PREFETCHER_IN_$(INSTR_PREFETCHER_LOCATION) \
	-D INSTR_PREFETCHER_$(INSTR_PREFETCHER_TYPE) \
	-D DATA_PREFETCHER_IN_$(DATA_PREFETCHER_LOCATION) \
	-D DATA_PREFETCHER_$(DATA_PREFETCHER_TYPE)

ifndef SUPERSCALAR
	ifndef IN_ORDER
		# Default to Superscalar Core
		define SUPERSCALAR 
endef
		BSC_COMPILATION_FLAGS += -D SUPERSCALAR
	else
		BSC_COMPILATION_FLAGS += -D IN_ORDER
	endif
else
	ifdef IN_ORDER
		$(error Cannot be both In-Order and Superscalar)
	else 
		BSC_COMPILATION_FLAGS += -D SUPERSCALAR
	endif
endif

# TODO:
#    -D SELF_INV_CACHE -D L1D_MAX_HITS=$(SELF_INV_CACHE)
#    -D SYSTEM_SELF_INV_L1D
#    -D LR_UP_TO_E
#    -D NO_LOAD_RESP_E
# various SECURITY related flags
#    -D PERF_COUNT    -D CHECK_DEADLOCK    -D RENAME_DEBUG ...

# +RTS -K1G -RTS " --bscflags=" -steps-max-intervals 200  -check-assert

# ================================================================
