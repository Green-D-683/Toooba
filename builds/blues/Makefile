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

include ./blues_target.mk

#================================================================
# Parameter settings for MIT RISCY

BSC_COMPILATION_FLAGS += -D BSIM \

include $(REPO)/builds/Resources/Include_RISCY_Config.mk

#================================================================
# Common boilerplate rules

include $(REPO)/builds/Resources/Include_Common.mk

define BLUES_COMPDB_JSON
[\
	{\
    	\"directory\": \"./builds/blues\",\
    	\"command\": \"bsc -u -sim -elab $(RTL_GEN_DIRS) $(BSC_COMPILATION_FLAGS) -p $(BSC_PATH)\"\
	}\
]
endef

blues: 
	@echo $(BLUES_COMPDB_JSON) > blues_compdb.json

blues_compdb.json: blues

blues_target.mk:
	cp blues_target_default.mk blues_target.mk