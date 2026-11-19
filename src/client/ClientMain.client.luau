--!strict

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ContextActionService = game:GetService("ContextActionService")
local MarketplaceService = game:GetService("MarketplaceService")
local Workspace = game:GetService("Workspace")
local TweenService = game:GetService("TweenService")

local BrainrotData = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("BrainrotData"))
local GameConfig = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("GameConfig"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui") :: PlayerGui

-- On mobile, pinch-zoom can fly hundreds of studs out and the whole map looks like empty green
player.CameraMaxZoomDistance = 70
player.CameraMinZoomDistance = 8

local remotes = ReplicatedStorage:WaitForChild("Remotes")
local catchEvent = remotes:WaitForChild("CatchBrainrot") :: RemoteEvent
local buyLockEvent = remotes:WaitForChild("BuyLock") :: RemoteEvent
local rebirthEvent = remotes:WaitForChild("Rebirth") :: RemoteEvent
local buyUpgradeEvent = remotes:WaitForChild("BuyUpgrade") :: RemoteEvent
local waveWarningEvent = remotes:WaitForChild("WaveWarning") :: RemoteEvent
local teleportToPlazaEvent = remotes:WaitForChild("TeleportToPlaza") :: RemoteEvent

-- GUI Setup
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "BrainrotBayGui"
screenGui.ResetOnSpawn = false
screenGui.IgnoreGuiInset = false
screenGui.Parent = playerGui

-- Cash Panel (Top-Right)
local cashPanel = Instance.new("Frame")
cashPanel.Name = "CashPanel"
cashPanel.Size = UDim2.new(0, 240, 0, 70)
cashPanel.Position = UDim2.new(1, -260, 0, 20)
cashPanel.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
cashPanel.BorderSizePixel = 0
cashPanel.Parent = screenGui

local cashCorner = Instance.new("UICorner")
cashCorner.CornerRadius = UDim.new(0, 8)
cashCorner.Parent = cashPanel

local cashLabel = Instance.new("TextLabel")
cashLabel.Name = "CashLabel"
cashLabel.Size = UDim2.new(1, 0, 0.5, 0)
cashLabel.Position = UDim2.new(0, 0, 0, 5)
cashLabel.BackgroundTransparency = 1
cashLabel.Font = Enum.Font.FredokaOne
cashLabel.Text = "CASH: $100"
cashLabel.TextColor3 = Color3.fromRGB(80, 255, 120)
cashLabel.TextSize = 24
cashLabel.Parent = cashPanel

local rateLabel = Instance.new("TextLabel")
rateLabel.Name = "RateLabel"
rateLabel.Size = UDim2.new(1, 0, 0.5, 0)
rateLabel.Position = UDim2.new(0, 0, 0.5, -5)
rateLabel.BackgroundTransparency = 1
rateLabel.Font = Enum.Font.FredokaOne
rateLabel.Text = "$0/s"
rateLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
rateLabel.TextSize = 18
rateLabel.Parent = cashPanel

	-- Version label sitting under the cash panel so we always know which build is live
	local versionLabel = Instance.new("TextLabel")
	versionLabel.Name = "VersionLabel"
	versionLabel.Size = UDim2.new(0, 240, 0, 20)
	versionLabel.Position = UDim2.new(1, -260, 0, 92)
	versionLabel.BackgroundTransparency = 1
	versionLabel.Font = Enum.Font.FredokaOne
	versionLabel.Text = "v25"
	versionLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	versionLabel.TextSize = 14
	versionLabel.TextXAlignment = Enum.TextXAlignment.Right
	versionLabel.Parent = screenGui

-- Title (Top-Center)
local titleFrame = Instance.new("Frame")
titleFrame.Name = "TitleFrame"
titleFrame.Size = UDim2.new(0, 450, 0, 60)
titleFrame.Position = UDim2.new(0.5, -225, 0, 15)
titleFrame.BackgroundTransparency = 1
titleFrame.Parent = screenGui

local titleLabel = Instance.new("TextLabel")
titleLabel.Name = "TitleLabel"
titleLabel.Size = UDim2.new(1, 0, 0.6, 0)
titleLabel.BackgroundTransparency = 1
titleLabel.Font = Enum.Font.FredokaOne
titleLabel.Text = "BRAINROT BAY"
titleLabel.TextColor3 = Color3.fromRGB(255, 100, 150)
titleLabel.TextSize = 32
titleLabel.Parent = titleFrame

local subtitleLabel = Instance.new("TextLabel")
subtitleLabel.Name = "SubtitleLabel"
subtitleLabel.Size = UDim2.new(1, 0, 0.4, 0)
subtitleLabel.Position = UDim2.new(0, 0, 0.6, 0)
subtitleLabel.BackgroundTransparency = 1
subtitleLabel.Font = Enum.Font.GothamBold
subtitleLabel.Text = "Catch brainrots - Fill your base - Outrun the wave!"
subtitleLabel.TextColor3 = Color3.fromRGB(220, 220, 220)
subtitleLabel.TextSize = 13
subtitleLabel.Parent = titleFrame

-- Center Wave Warning Label
local waveWarningLabel = Instance.new("TextLabel")
waveWarningLabel.Name = "WaveWarningLabel"
waveWarningLabel.Size = UDim2.new(0, 600, 0, 100)
waveWarningLabel.Position = UDim2.new(0.5, -300, 0.4, -50)
waveWarningLabel.BackgroundTransparency = 0.2
waveWarningLabel.BackgroundColor3 = Color3.fromRGB(180, 30, 30)
waveWarningLabel.BorderSizePixel = 0
waveWarningLabel.Visible = false
waveWarningLabel.Font = Enum.Font.FredokaOne
waveWarningLabel.Text = "TSUNAMI WAVE INCOMING - DASH HOME!"
waveWarningLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
waveWarningLabel.TextSize = 26
waveWarningLabel.Parent = screenGui

local waveCorner = Instance.new("UICorner")
waveCorner.CornerRadius = UDim.new(0, 12)
waveCorner.Parent = waveWarningLabel

-- Bottom-Center Button Row
local buttonRow = Instance.new("Frame")
buttonRow.Name = "ButtonRow"
buttonRow.Size = UDim2.new(0, 520, 0, 50)
buttonRow.Position = UDim2.new(0.5, -260, 1, -70)
buttonRow.BackgroundTransparency = 1
buttonRow.Parent = screenGui

local uiListLayout = Instance.new("UIListLayout")
uiListLayout.FillDirection = Enum.FillDirection.Horizontal
uiListLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
uiListLayout.VerticalAlignment = Enum.VerticalAlignment.Center
uiListLayout.SortOrder = Enum.SortOrder.LayoutOrder
uiListLayout.Padding = UDim.new(0, 15)
uiListLayout.Parent = buttonRow

local lockButton = Instance.new("TextButton")
lockButton.Name = "LockButton"
lockButton.LayoutOrder = 1
lockButton.Size = UDim2.new(0, 160, 0, 45)
lockButton.BackgroundColor3 = Color3.fromRGB(50, 120, 220)
lockButton.BorderSizePixel = 0
lockButton.Font = Enum.Font.FredokaOne
lockButton.Text = "LOCK BASE ($500)"
lockButton.TextColor3 = Color3.fromRGB(255, 255, 255)
lockButton.TextSize = 15
lockButton.Parent = buttonRow

local lockCorner = Instance.new("UICorner")
lockCorner.CornerRadius = UDim.new(0, 8)
lockCorner.Parent = lockButton

local rebirthButton = Instance.new("TextButton")
rebirthButton.Name = "RebirthButton"
rebirthButton.LayoutOrder = 2
rebirthButton.Size = UDim2.new(0, 160, 0, 45)
rebirthButton.BackgroundColor3 = Color3.fromRGB(220, 140, 40)
rebirthButton.BorderSizePixel = 0
rebirthButton.Font = Enum.Font.FredokaOne
rebirthButton.Text = "REBIRTH (x2)"
rebirthButton.TextColor3 = Color3.fromRGB(255, 255, 255)
rebirthButton.TextSize = 15
rebirthButton.Parent = buttonRow

local rebirthCorner = Instance.new("UICorner")
rebirthCorner.CornerRadius = UDim.new(0, 8)
rebirthCorner.Parent = rebirthButton

local upgradeButton = Instance.new("TextButton")
upgradeButton.Name = "UpgradeButton"
upgradeButton.LayoutOrder = 3
upgradeButton.Size = UDim2.new(0, 160, 0, 45)
upgradeButton.BackgroundColor3 = Color3.fromRGB(120, 50, 220)
upgradeButton.BorderSizePixel = 0
upgradeButton.Font = Enum.Font.FredokaOne
upgradeButton.Text = "UPGRADES"
upgradeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
upgradeButton.TextSize = 15
upgradeButton.Parent = buttonRow

local upgradeCorner = Instance.new("UICorner")
upgradeCorner.CornerRadius = UDim.new(0, 8)
upgradeCorner.Parent = upgradeButton

-- Shop Button (below the Roblox mobile top bar) + Shop Panel (game passes)
local shopButton = Instance.new("TextButton")
shopButton.Name = "ShopButton"
shopButton.Size = UDim2.new(0, 120, 0, 45)
shopButton.Position = UDim2.new(0, 20, 0, 80)
shopButton.BackgroundColor3 = Color3.fromRGB(220, 180, 40)
shopButton.BorderSizePixel = 0
shopButton.Font = Enum.Font.FredokaOne
shopButton.Text = "SHOP"
shopButton.TextColor3 = Color3.fromRGB(255, 255, 255)
shopButton.TextSize = 18
shopButton.Parent = screenGui

local shopCorner = Instance.new("UICorner")
shopCorner.CornerRadius = UDim.new(0, 8)
shopCorner.Parent = shopButton

local shopFrame = Instance.new("Frame")
shopFrame.Name = "ShopFrame"
shopFrame.Size = UDim2.new(0, 420, 0, 560)
shopFrame.Position = UDim2.new(0.5, -210, 0.5, -150)
shopFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 35)
shopFrame.BorderSizePixel = 0
shopFrame.Visible = false
shopFrame.Parent = screenGui

