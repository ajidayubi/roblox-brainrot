--!strict

local GameConfig = require(game:GetService("ReplicatedStorage").Shared.GameConfig)
local BrainrotData = require(game:GetService("ReplicatedStorage").Shared.BrainrotData)

export type PlayerState = {
	player: Player,
	cash: number,
	rebirthLevel: number,
	multiplier: number,
	passCashMultiplier: number,
	passExtraSlots: number,
	vip: boolean,
	lockedUntil: number,
	lockCooldownUntil: number,
	upgrades: {
		WalkSpeed: number,
		Magnet: number,
		ExtraSlot: number,
	},
}

local Economy = {}

function Economy.newPlayerState(player: Player): PlayerState
	return {
		player = player,
		cash = GameConfig.START_CASH,
		rebirthLevel = 0,
		multiplier = 1,
		passCashMultiplier = 1,
		passExtraSlots = 0,
		vip = false,
		lockedUntil = 0,
		lockCooldownUntil = 0,
		upgrades = {
			WalkSpeed = 0,
			Magnet = 0,
			ExtraSlot = 0,
		},
	}
end

function Economy.addCash(state: PlayerState, amount: number)
	state.cash += amount
end

function Economy.tickEarnings(state: PlayerState, brainrotsOnBase: { Model })
	local totalEarnings = 0
	for _, brainrotModel in ipairs(brainrotsOnBase) do
		local rateVal = brainrotModel:FindFirstChild("EarningsRate") :: NumberValue?
		if rateVal then
			totalEarnings += math.floor(rateVal.Value * state.multiplier * state.passCashMultiplier)
		end
	end
	if totalEarnings > 0 then
		Economy.addCash(state, totalEarnings)
	end
end

function Economy.canAfford(state: PlayerState, cost: number): boolean
	return state.cash >= cost
end

function Economy.rebirthCost(state: PlayerState): number
	return math.floor(GameConfig.REBIRTH_BASE_COST * (3 ^ state.rebirthLevel))
end

function Economy.tryRebirth(state: PlayerState): boolean
	local cost = Economy.rebirthCost(state)
	if not Economy.canAfford(state, cost) then
		return false
	end
	
	state.cash = GameConfig.START_CASH
	state.rebirthLevel += 1
	state.multiplier += GameConfig.REBIRTH_MULTIPLIER_PER_LEVEL
	return true
end

return Economy
