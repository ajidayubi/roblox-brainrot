--!strict

-- Game passes for Brainrot Bay (Robux monetization).
-- Pass IDs live in GameConfig.PASS_IDS. An ID of 0 means the pass has not
-- been created in the Creator Dashboard yet: ownership is treated as false
-- and the shop button for it stays disabled.

local MarketplaceService = game:GetService("MarketplaceService")

local GameConfig = require(game:GetService("ReplicatedStorage").Shared.GameConfig)
local Economy = require(script.Parent:WaitForChild("Economy"))

local GamePasses = {}

local VIP_WALKSPEED = 24
local BASE_WALKSPEED = 16

local function ownsPass(player: Player, passId: number): boolean
	if passId == 0 then
		return false
	end
	local ok, result = pcall(function()
		return MarketplaceService:UserOwnsGamePassAsync(player.UserId, passId)
	end)
	return ok and result == true
end

-- (Re)applies every pass perk to a player's live state. Safe to call on
-- join, on respawn (VIP speed), and right after a purchase completes.
function GamePasses.applyToState(player: Player, state: Economy.PlayerState)
	local ids = GameConfig.PASS_IDS
	local hasCash2x = ownsPass(player, ids.Cash2x)
	local hasSlot = ownsPass(player, ids.ExtraSlot)
	local hasVip = ownsPass(player, ids.VIP)

	state.passCashMultiplier = 1
	if hasCash2x or hasVip then
		state.passCashMultiplier = 2
	end

	state.passExtraSlots = 0
	if hasSlot or hasVip then
		state.passExtraSlots = 1
	end

	state.vip = hasVip

	local character = player.Character
	if character then
		local humanoid = character:FindFirstChildOfClass("Humanoid")
		if humanoid then
			if hasVip then
				humanoid.WalkSpeed = VIP_WALKSPEED
			else
				humanoid.WalkSpeed = BASE_WALKSPEED
			end
		end
	end
end

-- Fires `onGranted(player)` whenever this player finishes buying one of
-- our passes, so perks land immediately without rejoining.
function GamePasses.init(onGranted: (Player) -> ())
	MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, passId, wasPurchased)
		if not wasPurchased then
			return
		end
		local ids = GameConfig.PASS_IDS
		if passId ~= ids.Cash2x and passId ~= ids.ExtraSlot and passId ~= ids.VIP then
			return
		end
		onGranted(player)
	end)
end

return GamePasses