local shopFrameCorner = Instance.new("UICorner")
shopFrameCorner.CornerRadius = UDim.new(0, 10)
shopFrameCorner.Parent = shopFrame

local shopTitle = Instance.new("TextLabel")
shopTitle.Name = "ShopTitle"
shopTitle.Size = UDim2.new(1, 0, 0, 40)
shopTitle.BackgroundTransparency = 1
shopTitle.Font = Enum.Font.FredokaOne
shopTitle.Text = "TOKO"
shopTitle.TextColor3 = Color3.fromRGB(255, 220, 100)
shopTitle.TextSize = 20
shopTitle.Parent = shopFrame

local shopClose = Instance.new("TextButton")
shopClose.Name = "ShopClose"
shopClose.Size = UDim2.new(0, 30, 0, 30)
shopClose.Position = UDim2.new(1, -38, 0, 5)
shopClose.BackgroundColor3 = Color3.fromRGB(180, 40, 40)
shopClose.BorderSizePixel = 0
shopClose.Font = Enum.Font.FredokaOne
shopClose.Text = "X"
shopClose.TextColor3 = Color3.fromRGB(255, 255, 255)
shopClose.TextSize = 16
shopClose.Parent = shopFrame

local shopCloseCorner = Instance.new("UICorner")
shopCloseCorner.CornerRadius = UDim.new(0, 6)
shopCloseCorner.Parent = shopClose

