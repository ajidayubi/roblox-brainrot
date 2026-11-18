--!strict

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local GameConfig = require(Shared:WaitForChild("GameConfig"))
local BrainrotData = require(Shared:WaitForChild("BrainrotData"))

local Economy = require(script.Parent:WaitForChild("Economy"))
local Spawner = require(script.Parent:WaitForChild("Spawner"))
local Threat = require(script.Parent:WaitForChild("Threat"))
local BaseManager = require(script.Parent:WaitForChild("BaseManager"))
local GamePasses = require(script.Parent:WaitForChild("GamePasses"))
local DeveloperProducts = require(script.Parent:WaitForChild("DeveloperProducts"))

-- RemoteEvents live in a "Remotes" folder under ReplicatedStorage, exactly
-- where the client looks for them (a missing folder used to hang the client
-- forever at WaitForChild("Remotes")).
local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
if not remotesFolder then
	remotesFolder = Instance.new("Folder")
	remotesFolder.Name = "Remotes"
	remotesFolder.Parent = ReplicatedStorage
end

-- Create RemoteEvents under ReplicatedStorage/Remotes if missing
local function getOrCreateRemoteEvent(name: string): RemoteEvent
	local existing = remotesFolder:FindFirstChild(name)
	if existing and existing:IsA("RemoteEvent") then
		return existing
	end
	local ev = Instance.new("RemoteEvent")
	ev.Name = name
	ev.Parent = remotesFolder
	return ev
end

local catchBrainrotEvent = getOrCreateRemoteEvent("CatchBrainrot")
local buyLockEvent = getOrCreateRemoteEvent("BuyLock")
local rebirthEvent = getOrCreateRemoteEvent("Rebirth")
local buyUpgradeEvent = getOrCreateRemoteEvent("BuyUpgrade")
local waveWarningEvent = getOrCreateRemoteEvent("WaveWarning")

-- Conveyor folder in Workspace
local conveyorFolder = Workspace:FindFirstChild("Conveyor")
if not conveyorFolder or not conveyorFolder:IsA("Folder") then
	conveyorFolder = Instance.new("Folder")
	conveyorFolder.Name = "Conveyor"
	conveyorFolder.Parent = Workspace
end

-- Bases folder in Workspace
local basesFolder = Workspace:FindFirstChild("Bases")
if not basesFolder or not basesFolder:IsA("Folder") then
	basesFolder = Instance.new("Folder")
	basesFolder.Name = "Bases"
	basesFolder.Parent = Workspace
end

-- Player states and base assignments
type PlayerState = Economy.PlayerState
local playerStates: { [Player]: PlayerState } = {}
local playerBases: { [Player]: Model } = {}
local playerCarried: { [Player]: Model } = {}

Players.PlayerAdded:Connect(function(player)
	local state = Economy.newPlayerState(player)
	playerStates[player] = state

	-- Game pass perks (2x cash, extra slot, VIP speed) from prior purchases.
	GamePasses.applyToState(player, state)
	player.CharacterAdded:Connect(function()
		GamePasses.applyToState(player, state)
	end)

	local baseModel = BaseManager.assignBase(player, basesFolder)
	if baseModel then
		playerBases[player] = baseModel
	end
end)

-- Re-apply pass perks right after a purchase completes.
GamePasses.init(function(player)
	local state = playerStates[player]
	if state then
		GamePasses.applyToState(player, state)
	end
end)

-- Developer products: grant cash/boost on purchase (repeat-purchase).
DeveloperProducts.init(function(player)
	return playerStates[player]
end)

Players.PlayerRemoving:Connect(function(player)
	playerStates[player] = nil
	local baseModel = playerBases[player]
	if baseModel then
		-- Clear owner
		local ownerVal = baseModel:FindFirstChild("Owner")
		if ownerVal and ownerVal:IsA("StringValue") then
			ownerVal.Value = ""
		end
	end
	playerBases[player] = nil
	playerCarried[player] = nil
end)

