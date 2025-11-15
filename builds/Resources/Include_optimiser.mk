cleanup_failed:
	@printf "Removing\n$$(ls ../ | grep -E "RV64ACDFIMSU_Toooba_optimiser_[0-9]+" | sed "s/^/..\//g")\n"
	rm -rf $$(ls ../ | grep -E "RV64ACDFIMSU_Toooba_optimiser_[0-9]+" | sed "s/^/..\//g")
	@echo "Build Directories Cleaned - recommended to manually check ./optimiser_artifacts to ensure no erroneous outputs"

OPTIMISER_ARGS += 

optimiser: $(wildcard $(REPO)/optimiser/*.py)
	$(REPO)/optimiser/optimiser.py $(OPTIMISER_ARGS)