local shopList = Instance.new("Frame")
shopList.Name = "ShopList"
shopList.Size = UDim2.new(1, -16, 1, -50)
shopList.Position = UDim2.new(0, 8, 0, 45)
shopList.BackgroundTransparency = 1
shopList.BorderSizePixel = 0
shopList.Parent = shopFrame

local shopLayout = Instance.new("UIListLayout")
shopLayout.FillDirection = Enum.FillDirection.Vertical
shopLayout.SortOrder = Enum.SortOrder.LayoutOrder
shopLayout.Padding = UDim.new(0, 10)
shopLayout.Parent = shopList

-- Toggle button for guide panel
local guideToggle = Instance.new("TextButton")
guideToggle.Name = "GuideToggle"
guideToggle.Size = UDim2.new(0, 110, 0, 40)
guideToggle.Position = UDim2.new(0, 20, 1, -100)
guideToggle.BackgroundColor3 = Color3.fromRGB(60, 60, 80)
guideToggle.BorderSizePixel = 0
guideToggle.FontFace = Font.fromName("FredokaOne")
guideToggle.Text = "GUIDE"
guideToggle.TextColor3 = Color3.fromRGB(255, 255, 255)
guideToggle.TextSize = 15
guideToggle.Parent = screenGui

local guideToggleCorner = Instance.new("UICorner")
guideToggleCorner.CornerRadius = UDim.new(0, 8)
guideToggleCorner.Parent = guideToggle