-- Spawn loop
task.spawn(function()
	while true do
		task.wait(GameConfig.SPAWN_INTERVAL_SECONDS)
		pcall(function()
			Spawner.spawnBrainrot(conveyorFolder :: Folder)
		end)
	end
end)

-- Conveyor movement loop: brainrots ride the belt from the spawn gate
-- (z=-130) to the despawn gate (z=-10). Without this, spawned brainrots
-- pile up at the gate forever and the belt looks dead.
task.spawn(function()
	while true do
		task.wait(0.1)
		for _, model in ipairs(conveyorFolder:GetChildren()) do
			if model:IsA("Model") then
				pcall(function()
					Spawner.moveAlongConveyor(model, 0.1, 4)
				end)
			end
		end
	end
end)

-- Earnings loop (once per second)
task.spawn(function()
	while true do
		task.wait(1)
		local now = os.time()
		for player, state in pairs(playerStates) do
			local baseModel = playerBases[player]
			if baseModel then
				local brainrots = BaseManager.listBaseBrainrots(baseModel)
				Economy.tickEarnings(state, brainrots)
			end
		end
	end
end)

-- Wave timer loop
task.spawn(function()
	while true do
		task.wait(GameConfig.WAVE_INTERVAL_SECONDS)
		waveWarningEvent:FireAllClients()
		task.wait(GameConfig.WAVE_WARNING_SECONDS)
		
		local now = os.time()
		for player, state in pairs(playerStates) do
			local character = player.Character
			local baseModel = playerBases[player]
			if character and character:PrimaryPart and baseModel and baseModel.PrimaryPart then
				local hit = Threat.shouldWaveHit(character.PrimaryPart.Position, baseModel.PrimaryPart.Position)
				if hit then
					local isLocked = Threat.isBaseLocked(state, now)
					if not isLocked then
						local carried = playerCarried[player]
						if carried then
							carried:Destroy()
							playerCarried[player] = nil
						end
					end
				end
			end
		end
	end
end)

-- Handle CatchBrainrot
catchBrainrotEvent.OnServerEvent:Connect(function(player, brainrotModel)
	local baseModel = playerBases[player]
	if not baseModel then return end
	
	local state = playerStates[player]
	if not state then return end
	
	-- Check capacity (max base slots + ExtraSlot upgrade + ExtraSlot pass)
	local maxSlots = GameConfig.MAX_BASE_SLOTS + (state.upgrades.ExtraSlot or 0) + (state.passExtraSlots or 0)
	local currentBrainrots = BaseManager.listBaseBrainrots(baseModel)
	if #currentBrainrots >= maxSlots then
		return
	end
	
	if brainrotModel and brainrotModel:IsA("Model") and brainrotModel.Parent == conveyorFolder then
		-- Remove from conveyor and place on base
		brainrotModel.Parent = nil
		local placed = BaseManager.placeOnBase(player, brainrotModel, baseModel)
		if not placed then
			-- put back or destroy if no slot
			brainrotModel:Destroy()
		end
	end
end)

-- Handle BuyLock
buyLockEvent.OnServerEvent:Connect(function(player)
	local state = playerStates[player]
	if not state then return end
	local now = os.time()
	Threat.tryLockBase(state, now)
end)

-- Handle Rebirth
rebirthEvent.OnServerEvent:Connect(function(player)
	local state = playerStates[player]
	if not state then return end
	Economy.tryRebirth(state)
end)

-- Handle BuyUpgrade
buyUpgradeEvent.OnServerEvent:Connect(function(player, upgradeName: string)
	local state = playerStates[player]
	if not state then return end
	
	local costs = GameConfig.UPGRADE_COSTS
	local cost = costs[upgradeName]
	if not cost then return end
	
	-- Calculate cost scaling based on current upgrade level
	local currentLevel = state.upgrades[upgradeName] or 0
	local totalCost = cost * (1 + currentLevel)
	
	if Economy.canAfford(state, totalCost) then
		state.cash -= totalCost
		state.upgrades[upgradeName] = currentLevel + 1
	end
end)
