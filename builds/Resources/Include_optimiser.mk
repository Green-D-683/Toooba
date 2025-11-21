# TODO - remove explicit RV64ACDFIMSU here...

cleanup_failed:
	@printf "Removing\n$$(ls ../ | grep -E "RV64ACDFIMSU_Toooba_optimiser_[0-9]+" | sed "s/^/..\//g")\n"
	rm -rf $$(ls ../ | grep -E "RV64ACDFIMSU_Toooba_optimiser_[0-9]+" | sed "s/^/..\//g")
	@echo "Build Directories Cleaned - recommended to manually check ./optimiser_artifacts to ensure no erroneous outputs"

OPTIMISER_ARGS += --param_file optimiser.json

OPTIMISER_RUN = $(REPO)/optimiser/optimiser.py $(OPTIMISER_ARGS)

optimiser: $(wildcard $(REPO)/optimiser/*.py) optimiser.json

optimiser_init: optimiser
	$(OPTIMISER_RUN)

optimiser_init_sweep: optimiser
	$(OPTIMISER_RUN) --optimiser initialSweep

optimiser_iter: optimiser
	$(OPTIMISER_RUN) --optimiser incrementSweep

optimiser.json: $(REPO)/optimiser/param_sweep.json
	cp $(REPO)/optimiser/param_sweep.json $@