-- One tap teleports player back to spawn/plaza so nobody ever gets lost on empty green baseplate again
-- Button sits top-centre under title so it is never covered by the GUIDE panel
local plazaButton = Instance.new("TextButton")
plazaButton.Name = "PlazaButton"
plazaButton.Size = UDim2.new(0, 110, 0, 40)
plazaButton.Position = UDim2.new(0.5, -55, 0, 80)
plazaButton.BackgroundColor3 = Color3.fromRGB(220, 60, 120)
plazaButton.BorderSizePixel = 0
plazaButton.FontFace = Font.fromName("FredokaOne")
plazaButton.Text = "PLAZA"
plazaButton.TextColor3 = Color3.fromRGB(255, 255, 255)
plazaButton.TextSize = 15
plazaButton.Parent = screenGui

local plazaCorner = Instance.new("UICorner")
plazaCorner.CornerRadius = UDim.new(0, 8)
plazaCorner.Parent = plazaButton

plazaButton.MouseButton1Click:Connect(function()
	local char = player.Character
	if char then
		local hrp = char:FindFirstChild("HumanoidRootPart")
		if hrp then
			hrp.CFrame = CFrame.new(0, 5, 35)
		end
	end
	pcall(function()
		teleportToPlazaEvent:FireServer()
	end)
end)

-- Bottom-Left Info Panel (Brainrot Guide)
local guidePanel = Instance.new("Frame")
guidePanel.Name = "GuidePanel"
guidePanel.Size = UDim2.new(0, 280, 0, 420)
guidePanel.Position = UDim2.new(0, 20, 1, -450)
guidePanel.BackgroundColor3 = Color3.fromRGB(25, 25, 35)
guidePanel.BackgroundTransparency = 0.1
guidePanel.BorderSizePixel = 0
guidePanel.Visible = false
guidePanel.Parent = screenGui

guideToggle.MouseButton1Click:Connect(function()
	guidePanel.Visible = not guidePanel.Visible
end)

local guideCorner = Instance.new("UICorner")
guideCorner.CornerRadius = UDim.new(0, 10)
guideCorner.Parent = guidePanel

local guideTitle = Instance.new("TextLabel")
guideTitle.Name = "GuideTitle"
guideTitle.Size = UDim2.new(1, 0, 0, 40)
guideTitle.BackgroundTransparency = 1
guideTitle.Font = Enum.Font.FredokaOne
guideTitle.Text = "BRAINROT GUIDE"
guideTitle.TextColor3 = Color3.fromRGB(255, 220, 100)
guideTitle.TextSize = 18
guideTitle.Parent = guidePanel

