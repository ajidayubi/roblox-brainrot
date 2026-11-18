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
	
	-- Developer product asset IDs (Creator Dashboard, universe 10777475907).
	-- Created 2026-11-18 ~14:31 WIB, all on sale. 0 = not created yet.
	PRODUCT_IDS = {
		Cash5000 = 3732998727,
		Cash25000 = 3732998760,
		Boost2x = 3732998797,
	} :: { [string]: number },

	PRODUCT_SHOP = {
		{ key = "Cash5000", name = "Paket Uang 5.000", price = 49, desc = "+5.000 cash langsung." },
		{ key = "Cash25000", name = "Paket Uang 25.000", price = 149, desc = "+25.000 cash langsung." },
		{ key = "Boost2x", name = "Boost 2x 10 Menit", price = 79, desc = "Penghasilan 2x lipat 10 menit." },
	},

	UPGRADE_COSTS = {
		WalkSpeed = 300,
		Magnet = 500,
		ExtraSlot = 1000,
	} :: { [string]: number },
}

return GameConfig
