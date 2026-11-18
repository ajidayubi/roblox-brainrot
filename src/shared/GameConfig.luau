--!strict

local GameConfig = {
	SPAWN_INTERVAL_SECONDS = 4,
	CONVEYOR_LENGTH_STUDS = 120,
	WAVE_INTERVAL_SECONDS = 75,
	WAVE_WARNING_SECONDS = 5,
	LOCK_DURATION_SECONDS = 30,
	LOCK_COOLDOWN_SECONDS = 60,
	LOCK_COST = 500,
	REBIRTH_BASE_COST = 5000,
	REBIRTH_MULTIPLIER_PER_LEVEL = 2,
	MAX_BASE_SLOTS = 8,
	START_CASH = 100,

	-- Game pass asset IDs (Creator Dashboard, universe 10777475907).
	-- Created 2026-11-18 ~13:41 WIB, all on sale. 0 = not created yet.
	PASS_IDS = {
		Cash2x = 2094339074,
		ExtraSlot = 2093295021,
		VIP = 2093175052,
	} :: { [string]: number },

	PASS_SHOP = {
		{ key = "Cash2x", name = "2x Uang", price = 149, desc = "Penghasilan 2x lipat, selamanya." },
		{ key = "ExtraSlot", name = "Slot Ekstra", price = 99, desc = "+1 slot brainrot permanen." },
		{ key = "VIP", name = "VIP Brainrot", price = 299, desc = "2x uang + 1 slot + jalan lebih cepat." },
	},
	
	UPGRADE_COSTS = {
		WalkSpeed = 300,
		Magnet = 500,
		ExtraSlot = 1000,
	} :: { [string]: number },
}

return GameConfig