local scrollContainer = Instance.new("ScrollingFrame")
scrollContainer.Name = "ScrollContainer"
scrollContainer.Size = UDim2.new(1, -16, 1, -50)
scrollContainer.Position = UDim2.new(0, 8, 0, 45)
scrollContainer.BackgroundTransparency = 1
scrollContainer.BorderSizePixel = 0
scrollContainer.CanvasSize = UDim2.new(0, 0, 0, 12 * 35)
scrollContainer.ScrollBarThickness = 6
scrollContainer.Parent = guidePanel

local scrollLayout = Instance.new("UIListLayout")
scrollLayout.FillDirection = Enum.FillDirection.Vertical
scrollLayout.SortOrder = Enum.SortOrder.LayoutOrder
scrollLayout.Padding = UDim.new(0, 6)
scrollLayout.Parent = scrollContainer

-- State variables
local currentCash = GameConfig.START_CASH
local currentRate = 5 -- initial base rate from start
local upgradeTypes = { "WalkSpeed", "Magnet", "ExtraSlot" }
local currentUpgradeIndex = 1

-- Functions required by instructions
local function updateCashDisplay(newCash: number, newRate: number?)
	currentCash = newCash
	if newRate then
		currentRate = newRate
	end
	cashLabel.Text = string.format("CASH: $%d", math.floor(currentCash))
	rateLabel.Text = string.format("$%d/s", currentRate)
end

local function showWaveWarning()
	waveWarningLabel.Visible = true
	task.delay(5, function()
		waveWarningLabel.Visible = false
	end)
end

local function bindCatchKey()
	local function catchAction(actionName: string, inputState: Enum.UserInputState, inputObject: InputObject)
		if inputState == Enum.UserInputState.Begin then
			local character = player.Character
			if character and character:FindFirstChild("HumanoidRootPart") then
				local rootPart = character.HumanoidRootPart :: Part
				local conveyorFolder = Workspace:FindFirstChild("Conveyor")
				if conveyorFolder then
					local nearestModel: Model? = nil
					local shortestDist = 12
					
					for _, item in ipairs(conveyorFolder:GetChildren()) do
						if item:IsA("Model") and item.PrimaryPart then
							local dist = (item.PrimaryPart.Position - rootPart.Position).Magnitude
							if dist <= shortestDist then
								shortestDist = dist
								nearestModel = item
							end
						end
					end
					
					if nearestModel then
						catchEvent:FireServer(nearestModel)
					end
				end
			end
		end
		return Enum.ContextActionResult.Sink
	end
	
	ContextActionService:BindAction("CatchBrainrotAction", catchAction, false, Enum.KeyCode.E)
end

local function setupButtons()
	lockButton.MouseButton1Click:Connect(function()
		buyLockEvent:FireServer()
	end)
	
	rebirthButton.MouseButton1Click:Connect(function()
		rebirthEvent:FireServer()
	end)
	
	upgradeButton.MouseButton1Click:Connect(function()
		local chosenUpgrade = upgradeTypes[currentUpgradeIndex]
		buyUpgradeEvent:FireServer(chosenUpgrade)
		
		-- Cycle to next upgrade type for subsequent clicks
		currentUpgradeIndex = currentUpgradeIndex + 1
		if currentUpgradeIndex > #upgradeTypes then
			currentUpgradeIndex = 1
		end
		upgradeButton.Text = "UPGRADE: " .. upgradeTypes[currentUpgradeIndex]
	end)
end

