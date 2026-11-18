--!strict

local Workspace = game:GetService("Workspace")

local RidesModule = {}

function RidesModule.init()
	local ridesFolder = Workspace:FindFirstChild("Rides")
	if not ridesFolder then
		return
	end

	local ferrisWheel = ridesFolder:FindFirstChild("FerrisWheel")
	local carousel = ridesFolder:FindFirstChild("Carousel")
	local swing1 = ridesFolder:FindFirstChild("Swing1")
	local swing2 = ridesFolder:FindFirstChild("Swing2")
	local coasterCar1 = ridesFolder:FindFirstChild("CoasterCar1")
	local coasterCar2 = ridesFolder:FindFirstChild("CoasterCar2")

	-- Precompute 16 pad positions for coaster
	local waypoints = {}
	for i = 0, 15 do
		local angle = i * 22.5 * (math.pi / 180)
		local x = tonumber(string.format("%.1f", -110 + 25 * math.cos(angle))) or 0
		local z = tonumber(string.format("%.1f", -30 + 40 * math.sin(angle))) or 0
		local y = tonumber(string.format("%.1f", 5 + 3 * math.sin(2 * angle))) or 5
		waypoints[i + 1] = Vector3.new(x, y, z)
	end

	local wheelAngle = 0
	local progress1 = 0
	local progress2 = 0.5

	task.spawn(function()
		while true do
			task.wait(0.1)
			local now = os.clock()

			-- Ferris Wheel
			if ferrisWheel then
				pcall(function()
					local hub = ferrisWheel:FindFirstChild("Hub")
					if hub and hub:IsA("BasePart") then
						wheelAngle += 0.0157
						local axlePos = hub.Position
						for i = 1, 8 do
							local cabin = ridesFolder:FindFirstChild("Cabin" .. i)
							if cabin and cabin:IsA("Model") then
								local primary = cabin.PrimaryPart or cabin:FindFirstChild("HumanoidRootPart") or cabin:FindFirstChildWhichIsA("BasePart")
								if primary then
									local angle = wheelAngle + (i - 1) * (math.pi / 4)
									local targetPos = axlePos + Vector3.new(15 * math.cos(angle), 15 * math.sin(angle), 0)
									cabin:PivotTo(CFrame.new(targetPos) * CFrame.Angles(0, 0, 0))
								end
							end
						end
					end
				end)
			end

			-- Carousel
			if carousel then
				pcall(function()
					local platform = carousel:FindFirstChild("Platform")
					if platform and platform:IsA("BasePart") then
						local carouselAngle = wheelAngle * 3
						carousel:PivotTo(CFrame.new(platform.Position) * CFrame.Angles(0, carouselAngle, 0))
					end
				end)
			end

			-- Swings
			for index, swingModel in ipairs({swing1, swing2}) do
				if swingModel then
					pcall(function()
						local pivot = swingModel:FindFirstChild("Pivot")
						if pivot and pivot:IsA("BasePart") then
							local rotX = math.sin(now * 1.5 + index) * 0.3
							swingModel:PivotTo(pivot.CFrame * CFrame.Angles(rotX, 0, 0))
						end
					end)
				end
			end

			-- Coaster Cars
			for i, carModel in ipairs({coasterCar1, coasterCar2}) do
				if carModel then
					pcall(function()
						if i == 1 then
							progress1 = (progress1 + 0.002) % 1
						else
							progress2 = (progress2 + 0.002) % 1
						end
						local p = (i == 1) and progress1 or progress2

						local floatIndex = p * 16
						local idx1 = math.floor(floatIndex) % 16
						local idx2 = (idx1 + 1) % 16
						local alpha = floatIndex - math.floor(floatIndex)

						local pos1 = waypoints[idx1 + 1]
						local pos2 = waypoints[idx2 + 1]
						local pos = pos1:Lerp(pos2, alpha)
						local nextPos = waypoints[(idx2 + 1) % 16 + 1]
						local dir = (nextPos - pos1).Unit

						if dir.Magnitude > 0 then
							local lookAtCFrame = CFrame.lookAt(pos, pos + dir)
							carModel:PivotTo(lookAtCFrame)
						else
							carModel:PivotTo(CFrame.new(pos))
						end
					end)
				end
			end
		end
	end)
end

return RidesModule
