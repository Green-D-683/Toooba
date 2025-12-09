# TODO - remove explicit RV64ACDFIMSU here...

cleanup_failed:
	@printf "Removing\n$$(ls ../ | grep -E "RV64ACDFIMSU_Toooba_optimiser_[0-9]+" | sed "s/^/..\//g")\n"
	rm -rf $$(ls ../ | grep -E "RV64ACDFIMSU_Toooba_optimiser_[0-9]+" | sed "s/^/..\//g")
	@echo "Build Directories Cleaned - recommended to manually check ./optimiser_artifacts to ensure no erroneous outputs"

ifeq ($(strip $(filter --param_file,$(ARGS))),)
override ARGS += --param_file optimiser.json
endif

OPTIMISER_RUN = $(REPO)/optimiser/optimiser.py $(ARGS)
OPTIMISER ?= initialValues

optimiser: $(wildcard $(REPO)/optimiser/*.py) optimiser.json
ifneq ($(strip $(filter initialValues initialSweep incrementSweep,$(OPTIMISER))),)
	$(OPTIMISER_RUN) --optimiser $(OPTIMISER)
endif

optimiser_init: override OPTIMISER=initialValues
optimiser_init: optimiser

optimiser_init_sweep: override OPTIMISER=initialSweep 
optimiser_init_sweep: optimiser

optimiser_iter: override OPTIMISER=incrementSweep 
optimiser_iter: optimiser

optimiser.json: $(REPO)/optimiser/param_sweep.json
	cp $(REPO)/optimiser/param_sweep.json $@