local function buildGuidePanel()
	for i, data in ipairs(BrainrotData.BRAINROTS) do
		local row = Instance.new("Frame")
		row.Name = data.name
		row.Size = UDim2.new(1, 0, 0, 30)
		row.BackgroundTransparency = 0.8
		row.BackgroundColor3 = data.color
		row.BorderSizePixel = 0
		row.LayoutOrder = i
		row.Parent = scrollContainer
		
		local rCorner = Instance.new("UICorner")
		rCorner.CornerRadius = UDim.new(0, 4)
		rCorner.Parent = row
		
		local nameLabel = Instance.new("TextLabel")
		nameLabel.Size = UDim2.new(0.65, 0, 1, 0)
		nameLabel.Position = UDim2.new(0, 8, 0, 0)
		nameLabel.BackgroundTransparency = 1
		nameLabel.Font = Enum.Font.GothamBold
		nameLabel.Text = data.name
		nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
		nameLabel.TextSize = 12
		nameLabel.TextXAlignment = Enum.TextXAlignment.Left
		nameLabel.Parent = row
		
		local statsLabel = Instance.new("TextLabel")
		statsLabel.Size = UDim2.new(0.35, -8, 1, 0)
		statsLabel.Position = UDim2.new(0.65, 0, 0, 0)
		statsLabel.BackgroundTransparency = 1
		statsLabel.Font = Enum.Font.Gotham
		statsLabel.Text = string.format("$%d/s", data.rate)
		statsLabel.TextColor3 = Color3.fromRGB(150, 255, 150)
		statsLabel.TextSize = 12
		statsLabel.TextXAlignment = Enum.TextXAlignment.Right
		statsLabel.Parent = row
	end
end

