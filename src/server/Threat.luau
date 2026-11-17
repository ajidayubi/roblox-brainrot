--!strict

local GameConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("GameConfig"))

local Threat = {}

function Threat.isBaseLocked(state: { lockedUntil: number }, now: number): boolean
	return now < state.lockedUntil
end

function Threat.tryLockBase(state: { cash: number, lockedUntil: number, lockCooldownUntil: number }, now: number): boolean
	if state.cash < GameConfig.LOCK_COST then
		return false
	end
	if now < state.lockCooldownUntil then
		return false
	end
	
	state.cash -= GameConfig.LOCK_COST
	state.lockedUntil = now + GameConfig.LOCK_DURATION_SECONDS
	state.lockCooldownUntil = now + GameConfig.LOCK_COOLDOWN_SECONDS
	return true
end

function Threat.shouldWaveHit(playerPosition: Vector3, baseCenter: Vector3): boolean
	local distance = (playerPosition - baseCenter).Magnitude
	return distance > 20
end

function Threat.spawnRaccoon(workspaceFolder: Folder, basesFolder: Folder): Model
	local raccoon = Instance.new("Model")
	raccoon.Name = "SneakyRaccoon"
	
	local body = Instance.new("Part")
	body.Name = "Body"
	body.Size = Vector3.new(3, 2, 3)
	body.Position = Vector3.new(math.random(-40, 40), 2, math.random(-40, 40))
	body.Anchored = true
	body.Color = Color3.fromRGB(80, 80, 80)
	body.Parent = raccoon
	raccoon.PrimaryPart = body
	
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.new(0, 140, 0, 40)
	billboard.StudsOffset = Vector3.new(0, 2.5, 0)
	billboard.AlwaysOnTop = true
	
	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.TextColor3 = Color3.fromRGB(255, 100, 100)
	label.TextStrokeTransparency = 0
	label.TextSize = 14
	label.Font = Enum.Font.FredokaOne
	label.Text = "SNEAKY RACCOON"
	label.Parent = billboard
	billboard.Parent = body
	
	raccoon.Parent = workspaceFolder
	return raccoon
end

function Threat.stealLowestBrainrot(baseModel: Model, isLocked: boolean): string?
	if isLocked then
		return nil
	end
	
	local lowestRate = math.huge
	local lowestModel: Model? = nil
	local lowestName: string? = nil
	
	for _, child in ipairs(baseModel:GetChildren()) do
		if child:IsA("Model") then
			local rateVal = child:FindFirstChild("EarningsRate") :: NumberValue?
			if rateVal then
				if rateVal.Value < lowestRate then
					lowestRate = rateVal.Value
					lowestModel = child
					lowestName = child.Name
				end
			end
		end
	end
	
	if lowestModel then
		lowestModel:Destroy()
		return lowestName
	end
	
	return nil
end

return Threat
