--!strict

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")
local BrainrotData = require(Shared:WaitForChild("BrainrotData"))
local GameConfig = require(Shared:WaitForChild("GameConfig"))

local Spawner = {}

function Spawner.pickRandomBrainrotOfRarity(rarity: string)
	return BrainrotData.getRandomByRarity(rarity)
end

function Spawner.spawnBrainrot(conveyorFolder: Folder): Model
	local rarity = BrainrotData.rollRarity()
	local brainrotInfo = Spawner.pickRandomBrainrotOfRarity(rarity)
	local mutation = BrainrotData.rollMutation()
	
	local model = Instance.new("Model")
	model.Name = brainrotInfo.name
	
	local body = Instance.new("Part")
	body.Name = "Body"
	body.Size = Vector3.new(4, 4, 4)
	body.Position = Vector3.new(0, 3, -130)
	body.Anchored = true
	body.Color = brainrotInfo.color
	body.Parent = model
	model.PrimaryPart = body
	
	local mutationMultiplier = 1
	if mutation == "Golden" then
		mutationMultiplier = 2
	elseif mutation == "Diamond" then
		mutationMultiplier = 4
	elseif mutation == "Rainbow" then
		mutationMultiplier = 6
	elseif mutation == "Void" then
		mutationMultiplier = 10
	end
	
	local finalRate = math.floor(brainrotInfo.rate * mutationMultiplier)
	
	local rateVal = Instance.new("NumberValue")
	rateVal.Name = "EarningsRate"
	rateVal.Value = finalRate
	rateVal.Parent = model
	
	local mutationVal = Instance.new("StringValue")
	mutationVal.Name = "Mutation"
	mutationVal.Value = mutation
	mutationVal.Parent = model
	
	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.new(0, 160, 0, 50)
	billboard.StudsOffset = Vector3.new(0, 3, 0)
	billboard.AlwaysOnTop = true
	
	local textLabel = Instance.new("TextLabel")
	textLabel.Size = UDim2.new(1, 0, 1, 0)
	textLabel.BackgroundTransparency = 1
	textLabel.TextColor3 = Color3.new(1, 1, 1)
	textLabel.TextStrokeTransparency = 0
	textLabel.TextSize = 14
	textLabel.Font = Enum.Font.FredokaOne
	
	local prefix = ""
	if mutation ~= "None" then
		prefix = "[" .. mutation .. "] "
	end
	textLabel.Text = prefix .. brainrotInfo.name .. "\n" .. rarity .. " | $" .. finalRate .. "/s"
	textLabel.Parent = billboard
	billboard.Parent = body
	
	model.Parent = conveyorFolder
	return model
end

function Spawner.moveAlongConveyor(model: Model, dt: number, speed: number): boolean
	local body = model.PrimaryPart or model:FindFirstChild("Body")
	if not body or not body:IsA("BasePart") then
		model:Destroy()
		return true
	end
	
	local currentPos = body.Position
	local newZ = currentPos.Z + (speed * dt)
	body.Position = Vector3.new(currentPos.X, currentPos.Y, newZ)
	
	if newZ >= -10 then
		model:Destroy()
		return true
	end
	
	return false
end

return Spawner
