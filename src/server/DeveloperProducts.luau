--!strict

-- Developer products: repeat-purchase Robux items.
-- Product IDs live in GameConfig.PRODUCT_IDS.
-- ProcessReceipt grants the item and returns PurchaseGranted while unknown ids
-- or a missing player return NotProcessedYet so the purchase is retried, never lost.

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local GameConfig = require(Shared:WaitForChild("GameConfig"))
local Economy = require(script.Parent:WaitForChild("Economy"))

local DeveloperProducts = {}

local BOOST_DURATION_SECONDS = 600
local CASH_AMOUNTS = {
	[GameConfig.PRODUCT_IDS.Cash5000] = 5000,
	[GameConfig.PRODUCT_IDS.Cash25000] = 25000,
}

function DeveloperProducts.init(getState: (Player) -> Economy.PlayerState?)
	MarketplaceService.ProcessReceipt = function(receiptInfo: { PlayerId: number, ProductId: number, PurchaseId: string }): Enum.ProductPurchaseDecision
		local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
		if not player then
			return Enum.ProductPurchaseDecision.NotProcessedYet
		end

		local state = getState(player)
		if not state then
			return Enum.ProductPurchaseDecision.NotProcessedYet
		end

		local productId = receiptInfo.ProductId

		local cashAmount = CASH_AMOUNTS[productId]
		if cashAmount then
			Economy.addCash(state, cashAmount)
			return Enum.ProductPurchaseDecision.PurchaseGranted
		elseif productId == GameConfig.PRODUCT_IDS.Boost2x then
			Economy.applyBoost(state, BOOST_DURATION_SECONDS)
			return Enum.ProductPurchaseDecision.PurchaseGranted
		end

		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
end

return DeveloperProducts
