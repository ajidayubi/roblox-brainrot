--!strict

local BrainrotData = {}

export type Brainrot = {
	name: string,
	rarity: string,
	rate: number,
	cost: number,
	color: Color3,
}

BrainrotData.BRAINROTS = {
	{ name = "Noodle Cat", rarity = "Common", rate = 5, cost = 0, color = Color3.fromRGB(150, 150, 150) },
	{ name = "Sir Reginald Pigeon", rarity = "Common", rate = 8, cost = 0, color = Color3.fromRGB(150, 150, 150) },
	{ name = "Professor Pickle", rarity = "Rare", rate = 15, cost = 100, color = Color3.fromRGB(50, 150, 255) },
	{ name = "Sir Quacksalot", rarity = "Rare", rate = 22, cost = 250, color = Color3.fromRGB(50, 150, 255) },
	{ name = "DJ Toaster", rarity = "Epic", rate = 40, cost = 800, color = Color3.fromRGB(170, 50, 220) },
	{ name = "Captain Cactus", rarity = "Epic", rate = 60, cost = 1500, color = Color3.fromRGB(170, 50, 220) },
	{ name = "Grandma Rocket", rarity = "Legendary", rate = 95, cost = 4000, color = Color3.fromRGB(255, 215, 0) },
	{ name = "The Forbidden Burrito", rarity = "Legendary", rate = 150, cost = 8000, color = Color3.fromRGB(255, 215, 0) },
	{ name = "Quantum Llama", rarity = "Mythic", rate = 230, cost = 20000, color = Color3.fromRGB(255, 105, 180) },
	{ name = "King Spaghetti", rarity = "Mythic", rate = 340, cost = 40000, color = Color3.fromRGB(255, 105, 180) },
	{ name = "The Almighty Sock", rarity = "Secret", rate = 600, cost = 100000, color = Color3.fromRGB(255, 255, 255) },
	{ name = "Disco Shark", rarity = "Secret", rate = 900, cost = 250000, color = Color3.fromRGB(255, 255, 255) },
}

local RARITY_WEIGHTS = {
	Common = 45,
	Rare = 28,
	Epic = 15,
	Legendary = 8,
	Mythic = 3,
	Secret = 1,
}

local MUTATION_WEIGHTS = {
	None = 80,
	Golden = 10,
	Diamond = 5,
	Rainbow = 3,
	Void = 2,
}

local MUTATION_MULTIPLIERS = {
	None = 1,
	Golden = 2,
	Diamond = 4,
	Rainbow = 6,
	Void = 10,
}

function BrainrotData.rollRarity(): string
	local totalWeight = 0
	for _, weight in pairs(RARITY_WEIGHTS) do
		totalWeight += weight
	end
	
	local roll = math.random(1, totalWeight)
	local current = 0
	for rarity, weight in pairs(RARITY_WEIGHTS) do
		current += weight
		if roll <= current then
			return rarity
		end
	end
	return "Common"
end

function BrainrotData.rollMutation(): string
	local totalWeight = 0
	for _, weight in pairs(MUTATION_WEIGHTS) do
		totalWeight += weight
	end
	
	local roll = math.random(1, totalWeight)
	local current = 0
	for mutation, weight in pairs(MUTATION_WEIGHTS) do
		current += weight
		if roll <= current then
			return mutation
		end
	end
	return "None"
end

function BrainrotData.getEarnings(brainrot: Brainrot, mutation: string, rebirthMultiplier: number): number
	local mult = MUTATION_MULTIPLIERS[mutation] or 1
	return math.floor(brainrot.rate * mult * rebirthMultiplier)
end

function BrainrotData.getRandomByRarity(rarity: string): Brainrot?
	local pool = {}
	for _, b in ipairs(BrainrotData.BRAINROTS) do
		if b.rarity == rarity then
			table.insert(pool, b)
		end
	end
	if #pool == 0 then
		return BrainrotData.BRAINROTS[1]
	end
	return pool[math.random(1, #pool)]
end

return BrainrotData