local function setupShop()
	shopButton.MouseButton1Click:Connect(function()
		shopFrame.Visible = not shopFrame.Visible
	end)
	shopClose.MouseButton1Click:Connect(function()
		shopFrame.Visible = false
	end)

	for i, pass in ipairs(GameConfig.PASS_SHOP) do
		local passId = GameConfig.PASS_IDS[pass.key] or 0
		local row = Instance.new("Frame")
		row.Name = pass.key
		row.Size = UDim2.new(1, 0, 0, 64)
		row.BackgroundColor3 = Color3.fromRGB(40, 40, 55)
		row.BorderSizePixel = 0
		row.LayoutOrder = i
		row.Parent = shopList

		local rowCorner = Instance.new("UICorner")
		rowCorner.CornerRadius = UDim.new(0, 8)
		rowCorner.Parent = row

		local nameLabel = Instance.new("TextLabel")
		nameLabel.Size = UDim2.new(0.6, -8, 0, 28)
		nameLabel.Position = UDim2.new(0, 10, 0, 4)
		nameLabel.BackgroundTransparency = 1
		nameLabel.Font = Enum.Font.FredokaOne
		nameLabel.Text = pass.name
		nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
		nameLabel.TextSize = 16
		nameLabel.TextXAlignment = Enum.TextXAlignment.Left
		nameLabel.Parent = row

		local descLabel = Instance.new("TextLabel")
		descLabel.Size = UDim2.new(0.6, -8, 0, 28)
		descLabel.Position = UDim2.new(0, 10, 0, 32)
		descLabel.BackgroundTransparency = 1
		descLabel.Font = Enum.Font.Gotham
		descLabel.Text = pass.desc
		descLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
		descLabel.TextSize = 12
		descLabel.TextXAlignment = Enum.TextXAlignment.Left
		descLabel.Parent = row

		local buyButton = Instance.new("TextButton")
		buyButton.Name = "BuyButton"
		buyButton.Size = UDim2.new(0, 130, 0, 44)
		buyButton.Position = UDim2.new(1, -140, 0, 10)
		buyButton.BackgroundColor3 = Color3.fromRGB(80, 200, 80)
		buyButton.BorderSizePixel = 0
		buyButton.Font = Enum.Font.FredokaOne
		buyButton.Text = "BELI  R$" .. tostring(pass.price)
		buyButton.TextColor3 = Color3.fromRGB(255, 255, 255)
		buyButton.TextSize = 15
		buyButton.Parent = row

		local buyCorner = Instance.new("UICorner")
		buyCorner.CornerRadius = UDim.new(0, 8)
		buyCorner.Parent = buyButton

		if passId == 0 then
			buyButton.Text = "SEGERA"
			buyButton.BackgroundColor3 = Color3.fromRGB(120, 120, 120)
		else
			buyButton.MouseButton1Click:Connect(function()
				pcall(function()
					MarketplaceService:PromptGamePassPurchase(player, passId)
				end)
			end)
		end
	end

	local sectionLabel = Instance.new("TextLabel")
	sectionLabel.Name = "SectionLabel"
	sectionLabel.Size = UDim2.new(1, 0, 0, 30)
	sectionLabel.BackgroundTransparency = 1
	sectionLabel.Font = Enum.Font.FredokaOne
	sectionLabel.Text = "BELI BERKALI-KALI"
	sectionLabel.TextColor3 = Color3.fromRGB(255, 200, 100)
	sectionLabel.TextSize = 14
	sectionLabel.TextXAlignment = Enum.TextXAlignment.Left
	sectionLabel.LayoutOrder = 100
	sectionLabel.Parent = shopList

	for i, prod in ipairs(GameConfig.PRODUCT_SHOP) do
		local prodId = GameConfig.PRODUCT_IDS[prod.key] or 0
		local row = Instance.new("Frame")
		row.Name = prod.key
		row.Size = UDim2.new(1, 0, 0, 64)
		row.BackgroundColor3 = Color3.fromRGB(40, 40, 55)
		row.BorderSizePixel = 0
		row.LayoutOrder = 100 + i
		row.Parent = shopList

		local rowCorner = Instance.new("UICorner")
		rowCorner.CornerRadius = UDim.new(0, 8)
		rowCorner.Parent = row

		local nameLabel = Instance.new("TextLabel")
		nameLabel.Size = UDim2.new(0.6, -8, 0, 28)
		nameLabel.Position = UDim2.new(0, 10, 0, 4)
		nameLabel.BackgroundTransparency = 1
		nameLabel.Font = Enum.Font.FredokaOne
		nameLabel.Text = prod.name
		nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
		nameLabel.TextSize = 16
		nameLabel.TextXAlignment = Enum.TextXAlignment.Left
		nameLabel.Parent = row

		local descLabel = Instance.new("TextLabel")
		descLabel.Size = UDim2.new(0.6, -8, 0, 28)
		descLabel.Position = UDim2.new(0, 10, 0, 32)
		descLabel.BackgroundTransparency = 1
		descLabel.Font = Enum.Font.Gotham
		descLabel.Text = prod.desc
		descLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
		descLabel.TextSize = 12
		descLabel.TextXAlignment = Enum.TextXAlignment.Left
		descLabel.Parent = row

		local buyButton = Instance.new("TextButton")
		buyButton.Name = "BuyButton"
		buyButton.Size = UDim2.new(0, 130, 0, 44)
		buyButton.Position = UDim2.new(1, -140, 0, 10)
		buyButton.BackgroundColor3 = Color3.fromRGB(80, 200, 80)
		buyButton.BorderSizePixel = 0
		buyButton.Font = Enum.Font.FredokaOne
		buyButton.Text = "BELI  R$" .. tostring(prod.price)
		buyButton.TextColor3 = Color3.fromRGB(255, 255, 255)
		buyButton.TextSize = 15
		buyButton.Parent = row

		local buyCorner = Instance.new("UICorner")
		buyCorner.CornerRadius = UDim.new(0, 8)
		buyCorner.Parent = buyButton

		if prodId == 0 then
			buyButton.Text = "SEGERA"
			buyButton.BackgroundColor3 = Color3.fromRGB(120, 120, 120)
		else
			buyButton.MouseButton1Click:Connect(function()
				pcall(function()
					MarketplaceService:PromptProductPurchase(player, prodId)
				end)
			end)
		end
	end
end

-- Initialize UI components
buildGuidePanel()
setupButtons()
setupShop()
bindCatchKey()

-- Listen for Wave Warning Remote
waveWarningEvent.OnClientEvent:Connect(function()
	showWaveWarning()
end)

-- Cash accumulation loop (once per second)
task.spawn(function()
	while true do
		task.wait(1)
		currentCash += currentRate
		updateCashDisplay(currentCash)
	end
end)

print("ClientMain initialized successfully.")
